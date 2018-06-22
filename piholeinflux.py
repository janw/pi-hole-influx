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

def send_msg():

    json_body = [
        {
            "measurement": "pihole." + HOSTNAME.replace(".", "_"),
            "tags": {
                "host": HOSTNAME
            },
            "fields": {
                "domains_blocked": int(domains_blocked),
                "dns_queries_today": int(dns_queries_today),
                "ads_percentage_today": float(ads_percentage_today),
                "ads_blocked_today": int(ads_blocked_today),
                "unique_domains": int(unique_domains),
                "queries_forwarded": int(queries_forwarded),
                "queries_cached": int(queries_cached),
                "clients_ever_seen": int(clients_ever_seen)
            }
        }
    ]

    client = InfluxDBClient(INFLUXDB_SERVER, INFLUXDB_PORT, INFLUXDB_USERNAME, INFLUXDB_PASSWORD, INFLUXDB_DATABASE)
    # client.create_database(INFLUXDB_DATABASE) # Uncomment to create the database (expected to exist prior to feeding it data)
    client.write_points(json_body)

if __name__ == '__main__':
    while True:
        try:
            api = requests.get(PIHOLE_API) # URI to pihole server api
            API_out = api.json()
            domains_blocked = (API_out['domains_being_blocked'])
            dns_queries_today = (API_out['dns_queries_today'])
            ads_percentage_today = (API_out['ads_percentage_today'])
            ads_blocked_today = (API_out['ads_blocked_today'])
            unique_domains = (API_out['unique_domains'])
            queries_forwarded = (API_out['queries_forwarded'])
            queries_cached = (API_out['queries_cached'])
            clients_ever_seen = (API_out['clients_ever_seen'])

            send_msg()
            time.sleep(DELAY)

        except Exception as e:
            print('Failed, to report to InfluxDB:', str(e))
            print(traceback.format_exc())
            time.sleep(DELAY)
