# Pi-hole-Influx

[![Build Status](https://travis-ci.org/janw/pi-hole-influx.svg?branch=master)](https://travis-ci.org/janw/pi-hole-influx)
[![Maintainability](https://api.codeclimate.com/v1/badges/cfe71020e6505ca65cfc/maintainability)](https://codeclimate.com/github/janw/pi-hole-influx/maintainability)
[![Coverage Status](https://coveralls.io/repos/github/janw/pi-hole-influx/badge.svg?branch=master)](https://coveralls.io/github/janw/pi-hole-influx?branch=master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

A simple daemonized script to report Pi-Hole stats to an InfluxDB, ready to be displayed via Grafana.

**Heads-up: the configuration options changed fundamentally in recent versions. Please read up on the current state below.**

![Example Grafana Dashboard](.readme-assets/dashboard.png)

## Setup (Using Docker)

To use docker for running the daemon, use the following command:

```bash
docker run \
-e DATABASE_URL="influxdb://pihole:mysecretpassword@hostname" \
-e PIHOLE_INSTANCES="localhost=http://127.0.0.1/admin/api.php" \
janw/pi-hole-influx
```

Note, that the `DATABASE_URL` variable contains the InfluxDB connection details in popular URL format inspired by [SQLAlchemy](https://docs.sqlalchemy.org/en/latest/core/engines.html), i.e.

```bash
DATABASE_URL="influxdb://<username>:<password>@<hostname>[:<port]>[/<database>]"
```

If port and database are not given, they default to `8086`, and `pihole`, respectively.

`PIHOLE_INSTANCES` contains the Pi-hole instances that are to be reported. Multiple instances can be seperated by comma:

```bash
PIHOLE_INSTANCES="[<name>=]http://127.0.0.1/admin/api.php,[<second_name>=]http://192.168.42.79/admin/api.php[,…]"
```

Note that instances can be prefixed by a custom name, separated by an equal sign.


## Setup (Traditional Way)

As Pi-hole (as the name suggests) is built specifically with the Raspberry Pi in mind (and I run it on there as well), the following steps assume an instance of Pi-hole on Raspbian Strech Lite, with no additional modifications so far. Piholestatus will be configured to run on the same Pi.

First install the necessary packages via apt as Raspbian Lite does have neither git nor pip installed.

```bash
sudo apt update
sudo apt install git python3-pip -y
```

Now clone the repo, install the Python dependencies, and make sure to copy and adjust the example configuation file to match your setup.

```bash
git clone https://github.com/janw/pi-hole-influx.git ~/pi-hole-influx
cd ~/pi-hole-influx

# Install requirements via pip
pip3 install -r requirements.txt

# Copy config.example and modify it (should be self-explanatory)
cp config.ini.example config.ini
vi config.ini
```

Before starting the daemon for the first time, symlink the systemd service into place, reload, and enable the service.

```bash
sudo ln -s /home/pi/pi-hole-influx/piholeinflux.service /etc/systemd/system/
sudo systemctl --system daemon-reload
sudo systemctl enable piholeinflux.service
```

Now you're ready to start the daemon. Wait a few seconds to check its status.

```bash
sudo systemctl start piholeinflux.service
sudo systemctl status piholeinflux.service
```

The status should look as follows. Note the `Status:` line showing the last time, the daemon reported to InfluxDB:

```text
● piholeinflux.service - Pi-hole-Influx - Send Pi-hole statistics to InfluxDB for visualization
   Loaded: loaded (/home/pi/pi-hole-influx/piholeinflux.service; enabled; vendor preset: enabled)
   Active: active (running) since Fri 2018-06-22 19:03:56 UTC; 10min ago
     Docs: https://github.com/janw/pi-hole-influx
 Main PID: 21329 (python)
   Status: "Reported to InfluxDB at 2018-06-22 19:14:09 +0000"
   CGroup: /system.slice/piholeinflux.service
           └─21329 /usr/bin/python /home/pi/pi-hole-influx/piholeinflux.py
```

## Set up a Grafana Dashboard

The example dashboard seen [at the top](#pi-hole-influx) uses the collected data and displays it in concise and sensible graphs and single stats. The dashboard can be imported into your Grafana instance from the `dashboard.json` file included in the repo, or by using ID `6603` to [import it from Grafana's Dashboard Directory](https://grafana.com/dashboards/6603).

## Monitoring multiple Pi-holes

As shown in the example configuration, it is possibe to add more than one Pi-hole instance to be monitored. Simply add more instances to the `[pihole]`, using a different name for the instance as a config entry, like so:

```ini
[pihole]
pihole = http://127.0.0.1/admin/api.php
second_pihole = http://192.168.27.42/admin/api.php
```

## Attributions

The script originally [created by Jon Hayward](https://fattylewis.com/Graphing-pi-hole-stats/), adapted to work with InfluxDB [by /u/tollsjo in December 2016](https://github.com/sco01/piholestatus), and [improved and extended by @johnappletree](https://github.com/johnappletree/piholestatus). "If I have seen further it is by standing on the shoulders of giants". 🤓
