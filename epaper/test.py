#!/usr/bin/python

import sys, os, logging, time
from waveshare_epd import epd2in13_V4
from PIL import Image,ImageDraw,ImageFont

class DisplayBuffer:

  def __init__(self,width,height):
    self.width = width
    self.height = height

    self.resources = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
    self.font = ImageFont.truetype(os.path.join(self.resources, 'fhwa-series-d.otf'), 24)
    self.symbols = ImageFont.truetype(os.path.join(self.resources, 'aristotelica.icons-bold.ttf'), 24)

    ascent, descent = self.font.getmetrics()
    self.textheight = self.font.getmask('Aj').getbbox()[3] + descent

    ImageDraw.ImageDraw.font = self.font

    self.image = Image.new('1', (self.height, self.width), 255)
    self.draw = ImageDraw.Draw(self.image)

  def text_in_spot(self,x,y,width,height,message):
    self.draw.rectangle((x,y,x + width, y + height), fill = 0)
    self.draw.text((x,y+1), message, fill = 255, anchor = 'lt')

    return(self.image)

  def symbol_in_spot(self,x,y,width,height,char):
    self.draw.rectangle((x,y,x + width, y + height), fill = 0)
    self.draw.text((x,y+1), char, fill = 255, font = self.symbols, anchor = 'lt')

    return(self.image)

try:
  logging.basicConfig(level=logging.DEBUG)
  epd = epd2in13_V4.EPD()
  epd.init()
  epd.Clear(0xFF)

  logging.info("init successful. display size: %s w, %s h" % (epd.width, epd.height))

  buffer = DisplayBuffer(epd.width,epd.height)

except Exception as e:
  logging.error("init failed: %s" % (e))
  sys.exit(1)

epd.displayPartBaseImage(epd.getbuffer(buffer.image))


buffer.text_in_spot(0,10,30,buffer.textheight,"Hq")
buffer.text_in_spot(40,20,30,buffer.textheight,"Gg")
buffer.text_in_spot(100,20,30,buffer.textheight,"Ay")
buffer.symbol_in_spot(180,20,30,30,"!")
epd.displayPartial(epd.getbuffer(buffer.image))
time.sleep(4)

buffer.text_in_spot(0,10,30,buffer.textheight,"Jj")
epd.displayPartial(epd.getbuffer(buffer.image))
time.sleep(4)

logging.info("done, cleaning up and exiting")
epd.init()
epd.Clear(0xFF)
epd.sleep()
