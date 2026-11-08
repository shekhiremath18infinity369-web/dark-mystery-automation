
import os
import subprocess
from PIL import Image, ImageDraw, ImageFilter

os.makedirs("output", exist_ok=True)

def create_visual():
    width, height = 1080, 1920

    image = Image.new("RGB", (width, height))
    pixels = image.load()

    for y in range(height):
        for x in range(width):
            distance = ((x - 540)**2 + (y - 900)**2)**0.5
            shade = max(3, int(25 - distance / 65))
            pixels[x, y] = (shade, shade + 2, shade + 5)

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (330, 650, 750, 1500),
        fill=(8, 10, 13)
    )

    draw.rectangle(
        (450, 800, 630, 1500),
        fill=(2, 3, 5)
    )

    image = image.filter(ImageFilter.GaussianBlur(3))
    image.save("output/scene.png")

    subprocess.run([
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", "output/scene.png",
        "-t", "45",
        "-r", "24",
        "-pix_fmt", "yuv420p",
        "output/visual.mp4"
    ], check=True)

    print("Dark mystery visual created!")

if __name__ == "__main__":
    create_visual()
  
