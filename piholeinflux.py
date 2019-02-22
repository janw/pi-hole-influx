#! /usr/bin/python

from __future__ import print_function
import requests
from time import sleep, localtime, strftime
from influxdb import InfluxDBClient
from configparser import ConfigParser
from os import path
import traceback
import sdnotify
import sys

HERE = path.dirname(path.realpath(__file__))
config = ConfigParser()
config.read(path.join(HERE, "config.ini"))

INFLUXDB_SERVER = config["influxdb"].get("hostname", "127.0.0.1")
INFLUXDB_PORT = config["influxdb"].getint("port", 8086)
INFLUXDB_USERNAME = config["influxdb"]["username"]
INFLUXDB_PASSWORD = config["influxdb"]["password"]
INFLUXDB_DATABASE = config["influxdb"]["database"]
REPORTING_INTERVAL = config["influxdb"].getint("reporting_interval", 10)

INFLUXDB_CLIENT = InfluxDBClient(
    INFLUXDB_SERVER,
    INFLUXDB_PORT,
    INFLUXDB_USERNAME,
    INFLUXDB_PASSWORD,
    INFLUXDB_DATABASE,
)

n = sdnotify.SystemdNotifier()
n.notify("READY=1")


class Pihole:
    """Container object for a single Pi-hole instance."""

    def __init__(self, config):
        self.name = config.name
        self.url = config["api_location"]
        self.timeout = config.getint("timeout", 10)
        if "instance_name" in config:
            self.name = config["instance_name"]

    def get_data(self):
        """Retrieve API data from Pi-hole, and return as dict on success."""
        response = requests.get(self.url, timeout=self.timeout)
        if response.status_code == 200:
            return response.json()


def send_msg(resp, name):
    """Write the Pi-hole response data to the InfluxDB."""
    if "gravity_last_updated" in resp:
        del resp["gravity_last_updated"]

    json_body = [{"measurement": "pihole", "tags": {"host": name}, "fields": resp}]

    INFLUXDB_CLIENT.write_points(json_body)


if __name__ == "__main__":
    piholes = [Pihole(config[s]) for s in config.sections() if s != "influxdb"]
    while True:
        try:
            for pi in piholes:
                data = pi.get_data()
                send_msg(data, pi.name)
            timestamp = strftime("%Y-%m-%d %H:%M:%S %z", localtime())
            n.notify("STATUS=Reported to InfluxDB at {}".format(timestamp))

        except Exception as e:
            msg = "Failed, to report to InfluxDB:"
            n.notify("STATUS={} {}".format(msg, str(e)))
            print(msg, str(e))
            print(traceback.format_exc())
            sys.exit(1)

        sleep(REPORTING_INTERVAL)
