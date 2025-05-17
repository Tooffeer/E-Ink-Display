import os
import time
from io import BytesIO
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests

# Import the correct e-paper display driver
from waveshare_epd import epd2in13_V4

# Initialize the display
epd = epd2in13_V4.EPD()
epd.init()
epd.Clear(0xFF)

# Load environment variables
load_dotenv()

# Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="user-read-playback-state"
))

# Font
font = ImageFont.load_default()

while True:
    try:
        # Create a blank white image
        img = Image.new('1', (epd.height, epd.width), 255)
        draw = ImageDraw.Draw(img)

        # Fetch current track info
        current = sp.current_playback()

        if current and current.get('is_playing'):
            track = current['item']
            song_name = track['name']
            artist_name = track['artists'][0]['name']
            album_url = track['album']['images'][0]['url']
            progress_ms = current['progress_ms']
            duration_ms = track['duration_ms']
        else:
            song_name = "Nothing Playing"
            artist_name = ""
            album_url = None
            progress_ms = 0
            duration_ms = 1  # Prevent division by zero

        # Draw album art if available
        if album_url:
            try:
                r = requests.get(album_url)
                cover = Image.open(BytesIO(r.content)).convert('L')
                cover = cover.resize((64, 64))
                cover = cover.convert('1', dither=Image.FLOYDSTEINBERG)
                img.paste(cover, (10, 20))
            except Exception as e:
                print("Album art error:", e)

        # Draw song info text
        text_x = 80
        draw.text((text_x, 25), song_name, font=font, fill=0)
        draw.text((text_x, 45), artist_name, font=font, fill=0)

        # Draw progress bar
        bar_x = 10
        bar_y = 100
        bar_w = 230
        bar_h = 10

        percent = progress_ms / duration_ms
        fill_w = int(bar_w * percent)

        draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], outline=0, fill=255)
        draw.rectangle([bar_x, bar_y, bar_x + fill_w, bar_y + bar_h], outline=0, fill=0)

        # Display image using partial update
        epd.displayPartial(epd.getbuffer(img))

    except Exception as e:
        print("Error:", e)

    time.sleep(10)  # Update every 10 seconds
