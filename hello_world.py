from waveshare_epd import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont
import time

try:
    # Initialize the display
    epd = epd2in13_V4.EPD()
    epd.init()
    epd.Clear(0xFF)  # Clear the screen to white

    # Create a blank image for drawing
    image = Image.new('1', (epd.height, epd.width), 255)  # 1-bit mode, white background
    draw = ImageDraw.Draw(image)

    # Load a font and draw text
    font = ImageFont.load_default()
    draw.text((10, 10), "Hello World", font=font, fill=0)  # fill=0 = black text

    # Send image to display
    epd.display(epd.getbuffer(image))
    time.sleep(2)

    # Put display to sleep to save power
    epd.sleep()

except Exception as e:
    print("Error:", e)
