# Pi-hole-Influx

A simple script to report Pi-Hole stats to an InfluxDB, ready to be displayed via Grafana (and potentially other visualization platforms)


## Requirements and Setup

As Pi-hole (as the name suggests) is built specifically with the Raspberry Pi in mind (and I run it on there as well), the following steps assume an instance of Pi-hole on Raspbian Strech Lite, with no additional modifications so far. Piholestatus will be configured to run on the same Pi. 

First install the necessary packages via apt as Raspbian Lite does have neither git nor pip installed.

```bash
sudo apt update
sudo apt install git python-pip -y
```

Now clone the repo, and create the necessary files/symlinks

```bash
git clone https://github.com/janw/pi-hole-influx.git ~/pi-hole-influx

sudo ln -s /home/pi/pi-hole-influx/piholeinflux.service /etc/systemd/system/
sudo systemctl --system daemon-reload
sudo systemctl enable piholeinflux.service
```
Before starting the daemon for the first time, install the Python dependencies, and make sure to copy and adjust the example configuation file to match your setup.

```
cd ~/pi-hole-influx

pip install -r requirements.txt

cp config.ini.example config.ini
vi config.ini
```

Now you're ready to start the daemon. Wait a few seconds to check its status.

```bash
sudo systemctl start piholeinflux.service
sudo systemctl status piholeinflux.service
```

Dashboard Example: 
![Grafana Dashboard](http://i.imgur.com/4bitvQt.png)


## Attribution

The script originally [created by Jon Hayward](https://fattylewis.com/Graphing-pi-hole-stats/), adapted to work with InfluxDB [by /u/tollsjo in December 2016](https://github.com/sco01/piholestatus), and [improved and extended by @johnappletree](https://github.com/johnappletree/piholestatus).
