# piholestatus
A script to display Pi-Hole stats in Grafana via InfluxDB


Script originally created by JON HAYWARD: https://fattylewis.com/Graphing-pi-hole-stats/
Adapted fo work with InfluxDB by /u/tollsjo in December 2016

To install and run the script as a service under SystemD. See: https://linuxconfig.org/how-to-automatically-execute-shell-script-at-startup-boot-on-systemd-linux

You can set this up on pretty much any host that has access to the Pi-Hole API and the InfluxDB API. I opted to run it as a service on the Pi-Hole Host. It requires the http API to be enabled on Influx. It also requires a "pip install influxdb" to work. Tested on Ubuntu 16.04

Dashboard Example: 
![Grafana Dashboard](http://i.imgur.com/4bitvQt.png)
