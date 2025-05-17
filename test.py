from waveshare_epd import epd2in13_V2
from PIL import Image, ImageDraw, ImageFont
import time

epd = epd2in13_V2.EPD()
epd.init(epd.FULL_UPDATE)
epd.Clear(0xFF) 

img = Image.new('1', (250, 122), 255)
draw = ImageDraw.Draw(img)
font = ImageFont.load_default()

draw.text((10, 10), "Hello World!", font = font, fill = 0)

epd.display(epd.getbuffer(img))
time.sleep(2)
epd.sleep()
