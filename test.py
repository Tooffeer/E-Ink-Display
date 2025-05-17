from PIL import Image, ImageDraw, ImageFont

img = Image.new('1', (250, 122), 255)
draw = ImageDraw.Draw(img)
font = ImageFont.load_default()

draw.text((10, 10), "Hello World!", font = font, fill = 0)

img.show()