#!/usr/bin/python3

# -*- coding: utf-8 -*-
from datetime import datetime
from time import sleep
from lib_tft24T import TFT24T
import RPi.GPIO as GPIO
import spidev
import subprocess
from PIL import Image, ImageDraw, ImageFont
import locale
import os
import psutil
import Adafruit_DHT

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

locale.setlocale(locale.LC_TIME, 'cs_CZ.UTF-8')

DHTsensor = Adafruit_DHT.DHT22
DHTpin = 4
DC, RST, LED = 25, 24, 23
TFT = TFT24T(spidev.SpiDev(), GPIO, landscape=False)
TFT.initLCD(DC, RST, LED)
draw = TFT.draw()

margin_x_figure = 40
margin_x_bar = 110
bar_width = 125
bar_width_full = 127
bar_height = 8
bar_margin_top = 0
fontR3 = ImageFont.truetype(r'/home/pi/FONTS/Ubuntu-R.ttf', 11)

def get_temp():
    temp = float(subprocess.getoutput("vcgencmd measure_temp").split("=")[1].split("'")[0])
    return temp

def get_cpu():
    return psutil.cpu_percent()

def get_mem():
    return psutil.virtual_memory().percent

def format_percent(percent):
    return "%5.1f" % (percent)

def draw_text2(draw, margin_x, line_num, text):
    draw.text((margin_x, margin_y_line[line_num]), text, font=fontR3, fill="white")

def draw_bar(draw, line_num, percent):
    top_left_y = margin_y_line[line_num] + bar_margin_top
    draw.rectangle((margin_x_bar, top_left_y, margin_x_bar + bar_width, top_left_y + bar_height), outline="#a5a5a5")
    draw.rectangle((margin_x_bar, top_left_y, margin_x_bar + bar_width * percent / 100, top_left_y + bar_height), fill="white")

def draw_bar_full(draw, line_num):
    top_left_y = margin_y_line[line_num] + bar_margin_top
    draw.rectangle((margin_x_bar, top_left_y, margin_x_bar + bar_width_full, top_left_y + bar_height), fill="white")
    draw.text((65, top_left_y - 2), "100 %", font=fontR3, fill="black")

def stats():
    temp = get_temp()
    draw_text2(draw, 0, 0, "Temp")
    draw_text2(draw, margin_x_figure, 0, "%s'C" % (format_percent(temp)))
    if temp < 100:
        #draw_bar(draw, margin_x_figure, 1, "%s %%" % (format_percent(temp)))
        draw_bar(draw, 0, temp)
    else:
        draw_bar_full(draw, 1)

    cpu = get_cpu()
    draw_text2(draw, 0, 1, "CPU")
    if cpu < 100:
        draw_text2(draw, margin_x_figure, 1, "%s %%" % (format_percent(cpu)))
        draw_bar(draw, 1, cpu)
    else:
        draw_bar_full(draw, 1)

    mem = get_mem()
    draw_text2(draw, 0, 2, "Mem")
    if mem < 100:
        draw_text2(draw, margin_x_figure, 2, "%s %%" % (format_percent(mem)))
        draw_bar(draw, 2, mem)
    else:
        draw_bar_full(draw, 2)

font_paths = {
    "B1": '/home/pi/FONTS/Ubuntu-B.ttf',
    "B2": '/home/pi/FONTS/Ubuntu-B.ttf',
    "B3": '/home/pi/FONTS/Ubuntu-B.ttf',
    "R1": '/home/pi/FONTS/Ubuntu-R.ttf',
    "R2": '/home/pi/FONTS/Ubuntu-R.ttf',
    "R3": '/home/pi/FONTS/Ubuntu-R.ttf',
}

font_sizes = {
    "B1": 50,
    "B2": 30,
    "B3": 20,
    "R1": 15,
    "R2": 20,
    "R3": 11,
}

fonts = {k: ImageFont.truetype(v, font_sizes[k]) for k, v in font_paths.items()}


def read_sensor_data():
    VENKU_cmd = 'cat /home/pi/tmpfs/teplota_ext | cut -d\  -f1'
    VENKU = subprocess.check_output(VENKU_cmd, shell=True).strip().decode()
    humidity, temperature = Adafruit_DHT.read_retry(DHTsensor, DHTpin)

    commands = {
        "ZITRA_TEPLOTA": "jq .daily[1].temp.day /home/pi/tmpfs/pocasi-onecall.json",
        "ZITRA_STAV": "jq .daily[1].weather[0].description /home/pi/tmpfs/pocasi-onecall.json | tr -d '\"'",
        "ZITRA_IKONA": "jq .daily[1].weather[0].icon /home/pi/tmpfs/pocasi-onecall.json | tr -d '\"'",
        "ZITRA_VITR": "jq .daily[1].wind_speed /home/pi/tmpfs/pocasi-onecall.json",
        "DNES_TEPLOTA": "jq .daily[0].temp.day /home/pi/tmpfs/pocasi-onecall.json",
        "DNES_STAV": "jq .daily[0].weather[0].description /home/pi/tmpfs/pocasi-onecall.json | tr -d '\"'",
        "DNES_IKONA": "jq .daily[0].weather[0].icon /home/pi/tmpfs/pocasi-onecall.json | tr -d '\"'",
        "DNES_VITR": "jq .daily[0].wind_speed /home/pi/tmpfs/pocasi-onecall.json",
    }

    results = {key: subprocess.check_output(cmd, shell=True).strip().decode() for key, cmd in commands.items()}

    return VENKU, humidity, temperature, results

def draw_text(draw, text, position, font, fill="white"):
    _, _, w, h = draw.textbbox((0, 0), text, font=font)
    x, y = position
    draw.text((x - w // 2, y), text, font=font, fill=fill)


TFT.backlite(1)
II, PP = 0, 0
width, height = 240, 320
margin_y_line = [280, 290, 300]
VENKU, humidity, temperature, weather_data = read_sensor_data()

def cleanup():
    draw.rectangle((0,0,240,320), outline=0, fill=0)
    TFT.backlite(0)
    TFT.display()
try:
    while True:
        if II == 30:
            VENKU, humidity, temperature, weather_data = read_sensor_data()
            II = 0
        else:
            II += 1

        if PP == 3600:
            VENKU, humidity, temperature, weather_data = read_sensor_data()
            PP = 0
        else:
            PP += 1

        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        stats()

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime('%d. %B %Y')

        draw_text(draw, current_date, (width // 2, 0), fonts["R1"])
        draw_text(draw, current_time, (width // 2, 10), fonts["B2"])

        if temperature is not None:
            draw_text(draw, f"{temperature:.1f}", (60, 57), fonts["B1"], fill='#00EFFF')
        else:
            print('chyba čtení teploty')

        if humidity is not None:
            draw_text(draw, f"{humidity:.1f}", (180, 57), fonts["B1"], fill='#00EFFF')
        else:
            print('chyba čtení vlhkosti')

        draw_text(draw, 'teplota (°C)', (60, 50), fonts["R1"])
        draw_text(draw, 'vlhkost (%)', (180, 50), fonts["R1"])

        draw_text(draw, 'počasí dnes:', (60, 120), fonts["R1"])
        draw_text(draw, weather_data["DNES_STAV"], (60, 155), fonts["R1"], fill='#00EFFF')
        draw_text(draw, f"{weather_data['DNES_TEPLOTA']} °C", (60, 135), fonts["B3"], fill='#00EFFF')
        draw_text(draw, f"vítr: {weather_data['DNES_VITR']} m/s", (60, 170), fonts["R1"], fill='#00EFFF')
        draw.pasteimage(os.path.join(r'/home/pi/TFT/GIF/' + weather_data["DNES_IKONA"] + '.gif'), (25, 190))

        draw_text(draw, 'počasí zítra:', (180, 120), fonts["R1"])
        draw_text(draw, weather_data["ZITRA_STAV"], (180, 155), fonts["R1"], fill='#00EFFF')
        draw_text(draw, f"{weather_data['ZITRA_TEPLOTA']} °C", (180, 135), fonts["B3"], fill='#00EFFF')
        draw_text(draw, f"vítr: {weather_data['ZITRA_VITR']} m/s", (180, 170), fonts["R1"], fill='#00EFFF')
        draw.pasteimage(os.path.join(r'/home/pi/TFT/GIF/' + weather_data["ZITRA_IKONA"] + '.gif'), (145, 190))

        TFT.display()
        sleep(1)  # Add a short delay to reduce CPU usage
except KeyboardInterrupt:
    print("Skript byl přerušen")
finally:
    cleanup()
    print("Displej byl vypnut")
