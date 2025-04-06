#!/usr/bin/env python3

import os, sys, argparse, logging
from picamera2 import Picamera2
from datetime import datetime
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from rpi_status import Status
from libcamera import controls

def take_picture(path,config,status):
  global captures

  outfile = '%s/image%09d.jpg' % (path,captures)
  camera.capture_file(outfile)
  captures = captures + 1

  output = {
    'captures': captures,
    'last_file': outfile
  }
  status.send(output)

logging.basicConfig(level=logging.WARN)

parser = argparse.ArgumentParser()
parser.add_argument('-p','--path', dest='path', default='.', help='Directory to output images into. Will make timestamped subdirectories in this folder.')
parser.add_argument('-i','--interval', dest='interval', default=1.3, type=float, help='Seconds to delay between image captures. Default 1.3 seconds (fastest the 3B can capture without overruns.')
parser.add_argument('-s','--size', help='Size of image in WxH format. Default is sensor resolution.')
parser.add_argument('-j','--json-path', default='/tmp', help='Where to write the status file "rpi-timelapse.json". Default is /tmp')
args = parser.parse_args()

if os.path.exists(args.path) and os.access(args.path, os.W_OK):
  print("Directory %s exists and is writable." % (args.path))
  now = datetime.now().strftime('%Y-%m-%d-%H%M%S')
  path = '%s/%s' % (args.path,now)
  if not os.path.exists(path):
    os.mkdir(path)
    
  print("Created output directory %s" % (path))

camera = Picamera2()
camera.start()
camera.set_controls({"AfMode": controls.AfModeEnum.Manual})

# 7.2
status = Status.Out(path=args.json_path + '/rpi-timelapse.json')

if args.size:
  width,height = args.size.split('x')
  config = camera.create_still_configuration(main={"size": (int(width), int(height))})
else:
  config = camera.create_still_configuration()

camera.switch_mode(config)

controls = {
  'LensPosition': 7.2
}
camera.set_controls(controls)
time.sleep(1)

cron = BlockingScheduler()
captures = 0
cron.add_job(take_picture, trigger='interval', seconds=args.interval, args=[path,config,status])

try:
  print("begin at: %s" % (datetime.now()))
  cron.start()
except (KeyboardInterrupt, SystemExit):
  print("caught interrupt, cleaning up and exiting")
  camera.close()
  sys.exit(0)

