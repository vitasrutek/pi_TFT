# -*- coding: utf-8 -*-
from datetime import datetime
from time import sleep
from lib_tft24T import TFT24T
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
import spidev
import subprocess
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import locale
import os
import Adafruit_DHT


locale.setlocale(locale.LC_TIME, 'cs_CZ.UTF-8')
DHTsensor = Adafruit_DHT.DHT22
DHTpin = 4
DC = 25  # pin 15 on P1 pin out is the same as GPIO22
RST = 24
LED = 23
TFT = TFT24T(spidev.SpiDev(), GPIO, landscape=False)
TFT.initLCD(DC, RST, LED)
draw = TFT.draw()
fontB1 = ImageFont.truetype(r'/home/FONTS/Ubuntu-B.ttf', 50)
fontB2 = ImageFont.truetype(r'/home/FONTS/Ubuntu-B.ttf', 30)
fontB3 = ImageFont.truetype(r'/home/FONTS/Ubuntu-B.ttf', 20)
fontR1 = ImageFont.truetype(r'/home/FONTS/Ubuntu-R.ttf', 15)
fontR2 = ImageFont.truetype(r'/home/FONTS/Ubuntu-R.ttf', 20)

def cteni():
    global humidity, temperature, VENKU, ZITRA_TEPLOTA, ZITRA_STAV, ZITRA_IKONA, DNES_TEPLOTA, DNES_STAV, DNES_IKONA
    VENKU_cmd = 'cat /home/tmpfs/teplota_ext | cut -d\  -f1'
    VENKU = subprocess.check_output(VENKU_cmd, shell = True )
    humidity, temperature = Adafruit_DHT.read_retry(DHTsensor, DHTpin)
    ZITRA_TEPLOTA_cmd = "jq .daily[1].temp.day /home/tmpfs/pocasi-onecall.json"
    ZITRA_TEPLOTA = subprocess.check_output (ZITRA_TEPLOTA_cmd, shell = True)
    ZITRA_STAV_cmd = "jq .daily[1].weather[0].description /home/tmpfs/pocasi-onecall.json | rev | cut -c2- | rev | cut -c2-"
    ZITRA_STAV = subprocess.check_output (ZITRA_STAV_cmd, shell = True)
    ZITRA_IKONA_cmd = "jq .daily[1].weather[0].icon /home/tmpfs/pocasi-onecall.json | cut -c2- | rev | cut -c2- | rev"
    ZITRA_IKONA = subprocess.check_output (ZITRA_IKONA_cmd, shell = True)
    DNES_TEPLOTA_cmd = "jq .daily[0].temp.day /home/tmpfs/pocasi-onecall.json"
    DNES_TEPLOTA = subprocess.check_output (DNES_TEPLOTA_cmd, shell = True)
    DNES_STAV_cmd = "jq .daily[0].weather[0].description /home/tmpfs/pocasi-onecall.json | rev | cut -c2- | rev | cut -c2-"
    DNES_STAV = subprocess.check_output (DNES_STAV_cmd, shell = True)
    DNES_IKONA_cmd = "jq .daily[0].weather[0].icon /home/tmpfs/pocasi-onecall.json | cut -c2- | rev | cut -c2- | rev"
    DNES_IKONA = subprocess.check_output (DNES_IKONA_cmd, shell = True)

x = 0
WW = (120)
TFT.backlite(1)
II = 0
PP = 0
cteni()
#pocasi_update()
while True:
#    TFT.clear()
    if II == 10:
        cteni()
        II = 0
    else:
        II = II + 1
        print ('II je', II)

    draw.rectangle((0,0,240,320), outline=0, fill=0)
    draw.line((WW, 45, WW, 115))
    draw.line((10, 45, 230, 45))
    draw.line((10, 115, 230, 115))
    draw.line((10, 165, 230, 165))
    draw.line((10, 167, 230, 167))
    draw.line((WW, 167, WW, 310))#u pocasi kolma   

#cas a datum   
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime ('%d. %B %Y')

    W, H = (240, 320)
    _, _, w, h = draw.textbbox((0, 0), str(current_date), font=fontR1)
    draw.text(((W-w)/2,0), str(current_date), font=fontR1, fill="white")
    _, _, w, h = draw.textbbox((0, 0), str(current_time), font=fontB2)
    draw.text(((W-w)/2,10), str(current_time), font=fontB2, fill="white")

    #data
    if temperature is not None:
        _, _, w, h = draw.textbbox((0, 0), ('{0:0.1f}'.format(temperature)), font=fontB1)
        draw.text(((WW-w)/2, 57),       ('{0:0.1f}'.format(temperature)),  font=fontB1, fill='#00EFFF')
    else:
        print ('chyba čtení teploty')
    if humidity is not None:
        _, _, w, h = draw.textbbox((0, 0), ('{0:0.1f}'.format(humidity)), font=fontB1)
        draw.text((((WW-w)/2)+120, 57),        ('{0:0.1f}'.format(humidity)),  font=fontB1, fill='#00EFFF')
    else:
        print ('chyba čtení vlhkosti')
    _, _, w, h = draw.textbbox((0, 0), str(VENKU.decode()), font=fontB1)
    draw.text((((WW-w)/2)+120, 110),        str(VENKU.decode()),  font=fontB1, fill='#00EFFF')

    _, _, w, h = draw.textbbox((0, 0), 'teplota (°C)', font=fontR1)
    draw.text(((WW-w)/2, 50),       'teplota (°C)', font=fontR1, fill="white")
    _, _, w, h = draw.textbbox((0, 0), 'vlhkost (%)', font=fontR1)
    draw.text((((WW-w)/2)+120, 50),       'vlhkost (%)',  font=fontR1, fill="white")
    _, _, w, h = draw.textbbox((0, 0), 'venku (°C)', font=fontR1)
    draw.text((((WW-w)/2), 130),       'venku (°C)',  font=fontR1, fill="white")
    print (('{0:0.1f} ˚C'.format(temperature)))
    print (('{0:0.1f} %'.format(humidity)))

    #pocasi dnes
    _, _, w, h = draw.textbbox((0, 0), 'počasí dnes:', font=fontR1)
    draw.text (((WW-w)/2, 175), 'počasí dnes:', font = fontR1, fill = 'white')
    _, _, w, h = draw.textbbox((0, 0), str(DNES_STAV.decode()), font=fontR1)    
    draw.text (((WW-w)/2, 217), str(DNES_STAV.decode()), font = fontR1, fill = '#00EFFF')
    _, _, w, h = draw.textbbox((0, 0), str(DNES_TEPLOTA.decode().rstrip()+ ' °C'), font=fontB3)    
    draw.text (((WW-w)/2, 195), str(DNES_TEPLOTA.decode().rstrip()+ ' °C'), font = fontB3, fill = '#00EFFF')
    print(str(current_time) + ' ' + '/home/TFT/GIF/'+str(DNES_IKONA.decode()).rstrip()+'.gif')
    draw.pasteimage(os.path.join(r'/home/TFT/GIF/'+str(DNES_IKONA.decode()).rstrip()+'.gif'), (25, 240))
    #pocasi zitra
    _, _, w, h = draw.textbbox((0, 0), 'počasí zítra:', font=fontR1)
    draw.text ((((WW-w)/2)+120, 175), 'počasí zítra:', font = fontR1, fill = 'white')
    _, _, w, h = draw.textbbox((0, 0), str(ZITRA_STAV.decode()), font=fontR1)    
    draw.text ((((WW-w)/2)+120, 217), str(ZITRA_STAV.decode()), font = fontR1, fill = '#00EFFF')
    _, _, w, h = draw.textbbox((0, 0), str(ZITRA_TEPLOTA.decode().rstrip()+ ' °C'), font=fontB3)    
    draw.text ((((WW-w)/2)+120, 195), str(ZITRA_TEPLOTA.decode().rstrip()+ ' °C'), font = fontB3, fill = '#00EFFF')
    draw.pasteimage('/home/TFT/GIF/'+str(ZITRA_IKONA.decode()).rstrip()+'.gif', (145, 240))

    TFT.display()
    

# (x, y) == left, top
