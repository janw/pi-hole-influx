#! /usr/bin/python

from __future__ import print_function
import requests
import time
from influxdb import InfluxDBClient
from configparser import ConfigParser
from os import path
import traceback

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


def send_msg(resp):

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
            time.sleep(DELAY)

        except Exception as e:
            print('Failed, to report to InfluxDB:', str(e))
            print(traceback.format_exc())
            time.sleep(DELAY)
