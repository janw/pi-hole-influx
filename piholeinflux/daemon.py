import logging
from time import localtime
from time import sleep
from time import strftime

import sdnotify
from dynaconf.utils.boxing import DynaBox
from influxdb import InfluxDBClient

from piholeinflux.pihole import Pihole
from piholeinflux.settings import settings

logger = logging.getLogger(__name__)
n = sdnotify.SystemdNotifier()


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
        if self.single_run:
            logger.info("Single run mode.")
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
