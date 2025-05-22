import os
import time
import requests
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from io import BytesIO
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from waveshare_epd import epd2in13_V4

# Initilize display
epd = epd2in13_V4.EPD()
epd.init()
epd.Clear()

# Get parameters from .env file
load_dotenv()

# Authenticate Spotify requests
scope = "user-read-currently-playing user-read-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope=scope
))

# Draws album cover
def draw_album_cover(track):
    # Get album cover 
    album_url = track["item"]["album"]["images"][0]["url"] # Get the first image url from album images
    response = requests.get(album_url)
    album_cover = Image.open(BytesIO(response.content))

    # Resize album cover and dither
    album_cover = album_cover.resize((122, 122))
    album_cover = album_cover.convert('1')  # 1-bit dithered

    # Draw image
    img.paste(album_cover, (0, 0))

# Wrap text if needed (basic manual wrap)
def wrap_text(draw, text, font, max_width):
    lines = []
    words = text.split()
    line = ""

    for word in words:
        test_line = f"{line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)  # returns (x0, y0, x1, y1)
        w = bbox[2] - bbox[0]  # calculate width from bbox
        if w <= max_width:
            line = test_line
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

previous = None # Previous track
idle = False

# Main loop 
while True:
    # Get the current track
    current = sp.current_playback()

    # Create a blank image
    img = Image.new("1", (250, 122), color=1)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", size=14) # Arial on windows #font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", size=14) # Arial on mac

    if current:
        idle = False
        
        # Check if track is the same as the previous track
        if previous is not None and current["item"]["name"] == previous["item"]["name"]:
            print("Same song", current["item"]["name"])
        elif current and current.get("item"):
            print("New song", current["item"]["name"])

            # Draw album cover
            draw_album_cover(current)

            # Get song title and artist
            song_name = current["item"]["name"]
            artists = current["item"]["artists"]

            # Text box on right side (x=130 to end)
            x_text = 130
            y_text = 10
            max_width = 130

            # Wrap text
            track_lines  = wrap_text(draw, song_name, font, max_width)
            #artist_lines = wrap_text(draw, artists, font, max_width)

            # Draw wrapped text
            for line in track_lines[:3]:  # limit to 3 lines
                draw.text((x_text, y_text), line, font=font, fill=0)
                y_text += 12

            # Draw image
            #img.show()
            epd.display(epd.getbuffer(img))
            epd.sleep()
    else:
        print("No song")
        draw.text((10, 10), "No song is currently playing.", font=font, fill=0)

        if not idle:
            idle = True
            #img.show()
            epd.display(epd.getbuffer(img))
            epd.sleep()

    # Update previous
    previous = current

    time.sleep(10)

