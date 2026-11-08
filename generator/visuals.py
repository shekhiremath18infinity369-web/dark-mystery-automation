
import os
import json
import subprocess
from PIL import Image, ImageDraw, ImageFilter

os.makedirs("output/scenes", exist_ok=True)

with open("output/story.json", encoding="utf-8") as f:
    story = json.load(f)

def make_scene(index, description):
    w, h = 1080, 1920
    image = Image.new("RGB", (w, h))
    pixels = image.load()

    for y in range(h):
        for x in range(w):
            distance = ((x-w/2)**2 + (y-h/2)**2)**0.5
            shade = max(2, int(24-distance/80))
            pixels[x, y] = (shade, shade+2, shade+5)

    draw = ImageDraw.Draw(image)

    # Mysterious doorway and silhouette
    draw.rectangle((280, 550, 800, 1600), fill=(7, 9, 12))
    draw.rectangle((410, 700, 670, 1600), fill=(1, 2, 4))

    # Scene-specific visual variation
    if index % 2 == 0:
        draw.ellipse((440, 750, 640, 950), fill=(13, 17, 21))
    else:
        draw.rectangle((100, 1200, 980, 1250), fill=(9, 12, 16))

    image = image.filter(ImageFilter.GaussianBlur(2))
    image.save(f"output/scenes/scene_{index}.png")

for i, description in enumerate(story["scenes"], 1):
    make_scene(i, description)

    subprocess.run([
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", f"output/scenes/scene_{i}.png",
        "-t", "7.5",
        "-r", "24",
        "-vf", "format=yuv420p",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        f"output/scenes/clip_{i}.mp4"
    ], check=True)

with open("output/concat.txt", "w") as f:
    for i in range(1, 7):
        path = os.path.abspath(
            f"output/scenes/clip_{i}.mp4"
        )
        f.write(f"file '{path}'\n")

subprocess.run([
    "ffmpeg", "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", "output/concat.txt",
    "-c", "copy",
    "output/visual.mp4"
], check=True)

print("Six visual scenes completed!")
