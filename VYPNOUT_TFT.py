from datetime import datetime
from time import sleep
from lib_tft24T import TFT24T
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
import spidev
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import feedparser
import textwrap

DC = 25
RST = 24
LED = 23
TFT = TFT24T(spidev.SpiDev(), GPIO, landscape=False)
TFT.initLCD(DC, RST, LED)
draw = TFT.draw()
draw.rectangle((0,0,240,320), outline=0, fill=0)
TFT.backlite(0)
TFT.display()
