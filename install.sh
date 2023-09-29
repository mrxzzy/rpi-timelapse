#!/bin/bash

echo "copying udev rules.."
cp 99-rpi-timelapse.rules /etc/udev/rules.d/
echo "copying timelapse script.."
cp rpi-timelapse.py /usr/local/bin/
echo "copying systemd unit.."
cp media-dest.mount /etc/systemd/system/
cp rpi-timelapse.service /etc/systemd/system/

echo "enabling units and reloading configs.."
systemctl daemon-reload
systemctl enable media-dest.mount
systemctl enable rpi-timelapse.service
udevadm control --reload-rules

echo "chmod scripts.."
chmod 755 /usr/local/bin/sd-backup.py
