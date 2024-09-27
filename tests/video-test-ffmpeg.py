#!/usr/bin/env python3

# convert to mp4:
# ffmpeg -i testlapse.h264 -codec copy testlapse.mp4

import os, sys, argparse, logging, subprocess

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput

from datetime import datetime
import time
from rpi_status import Status
from libcamera import controls

def take_picture(path,config,status):

  outfile = '%s/preview_image.jpg' % (path)
  camera.capture_file(outfile)

  output = {
    'captures': captures,
    'last_file': outfile
  }
  status.send(output)


parser = argparse.ArgumentParser()
parser.add_argument('-p','--path', dest='path', default='.', help='Directory to output images into. Will make timestamped subdirectories in this folder.')
parser.add_argument('-i','--interval', dest='interval', default=1.3, type=float, help='Seconds to delay between image captures. Default 1.3 seconds (fastest the 3B can capture without overruns.')
parser.add_argument('-s','--size', help='Size of image in WxH format. Default is sensor resolution.')
parser.add_argument('-j','--json-path', default='/tmp', help='Where to write the status file "rpi-timelapse.json". Default is /tmp')
parser.add_argument('-d', '--debug', action='store_true', dest='verbose')
args = parser.parse_args()

if args.verbose:
  logging.basicConfig(level=logging.DEBUG)
else:
  logging.basicConfig(level=logging.WARN)

if os.path.exists(args.path) and os.access(args.path, os.W_OK):
  print("Directory %s exists and is writable." % (args.path))
  now = datetime.now().strftime('%Y-%m-%d-%H%M%S')
  path = '%s/%s' % (args.path,now)
  if not os.path.exists(path):
    os.mkdir(path)
    
  print("Created output directory %s" % (path))

camera = Picamera2()

status = Status.Out(path=args.json_path + '/rpi-timelapse.json')

if args.size:
  width,height = args.size.split('x')
else:
  #width,height = (1280,720)
  width,height = (1920,1080)

resolution = (width,height)

speedup_factor = 5
framerate = 10 

config = camera.create_video_configuration(
  main= {"size": resolution}
  #main={"size": (width, height), "format": "RGB888"},
  #lores={"size": (width, height), "format": "YUV420"},
  #controls={'FrameDurationLimits': (framerate_microseconds, framerate_microseconds)}
)
camera.configure(config)

encoder = H264Encoder()
output = FfmpegOutput("%s/testlapse.mp4" % (path), audio=False)
encoder.output = output

camera.start()

# wait a second, then disable auto exposure and auto white balance
time.sleep(1)
#camera.set_controls({"AeEnable": False, "AwbEnable": False, "FrameRate": framerate})

fps_seconds = 24
fps_micro = int( (1/fps_seconds) * 1000000 )

#camera.set_controls({"AeEnable": False, "AwbEnable": False, "FrameDurationLimits": (fps_micro, fps_micro)})
camera.set_controls({"FrameDurationLimits": (fps_micro, fps_micro)})

time.sleep(1)
camera.autofocus_cycle()

camera.start_encoder(encoder, quality=Quality.MEDIUM)

loop = 0
while loop < 11:
  time.sleep(1)
  loop = loop + 1

  outfile = os.path.abspath("%s/preview.jpg" % (path))
  still = camera.capture_request()
  still.save("main",outfile)
  still.release()
  output = {
    'captures': loop,
    'last_file': outfile
  }
  status.send(output)
  print("got a still")

camera.stop_encoder()
camera.stop()

