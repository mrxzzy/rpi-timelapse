#!/usr/bin/env python3

import os, sys, argparse, logging

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput

from datetime import datetime
import time
from rpi_status import Status

parser = argparse.ArgumentParser()
parser.add_argument('-p','--path', dest='path', default='.', help='Directory to output the video into. File will be named with the timestamp. Default is "."')
parser.add_argument('-s','--size', help='Size of image in WxH format. Default is 1920x1080.')
parser.add_argument('-j','--json-path', default='/tmp', help='Where to write the status file "rpi-timelapse.json". Default is /tmp')
parser.add_argument('--fps', default=12, help='Sets frames per second of video. Default is 12fps')
parser.add_argument('-d', '--debug', action='store_true', dest='verbose')
args = parser.parse_args()

if args.verbose:
  logging.basicConfig(level=logging.DEBUG)
else:
  logging.basicConfig(level=logging.WARN)

if os.path.exists(args.path) and os.access(args.path, os.W_OK):
  print("Directory %s exists and is writable." % (args.path))
  now = datetime.now().strftime('%Y-%m-%d-%H%M%S')
  path = '%s/%s.mp4' % (args.path,now)
    
  logging.debug("Will output video to %s" % (path))

camera = Picamera2()

status = Status.Out(path=args.json_path + '/rpi-timelapse.json')

if args.size:
  width,height = args.size.split('x')
else:
  width,height = (1920,1080)

resolution = (width,height)
fps_micro = int( (1/args.fps) * 1000000 )

config = camera.create_video_configuration(
  main={ "size": resolution }
)
camera.configure(config)

encoder = H264Encoder()
output = FfmpegOutput(path, audio=False)
encoder.output = output
camera.start()

camera.set_controls({"AwbEnable": False, "FrameDurationLimits": (fps_micro, fps_micro)})

time.sleep(1)
camera.autofocus_cycle()

logging.debug("begin at: %s" % (datetime.now()))
camera.start_encoder(encoder, quality=Quality.MEDIUM)

captures = 0
while True:
  try:
    time.sleep(1)
    tmpfile = args.json_path + '/timelapse_tmp.jpg'
    outfile = args.json_path + '/timelapse.jpg'
    logging.debug(outfile)
    still = camera.capture_request()
    still.save("main",tmpfile)
    still.release()
    os.rename(tmpfile,outfile)
    output = {
      'captures': captures,
      'last_file': outfile
    }
    captures = captures + 1
    status.send(output)

  except (KeyboardInterrupt, SystemExit):
    logging.warning("caught interrupt, cleaning up and exiting")
    camera.stop_encoder()
    camera.stop()
    sys.exit(0)

