# Pi-hole-Influx

[![Build Status](https://github.com/janw/pi-hole-influx/actions/workflows/docker-build.yaml/badge.svg?branch=fix-readme-badges)](https://github.com/janw/pi-hole-influx/pkgs/container/pi-hole-influx)

[![Coverage Status](https://codecov.io/gh/janw/pi-hole-influx/branch/master/graph/badge.svg?token=EZTLSEAZD9)](https://codecov.io/gh/janw/pi-hole-influx)
[![Maintainability](https://api.codeclimate.com/v1/badges/cfe71020e6505ca65cfc/maintainability)](https://codeclimate.com/github/janw/pi-hole-influx/maintainability)

[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

A simple daemonized script to report Pi-Hole stats to an InfluxDB v2 instance, ready to be displayed via Grafana.

**⚠️ The docker image name has been changed to `ghcr.io/janw/pi-hole-influx`. Please update your deployment accordingly. If you are still using InfluxDB v1, please use [version 1.0](https://github.com/janw/pi-hole-influx/tree/v1.0) (`ghcr.io/janw/pi-hole-influx:v1`) of Pi-hole-Influx. Newer versions (tagged `:v2`) only support InfluxDB v2. ⚠️**

![Example Grafana Dashboard](.readme-assets/dashboard.png)

## Setup (Using Docker)

* To use docker for running the daemon, use the following command:

  ```bash
  docker run \
    -e PIHOLE_INFLUXDB_URL=https://127.0.0.1:8086 \
    -e PIHOLE_INFLUXDB_BUCKET=mybucket \
    -e PIHOLE_INFLUXDB_TOKEN=mytoken \
    -e PIHOLE_INFLUXDB_ORG=myorg \
    -e PIHOLE_INSTANCES='[{
          "name": "pihole",
          "base_url": "http://127.0.0.1",
          "api_token": "<your_pihole_api_token>"
        }]' \
    --network host \
    ghcr.io/janw/pi-hole-influx:v2
  ```

where `PIHOLE_INSTANCES` is a JSON-formatted list of instances to monitor with required fields of `name` and `base_url` and an (theorically optional but generally required) `api_token` (see below).

### Authentication

Newer versions of Pi-hole [require authentication when accessing the API](https://pi-hole.net/blog/2022/11/17/upcoming-changes-authentication-for-more-api-endpoints-required/#page-content) of an instance that has been configured with a web-interface password. If that is the case for your instance (as it should be), please make sure to include the `api_token` in the instance config. You can find in the Pi-hole admin panel under Settings -> API / Web interface -> Show API token.

### Configuration file

An alternative to configure Pi-hole-Influx through environment variables is a TOML-formatted configuration file. See [user.toml.example](user.toml.example) for an example configuration. It can be mounted into the container under `/config/user.toml` to provide the configuration instead.

## Docker-compose example

If you want to run the daemon through Docker-compose, you might appreciate the configuration example below.

```yaml
version: "2"
services:
  piholeinflux:
    image: ghcr.io/janw/pi-hole-influx:v2
    container_name: piholeinflux
    restart: unless-stopped
    environment:

      # Replace details with your InfluxDB's hostname and credentials
      PIHOLE_INFLUXDB_URL: "http://10.10.10.1:8086"
      PIHOLE_INFLUXDB_TOKEN: "mytoken"
      PIHOLE_INFLUXDB_BUCKET: "pihole"
      PIHOLE_INFLUXDB_ORG: "eee0001234asdf"

      # Replace with your Pi-Hole's base_url and api_token below
      PIHOLE_INSTANCES: |
        [{
          "name": "pihole",
          "base_url": "https://127.0.0.1",
          "api_token": "<your_pihole_api_token>"
        }]

      # Additional options that can be adjusted
      PIHOLE_REQUEST_TIMEOUT: "15"  # seconds
      PIHOLE_REQUEST_VERIFY_SSL: "False"
      PIHOLE_REPORTING_INTERVAL: "90"  # seconds

    # OPTIONAL: Instead of the aobove environment variables,
    #           use a custom copy of the user.toml config file.
    volumes:
      - ./custom/config.toml:/config/user.toml
```

## Setup (Traditional Way)

As Pi-hole (as the name suggests) is built specifically with the Raspberry Pi in mind, the following steps assume an instance of Pi-hole running on a Raspbian installation, with no additional modifications. Pi-hole-Influx will be configured to run on the same Pi.

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
cp user.toml.example user.toml
vi user.toml
```

Before starting the daemon for the first time, symlink the systemd service into place, reload, and enable the service. Note that if you are using a user that isn't `pi`, you must edit piholeinflux.service and change the `User` and `WorkingDirectory` to match yours.

```bash
sudo cp piholeinflux.service /etc/systemd/system/
sudo systemctl --system daemon-reload
sudo systemctl enable piholeinflux.service
```

Now you're ready to start the daemon. Wait a few seconds to check its status.

```bash
$ sudo systemctl start piholeinflux.service
$ sudo systemctl status piholeinflux.service

● piholeinflux.service - Pi-hole-Influx - Send Pi-hole statistics to InfluxDB for visualization
     Loaded: loaded (/etc/systemd/system/piholeinflux.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2023-02-11 22:22:30 CET; 56s ago
       Docs: https://github.com/janw/pi-hole-influx
   Main PID: 776022 (python3)
      Tasks: 3 (limit: 1830)
        CPU: 1.059s
     CGroup: /system.slice/piholeinflux.service
             └─776022 /usr/bin/python3 ./piholeinflux.py
```

## Set up a Grafana Dashboard

The example dashboard seen [at the top](#pi-hole-influx) uses the collected data and displays it in concise and sensible graphs and single stats. The dashboard can be imported into your Grafana instance from the `dashboard.json` file included in the repo, or by using ID `6603` to [import it from Grafana's Dashboard Directory](https://grafana.com/dashboards/6603).

## Attributions

The script originally [created by Jon Hayward](https://fattylewis.com/Graphing-pi-hole-stats/), adapted to work with InfluxDB [by /u/tollsjo in December 2016](https://github.com/sco01/piholestatus), and [improved and extended by @johnappletree](https://github.com/johnappletree/piholestatus). "If I have seen further it is by standing on the shoulders of giants". 🤓
