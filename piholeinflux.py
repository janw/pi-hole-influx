#! /usr/bin/python

from __future__ import print_function
import requests
from time import sleep, localtime, strftime
from influxdb import InfluxDBClient
from configparser import ConfigParser
<<<<<<< HEAD
from os import path
from urllib.parse import urlparse
from shutil import copyfile
=======
from os import path, environ
from urllib.parse import urlparse, splitport, splituser, splitpasswd
>>>>>>> Major refactor, better env var handling
import traceback
import sdnotify
import sys
import logging

HERE = path.dirname(path.realpath(__file__))
CONFIG_FILE = path.join(HERE, "config.ini")


n = sdnotify.SystemdNotifier()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: [%(name)s] %(message)s")


class Config(ConfigParser):
    logger = logging.getLogger(__name__)

    def apply_environ(self):
        url = environ.get("DATABASE_URL")
        self._apply_database_url(url)

        instances = environ.get("PIHOLE_INSTANCES")
        self._apply_pihole_instances(instances)

    def _apply_database_url(self, url):
        if not url:
            return

        self.logger.debug("Applying database parameters from url: %s", url)
        parts = urlparse(url)
        if parts.scheme != "influxdb":
            return

        database = "pihole" if parts.path == "/" else parts.path.strip("/")
        hostname, port = splitport(parts.netloc)
        username, hostname = splituser(hostname)
        username, password = splitpasswd(username)

        if "influxdb" not in self:
            self.add_section("influxdb")
        self["influxdb"]["port"] = port if port else 8086
        self["influxdb"]["database"] = database
        self["influxdb"]["hostname"] = hostname
        self["influxdb"]["username"] = username
        self["influxdb"]["password"] = password

    def _apply_pihole_instances(self, piholes):
        if not piholes:
            return

        self.logger.debug("Applying pihole instances: %s", piholes)
        if "pihole" not in self:
            self.add_section("pihole")

        instances = piholes.split(",")
        for inst in instances:
            splits = inst.split("=")
            if len(splits) == 1:
                self["pihole"][urlparse(inst).netloc] = inst
            else:
                self["pihole"][splits[0]] = splits[1]


config = Config()
config.read(CONFIG_FILE)
config.apply_environ()


class Pihole:
    """Container object for a single Pi-hole instance."""

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.timeout = config["defaults"].getint("request_timeout", 10)
        self.logger = logging.getLogger(__name__ + name)
        self.logger.debug("Initialized for %s", name, url)

    def get_data(self):
        """Retrieve API data from Pi-hole, and return as dict on success."""
        response = requests.get(self.url, timeout=self.timeout)
        if response.status_code == 200:
            self.logger.debug("Got %d bytes", len(response.content))
            return response
        else:
            self.logger.error(
                "Got unexpected response %d, %s", response.status_code, response.content
            )


class Daemon(object):
    logger = logging.getLogger(__name__)

    def __init__(self, config):
        self.influx = InfluxDBClient(
            host=config["influxdb"].get("hostname", "127.0.0.1"),
            port=config["influxdb"].getint("port", 8086),
            username=config["influxdb"]["username"],
            password=config["influxdb"]["password"],
            database=config["influxdb"]["database"],
        )

        self.piholes = [Pihole(name, url) for name, url in config["pihole"].items()]
        self.interval = config["defaults"].getint("reporting_interval", 30)

    def run(self):
        while True:
            for pi in self.piholes:
                data = pi.get_data()
                self.send_msg(data, pi.name)
            timestamp = strftime("%Y-%m-%d %H:%M:%S %z", localtime())

            n.notify("STATUS=Last report to InfluxDB at {}".format(timestamp))
            n.notify("READY=1")
            sleep(self.interval)

    def send_msg(self, resp, name):
        if "gravity_last_updated" in resp:
            del resp["gravity_last_updated"]

        json_body = [{"measurement": "pihole", "tags": {"host": name}, "fields": resp}]

        self.influx.write_points(json_body)


if __name__ == "__main__":
    if "pihole" not in config or len(config["pihole"]) < 1:
        print("Missing Pi-hole configuration")
        sys.exit(1)

    daemon = Daemon(config)

    try:
        daemon.run()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
        sys.exit(1)
