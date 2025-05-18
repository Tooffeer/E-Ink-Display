import os
import time
from pathlib import Path
from PIL import Image

from waveshare_epd import epd2in13_V4

# Init display
epd = epd2in13_V4.EPD()
epd.init(epd.FULL_UPDATE)
epd.Clear(0xFF)

# Image directory and settings
IMAGE_FOLDER = Path("images")
DISPLAY_TIME = 10  # seconds each image

# Get all image files
image_files = sorted(IMAGE_FOLDER.glob("*.bmp"))

if not image_files:
    print("No BMP images found in images/")
    exit(1)

try:
    while True:  # Loop through images endlessly
        for img_path in image_files:
            image = Image.open(img_path).convert("1")  # Convert to 1-bit for display
            image = image.resize((epd.height, epd.width))  # Rotate if needed

            # If image is oriented vertically, rotate
            if image.size[0] != epd.height:
                image = image.rotate(90, expand=True)

            epd.display(epd.getbuffer(image))
            time.sleep(DISPLAY_TIME)

except KeyboardInterrupt:
    print("Interrupted by user, clearing and sleeping...")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)
    epd.sleep()
