import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
import datetime as dt
from pathlib import Path
import math

class Display:
    """Manages displaying the Clock and the text to the screen.  Call update to update the display"""

    def __init__(self):
        self.disp = self._create_display()

        # Create blank image for drawing.
        # Make sure to create image with mode 'RGB' for full color.
        self.height = self.disp.width  # we swap height/width to rotate it to landscape!
        self.width = self.disp.height
        self.image = Image.new("RGB", (self.width, self.height))
        self.rotation = 180

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

        self._clear_display()
        self._display_image()

        self.text = ''
        with (Path(__file__).parent / "../files/lotr.txt").open() as file:
            self.text = file.read()

        font_file = "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf"
        self.clock_font = ImageFont.truetype(font_file, math.floor(self.height / 3))
        self.text_font = ImageFont.truetype(font_file, math.floor(self.height / 6))

        self.text_char_width, text_char_height = self.draw.textsize('a', font=self.text_font)
        clock_char_width, clock_char_height = self.draw.textsize('a', font=self.clock_font)

        ideal_clock_height = math.floor(self.height / 6)
        ideal_clock_width = math.floor(self.width / 7)

        while clock_char_height >= ideal_clock_height and clock_char_width >= ideal_clock_width:
            self.clock_font = ImageFont.truetype(font_file, self.clock_font.size - 1)
            clock_char_width, clock_char_height = self.draw.textsize('a', font=self.clock_font)

        self.clock_x = (self.width / 2) - ((clock_char_width * 5) / 2)
        self.clock_y = (self.height / 3) - (clock_char_height / 2)

        self.char_on_screen = int(math.ceil(self.width / self.text_char_width))
        self.text = self.text.rjust(len(self.text) + self.char_on_screen - 1)
        self.text_y = (self.height * (5/6)) - (text_char_height / 2)

        now = dt.datetime.now()
        self.journey_start = dt.datetime(now.year,9,23,8,0,0)
        self.journey_end = dt.datetime(now.year+1,3,25,20,0,0)

        # for testing
        journey_total = (self.journey_end - self.journey_start)
        self.journey_start = now
        self.journey_end = self.journey_start + dt.timedelta(seconds=journey_total.total_seconds())

        self.journey_seconds = (self.journey_end - self.journey_start).total_seconds()

    def update(self):
        self._clear_display()

        # Enumerate characters and draw them.
        now = dt.datetime.now()
        self.draw.text((self.clock_x, self.clock_y), now.strftime("%I:%M"), font=self.clock_font, fill=255)

        if self.journey_start <= now <= self.journey_end:
            journey_delta_seconds = (now - self.journey_start).total_seconds()
            ch_offset_frac, ch_offset = math.modf(len(self.text) * (journey_delta_seconds / self.journey_seconds))
            px_offset = self.text_char_width * ch_offset_frac * -1
            
            self.draw.text((px_offset, self.text_y), self.text[math.floor(ch_offset):math.floor((ch_offset + self.char_on_screen) + 1)], font=self.text_font, fill=255)

        self._display_image()

    def _create_display(self):
        # Configuration for CS and DC pins
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

        # Turn on the backlight
        backlight = digitalio.DigitalInOut(board.D22)
        backlight.switch_to_output()
        backlight.value = True
        
        return disp

    def _clear_display(self):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=(0, 0, 0))
        

    def _display_image(self):
        self.disp.image(self.image, self.rotation)