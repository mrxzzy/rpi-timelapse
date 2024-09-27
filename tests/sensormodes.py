#!/usr/bin/env python3

from pprint import *
from picamera2 import Picamera2

camera = Picamera2()
pprint(camera.sensor_modes)

