#! /usr/bin/env python3

import requests
from time import sleep, localtime, strftime
from influxdb import InfluxDBClient
import sdnotify
import sys
import logging

from dynaconf import LazySettings, Validator
from dynaconf.utils.boxing import DynaBox

settings = LazySettings(
    SETTINGS_FILE_FOR_DYNACONF="default.toml,user.toml",
    ENVVAR_PREFIX_FOR_DYNACONF="PIHOLE",
)
settings.validators.register(Validator("INSTANCES", must_exist=True))
settings.validators.validate()

n = sdnotify.SystemdNotifier()

logger = logging.getLogger(__name__)


class Pihole:
    """Container object for a single Pi-hole instance."""

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.timeout = settings.as_int("REQUEST_TIMEOUT")
        self.logger = logging.getLogger("pihole." + name)
        self.logger.info("Initialized for %s (%s)", name, url)

    def get_data(self):
        """Retrieve API data from Pi-hole, and return as dict on success."""
        response = requests.get(self.url, timeout=self.timeout)
        if response.status_code == 200:
            self.logger.debug("Got %d bytes", len(response.content))
            return response.json()
        else:
            self.logger.error(
                "Got unexpected response %d, %s", response.status_code, response.content
            )


class Daemon(object):
    def __init__(self, single_run=False):
        self.influx = InfluxDBClient(
            host=settings.INFLUXDB_HOST,
            port=settings.as_int("INFLUXDB_PORT"),
            username=settings.get("INFLUXDB_USERNAME"),
            password=settings.get("INFLUXDB_PASSWORD"),
            database=settings.INFLUXDB_DATABASE,
        )
        self.single_run = single_run

        if isinstance(settings.INSTANCES, DynaBox):
            self.piholes = [
                Pihole(name, url) for name, url in settings.INSTANCES.items()
            ]
        elif isinstance(settings.INSTANCES, list):
            self.piholes = [
                Pihole("pihole" + str(n + 1), url)
                for n, url in enumerate(settings.INSTANCES)
            ]
        elif "=" in settings.INSTANCES:
            name, url = settings.INSTANCES.split("=", maxsplit=1)
            self.piholes = [Pihole(name, url)]
        elif isinstance(settings.INSTANCES, str):
            self.piholes = [Pihole("pihole", settings.INSTANCES)]
        else:
            raise ValueError("Unable to parse instances definition(s).")

    def run(self):
        logger.info("Running daemon, reporting to InfluxDB at %s.", self.influx._host)
        while True:
            for pi in self.piholes:
                data = pi.get_data()
                self.send_msg(data, pi.name)
            timestamp = strftime("%Y-%m-%d %H:%M:%S %z", localtime())

            n.notify("STATUS=Last report to InfluxDB at {}".format(timestamp))
            n.notify("READY=1")
            if self.single_run:
                logger.info("Finished single run.")
                break
            sleep(settings.as_int("REPORTING_INTERVAL"))  # pragma: no cover

    def send_msg(self, resp, name):
        if "gravity_last_updated" in resp:
            del resp["gravity_last_updated"]

        # Monkey-patch ads-% to be always float (type not enforced at API level)
        resp["ads_percentage_today"] = float(resp.get("ads_percentage_today", 0.0))

        json_body = [{"measurement": "pihole", "tags": {"host": name}, "fields": resp}]

        self.influx.write_points(json_body)


def main(single_run=False):
    log_level = (settings.LOG_LEVEL).upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(levelname)s: [%(name)s] %(message)s",
    )

    daemon = Daemon(single_run)

    try:
        daemon.run()
    except KeyboardInterrupt:
        sys.exit(0)  # pragma: no cover
    except Exception:
        logger.exception("Unexpected exception", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
