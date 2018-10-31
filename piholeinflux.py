#! /usr/bin/python

from __future__ import print_function
import requests
from time import sleep, localtime, strftime
from influxdb import InfluxDBClient
from configparser import ConfigParser
from os import path
import traceback
import sdnotify
from datetime import datetime
import sys

HERE = path.dirname(path.realpath(__file__))
config = ConfigParser()
config.read(path.join(HERE, 'config.ini'))

HOSTNAME = config['pihole']['instance_name']
PIHOLE_API = config['pihole']['api_location']
DELAY = config['pihole'].getint('reporting_interval', 10)

INFLUXDB_SERVER = config['influxdb'].get('hostname', '127.0.0.1')
INFLUXDB_PORT = config['influxdb'].getint('port', 8086)
INFLUXDB_USERNAME = config['influxdb']['username']
INFLUXDB_PASSWORD = config['influxdb']['password']
INFLUXDB_DATABASE = config['influxdb']['database']

INFLUXDB_CLIENT = InfluxDBClient(INFLUXDB_SERVER,
                                 INFLUXDB_PORT,
                                 INFLUXDB_USERNAME,
                                 INFLUXDB_PASSWORD,
                                 INFLUXDB_DATABASE)

n = sdnotify.SystemdNotifier()
n.notify("READY=1")

def send_msg(resp):
    if 'gravity_last_updated' in resp:
        del resp['gravity_last_updated']

    json_body = [
        {
            "measurement": "pihole",
            "tags": {
                "host": HOSTNAME
            },
            "fields": resp
        }
    ]

    INFLUXDB_CLIENT.write_points(json_body)


if __name__ == '__main__':
    while True:
        try:
            api = requests.get(PIHOLE_API)  # URI to pihole server api
            send_msg(api.json())
            timestamp = strftime('%Y-%m-%d %H:%M:%S %z', localtime())
            n.notify('STATUS=Reported to InfluxDB at {}'.format(timestamp))

        except Exception as e:
            msg = 'Failed, to report to InfluxDB:'
            n.notify('STATUS={} {}'.format(msg, str(e)))
            print(msg, str(e))
            print(traceback.format_exc())
            sys.exit(1)

        sleep(DELAY)
