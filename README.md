# Pi-hole-Influx

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/522433a84177441c917768f4621f1b09)](https://app.codacy.com/app/janw/pi-hole-influx?utm_source=github.com&utm_medium=referral&utm_content=janw/pi-hole-influx&utm_campaign=Badge_Grade_Dashboard)

A simple daemonized script to report Pi-Hole stats to an InfluxDB, ready to be displayed via Grafana.

![Example Grafana Dashboard](.readme-assets/dashboard.png)

## Requirements and Setup

As Pi-hole (as the name suggests) is built specifically with the Raspberry Pi in mind (and I run it on there as well), the following steps assume an instance of Pi-hole on Raspbian Strech Lite, with no additional modifications so far. Piholestatus will be configured to run on the same Pi. 

First install the necessary packages via apt as Raspbian Lite does have neither git nor pip installed.

```bash
sudo apt update
sudo apt install git python-pip -y
```

Now clone the repo, install the Python dependencies, and make sure to copy and adjust the example configuation file to match your setup.

```bash
git clone https://github.com/janw/pi-hole-influx.git ~/pi-hole-influx
cd ~/pi-hole-influx

# Install requirements via pip
pip install -r requirements.txt

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

```
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


## Attributions

The script originally [created by Jon Hayward](https://fattylewis.com/Graphing-pi-hole-stats/), adapted to work with InfluxDB [by /u/tollsjo in December 2016](https://github.com/sco01/piholestatus), and [improved and extended by @johnappletree](https://github.com/johnappletree/piholestatus). "If I have seen further it is by standing on the shoulders of giants". 🤓
