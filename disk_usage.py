#!/usr/bin/env python3

import os, sys, argparse, logging, subprocess#

def get_video_stats(filename):

  result = subprocess.Popen(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-show_entries", "stream=r_frame_rate", "-of", "csv", filename], stdout=subprocess.PIPE)

  while True:
    line = result.stdout.readline()
    if not line:
      break

    if line.startswith(b"stream"):
      (nom,dom) = line.split(b',')[1].rstrip(b'\n').split(b'/')
      framerate = float(nom) / float(dom)
    elif line.startswith(b'format'):
      length = line.split(b',')[1].rstrip(b'\n')

  return (float(length), framerate) 

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', dest='file', default='testlapse.mp4', help='Path to video file to do disk usage estimates for.')
parser.add_argument('-s', '--size', dest='size', default=512, help='Size of storage (in GB) to use for capacity test.')
parser.add_argument('-d', '--debug', action='store_true', dest='verbose')
args = parser.parse_args()

if args.verbose:
  logging.basicConfig(level=logging.DEBUG)
else:
  logging.basicConfig(level=logging.INFO)


if os.path.exists(args.file):
  logging.debug("Found the file: %s" % (args.file))
  (length, framerate) = get_video_stats(args.file)
  size = os.path.getsize(args.file)

  logging.debug("video length: %s , file size: %s" % (length,size))

  hours_capacity = ((args.size * 1024) / ((size / length) / 1024 / 1024) / 3600)

  logging.info("%s GB drive can store %d hours of this video (%s fps)" % (args.size,hours_capacity,framerate))


else:
  logging.error("file not found.")
