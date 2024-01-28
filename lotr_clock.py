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

from display.display import Display

display = Display()

while True:
    display.update()
    time.sleep(0.1)