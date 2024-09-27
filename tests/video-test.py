#!/usr/bin/env python3

# convert to mp4:
# ffmpeg -i testlapse.h264 -codec copy testlapse.mp4

import os, sys, argparse, logging, subprocess

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
#from picamera2.outputs import FileOutput
from picamera2.outputs import 

from datetime import datetime
import time
from rpi_status import Status
from libcamera import controls

class TimelapseOutput(FileOutput):
  def __init__(self, file=None, pts=None, speed=10):
    self.speed = int(speed)
    super().__init__(file, pts)

  def outputtimestamp(self, timestamp):
    if timestamp == 0:
      print("# timestamp format v2", file=self.ptsoutput, flush=True)

    timestamp //= self.speed
    super().outputtimestamp(timestamp)

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
output = TimelapseOutput("%s/testlapse.h264" % (path), "%s/testlapse.time" % (path), speedup_factor)
encoder.output = output

camera.start()

# wait a second, then disable auto exposure and auto white balance
time.sleep(1)
camera.set_controls({"AeEnable": False, "AwbEnable": False, "FrameRate": framerate})
time.sleep(1)

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

merge = subprocess.Popen(['mkvmerge', '-o', '%s/timelapse.mkv' % (path), "--timestamps", "0:%s/testlapse.time" % (path), '%s/testlapse.h264' % (path)])
merge.wait()
