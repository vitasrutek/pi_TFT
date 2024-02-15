#!/bin/bash
for (( ; ; ))
do
#sensors | awk '{print $2}' | tail -6 | head -1 | cut -c 2-5 | tee /home/vita/tmpfs/teplota_cpu
#awk '{print int($1/3600)":"int(($1%3600)/60)":"int($1%60)}' /proc/uptime | tee /home/vita/tmpfs/uptime_cpu


#python3 /var/www/html/DHT_read.py | tee /home/vita/tmpfs/teplota_int
ping -c 1 192.168.0.12
returncode=$?
if [ "$returncode" -eq "0" ]
then
    curl 192.168.0.12 | head -n 74 | tail -n 1 | awk '{print $1, $2}' | tee /home/vita/tmpfs/teplota_ext
fi
sleep 60
done
