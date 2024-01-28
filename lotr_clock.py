# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import math
import string
import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
import datetime as dt
from pathlib import Path


# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=240,
    height=240,
    x_offset=0,
    y_offset=80,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 180

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True


text = ''
with (Path(__file__).parent / "files/lotr.txt").open() as file:
    text = file.read()

font_file = "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf"
clock_font = ImageFont.truetype(font_file, math.floor(height / 3))
text_font = ImageFont.truetype(font_file, math.floor(height / 6))

text_char_width, text_char_height = draw.textsize('a', font=text_font)
clock_char_width, clock_char_height = draw.textsize('a', font=clock_font)

ideal_clock_height = math.floor(height / 6)
ideal_clock_width = math.floor(width / 7)

while clock_char_height >= ideal_clock_height and clock_char_width >= ideal_clock_width:
    clock_font = ImageFont.truetype(font_file, clock_font.size - 1)
    clock_char_width, clock_char_height = draw.textsize('a', font=clock_font)

clock_x = (width / 2) - ((clock_char_width * 5) / 2)
clock_y = (height / 3) - (clock_char_height / 2)

char_on_screen = int(math.ceil(width / text_char_width))
text = text.rjust(len(text) + char_on_screen - 1)
text_y = (height * (5/6)) - (text_char_height / 2)

now = dt.datetime.now()
journey_start = dt.datetime(now.year,9,23,8,0,0)
journey_end = dt.datetime(now.year+1,3,25,20,0,0)

# for testing
journey_total = (journey_end - journey_start)
journey_start = now
journey_end = journey_start + dt.timedelta(seconds=journey_total.total_seconds())

journey_seconds = (journey_end - journey_start).total_seconds()

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Enumerate characters and draw them.
    now = dt.datetime.now()
    draw.text((clock_x, clock_y), now.strftime("%I:%M"), font=clock_font, fill=255)

    if journey_start <= now <= journey_end:
        journey_delta_seconds = (now - journey_start).total_seconds()
        ch_offset_frac, ch_offset = math.modf(len(text) * (journey_delta_seconds / journey_seconds))
        px_offset = text_char_width * ch_offset_frac * -1
        
        draw.text((px_offset, text_y), text[math.floor(ch_offset):math.floor((ch_offset + char_on_screen) + 1)], font=text_font, fill=255)

    # Display image.
    disp.image(image, rotation)
    time.sleep(0.1)