#! /usr/bin/python

from __future__ import print_function
import requests
from time import sleep, localtime, strftime
from influxdb import InfluxDBClient
from configparser import ConfigParser
from os import path
from urllib.parse import urlparse
import traceback
import sdnotify
import sys

HERE = path.dirname(path.realpath(__file__))

n = sdnotify.SystemdNotifier()
n.notify("READY=1")


class Pihole:
    """Container object for a single Pi-hole instance."""

    def __init__(self, config):
        self.url = config["api_location"]
        self.timeout = int(config.get("timeout", 10))
        if "instance_name" in config:
            self.name = config["instance_name"]
        elif hasattr(config, "name"):
            self.name = config.name
        else:
            self.name = urlparse(self.url).netloc

    def get_data(self):
        """Retrieve API data from Pi-hole, and return as dict on success."""
        response = requests.get(self.url, timeout=self.timeout)
        if response.status_code == 200:
            return response.json()


def send_msg(influxdb, resp, name):
    """Write the Pi-hole response data to the InfluxDB."""
    if "gravity_last_updated" in resp:
        del resp["gravity_last_updated"]

    json_body = [{"measurement": "pihole", "tags": {"host": name}, "fields": resp}]

    influxdb.write_points(json_body)


def main(single_run=False):
    """Main application daemon."""
    config = ConfigParser()
    config.read_file(open(path.join(HERE, "config.ini")))

    influxdb_server = config["influxdb"].get("hostname", "127.0.0.1")
    influxdb_port = config["influxdb"].getint("port", 8086)
    influxdb_username = config["influxdb"]["username"]
    influxdb_password = config["influxdb"]["password"]
    influxdb_database = config["influxdb"]["database"]
    reporting_interval = config["influxdb"].getint("reporting_interval", 10)

    influxdb_client = InfluxDBClient(
        influxdb_server,
        influxdb_port,
        influxdb_username,
        influxdb_password,
        influxdb_database,
    )
    piholes = [
        Pihole(config[section])
        for section in config.sections()
        if section not in ("influxdb", "defaults")
    ]

    while True:
        try:
            for pi in piholes:
                data = pi.get_data()
                send_msg(influxdb_client, data, pi.name)
            timestamp = strftime("%Y-%m-%d %H:%M:%S %z", localtime())
            n.notify("STATUS=Reported to InfluxDB at {}".format(timestamp))

        except Exception as e:
            msg = "Failed, to report to InfluxDB:"
            n.notify("STATUS={} {}".format(msg, str(e)))
            print(msg, str(e))
            print(traceback.format_exc())
            sys.exit(1)

        if single_run:
            break
        else:
            sleep(reporting_interval)  # pragma: no cover


if __name__ == "__main__":
    main()
