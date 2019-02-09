#! /usr/bin/python

from __future__ import print_function
import requests
from time import sleep, localtime, strftime
from influxdb import InfluxDBClient
from configparser import ConfigParser
from os import path
from urllib.parse import urlparse
from shutil import copyfile
import traceback
import sdnotify
import sys

HERE = path.dirname(path.realpath(__file__))
CONFIG_FILE = path.join(HERE, 'config.ini')


n = sdnotify.SystemdNotifier()


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


class Daemon(object):
    def __init__(self, config):
        self.influx = InfluxDBClient(
            host=config['influxdb'].get('hostname', '127.0.0.1'),
            port=config['influxdb'].getint('port', 8086),
            username=config['influxdb']['username'],
            password=config['influxdb']['password'],
            database=config['influxdb']['database']
        )

        self.piholes = [
            Pihole(config[s]) for s in config.sections()
            if s != "influxdb"
        ]

        self.interval = config['influxdb'].getint('reporting_interval', 10)

    def run(self):
        while True:
            for pi in self.piholes:
                data = pi.get_data()
                self.send_msg(data, pi.name)
            timestamp = strftime('%Y-%m-%d %H:%M:%S %z', localtime())

            n.notify('STATUS=Last report to InfluxDB at {}'.format(timestamp))
            n.notify("READY=1")
            sleep(self.interval)

    def send_msg(self, resp, name):
        if 'gravity_last_updated' in resp:
            del resp['gravity_last_updated']

        json_body = [
            {
                "measurement": "pihole",
                "tags": {
                    "host": name
                },
                "fields": resp
            }
        ]

        self.influx.write_points(json_body)


if __name__ == '__main__':
    config = ConfigParser()
    config.read(CONFIG_FILE)

    if len(config) < 2 and not path.isfile(CONFIG_FILE):
        copyfile(path.join(HERE, "config.ini.example"), CONFIG_FILE)
        print("Created config file from example. Please "
              "modify to your needs, and restart.")
        sys.exit(0)

    daemon = Daemon(config)

    try:
        daemon.run()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
        sys.exit(1)
