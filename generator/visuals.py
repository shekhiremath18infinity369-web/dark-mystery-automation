
import os
import json
import subprocess
from PIL import Image, ImageDraw, ImageFilter

os.makedirs("output/scenes", exist_ok=True)

with open("output/story.json", encoding="utf-8") as f:
    story = json.load(f)

def create_scene(index, description):
    width, height = 1080, 1920

    image = Image.new("RGB", (width, height))
    pixels = image.load()

    for y in range(height):
        for x in range(width):
            distance = ((x - 540)**2 + (y - 850)**2)**0.5
            shade = max(3, int(24 - distance / 75))
            pixels[x, y] = (shade, shade + 2, shade + 5)

    draw = ImageDraw.Draw(image)

    # Atmospheric silhouette
    draw.rectangle(
        (300, 600, 780, 1600),
        fill=(5, 7, 10)
    )

    draw.rectangle(
        (430, 780, 650, 1600),
        fill=(1, 2, 4)
    )

    image = image.filter(ImageFilter.GaussianBlur(2))

    image.save(f"output/scenes/scene_{index}.png")

for index, description in enumerate(story["scenes"], 1):
    create_scene(index, description)
    print(f"Scene {index} created: {description}")

# Combine the six scenes into one vertical video.
for index in range(1, 7):
    subprocess.run([
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", f"output/scenes/scene_{index}.png",
        "-t", "7.5",
        "-r", "24",
        "-pix_fmt", "yuv420p",
        f"output/scenes/clip_{index}.mp4"
    ], check=True)

with open("output/concat.txt", "w") as f:
    for index in range(1, 7):
        f.write(f"file 'scenes/clip_{index}.mp4'\n")

subprocess.run([
    "ffmpeg", "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", "output/concat.txt",
    "-c", "copy",
    "output/visual.mp4"
], check=True)

print("Six-scene video created!")
