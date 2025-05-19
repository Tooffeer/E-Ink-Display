import os
import time
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from waveshare_epd import epd2in13_V4

load_dotenv()

scope = "user-read-currently-playing user-read-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope=scope,
    open_browser=False
))

epd = epd2in13_V4.EPD()
epd.init()
epd.Clear()

def get_album_cover_image(sp):
    current = sp.current_playback()
    if current and current.get("item"):
        album_url = current["item"]["album"]["images"][0]["url"]
        response = requests.get(album_url)
        img = Image.open(BytesIO(response.content))
        # Resize album cover to 122x122 (left side of display)
        img = img.resize((122, 122), Image.ANTIALIAS)
        img_bw = img.convert('1')  # 1-bit dithered
        return img_bw
    return None

def draw_display(epd, sp):
    # Create blank white image for full display (250x122)
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    current = sp.current_playback()
    if current and current.get("item"):
        # Draw album art on left side
        album_img = get_album_cover_image(sp)
        if album_img:
            image.paste(album_img, (0, 0))

        # Prepare song and artist text
        track = current["item"]["name"]
        artist = ", ".join([a["name"] for a in current["item"]["artists"]])

        # Text box on right side (x=130 to end)
        x_text = 130
        y_text = 10
        max_width = epd.height - x_text  # ~120 pixels

        # Wrap text if needed (basic manual wrap)
        def wrap_text(text, font, max_width):
            lines = []
            words = text.split()
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                if font.getsize(test_line)[0] <= max_width:
                    line = test_line
                else:
                    lines.append(line)
                    line = word
            lines.append(line)
            return lines

        track_lines = wrap_text(track, font, max_width)
        artist_lines = wrap_text(artist, font, max_width)

        # Draw song title
        for line in track_lines[:3]:  # limit to 3 lines
            draw.text((x_text, y_text), line, font=font, fill=0)
            y_text += 12

        y_text += 4  # small gap between song and artist

        # Draw artist
        for line in artist_lines[:3]:
            draw.text((x_text, y_text), line, font=font, fill=0)
            y_text += 12

    else:
        # No song playing, just text centered
        text = "Nothing Playing"
        w, h = draw.textsize(text, font=font)
        draw.text(((epd.height - w) // 2, (epd.width - h) // 2), text, font=font, fill=0)

    epd.display(epd.getbuffer(image))

try:
    while True:
        draw_display(epd, sp)
        time.sleep(10)
except KeyboardInterrupt:
    print("Exiting and clearing display")
    epd.init()
    epd.Clear()
    epd.sleep()
