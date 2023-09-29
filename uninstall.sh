#!/bin/bash

echo "delete udev rules.."
rm -f /etc/udev/rules.d/99-rpi-timelapse.rules
echo "delete mount script.."
rm -f /usr/local/bin/rpi-timelapse.py
echo "disable systemd units.."
systemctl disable media-dest.mount
systemctl disable rpi-timelapse.service
echo "delete systemd units.."
rm -f /etc/systemd/system/media-dest.mount
rm -f /etc/systemd/system/rpi-timelapse.service

echo "reloading configs.."
systemctl daemon-reload
udevadm control --reload-rules
