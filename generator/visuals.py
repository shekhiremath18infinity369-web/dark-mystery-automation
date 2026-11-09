import json
import math
import random
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

WIDTH, HEIGHT = 1080, 1920
OUTPUT = Path("output")
SCENES_DIR = OUTPUT / "scenes"

def make_scene(index, description):
    rng = random.Random(index * 197)
    image = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    # Smooth dark blue-grey vertical gradient.
    for y in range(HEIGHT):
        t = y / HEIGHT
        value = int(5 + 17 * (1 - t))
        draw.line((0, y, WIDTH, y), fill=(value, value + 2, value + 7))

    # Distant moon / dim light source.
    moon_x = 780 if index % 2 else 270
    moon_y = 340 + (index % 3) * 65
    draw.ellipse(
        (moon_x - 105, moon_y - 105, moon_x + 105, moon_y + 105),
        fill=(38, 43, 50)
    )

    # Fog banks.
    fog = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    fog_draw = ImageDraw.Draw(fog)
    for _ in range(34):
        x = rng.randint(-180, WIDTH - 80)
        y = rng.randint(650, 1650)
        rx = rng.randint(100, 300)
        ry = rng.randint(18, 70)
        fog_draw.ellipse(
            (x, y, x + rx, y + ry),
            fill=(125, 135, 148, rng.randint(5, 16))
        )
    fog = fog.filter(ImageFilter.GaussianBlur(38))
    image = Image.alpha_composite(image.convert("RGBA"), fog)
    draw = ImageDraw.Draw(image)

    # Different silhouettes so each scene is not an identical frame.
    if index in (1, 4):
        # Narrow corridor and open doorway.
        draw.rectangle((180, 520, 900, 1700), fill=(7, 9, 13, 255))
        draw.polygon([(180, 520), (420, 700), (420, 1700), (180, 1700)],
                     fill=(17, 19, 24, 255))
        draw.polygon([(900, 520), (660, 700), (660, 1700), (900, 1700)],
                     fill=(12, 14, 19, 255))
        draw.rectangle((425, 710, 655, 1700), fill=(1, 2, 4, 255))
    elif index in (2, 5):
        # Lonely house with lit window.
        draw.polygon([(190, 1050), (540, 720), (900, 1050)], fill=(5, 7, 10, 255))
        draw.rectangle((260, 1040, 820, 1690), fill=(5, 7, 10, 255))
        draw.rectangle((430, 1190, 650, 1690), fill=(1, 2, 4, 255))
        draw.rectangle((680, 1150, 760, 1280), fill=(43, 40, 31, 255))
    else:
        # Trees and a small distant figure in a forest.
        for x in range(-50, WIDTH + 100, 145):
            top = rng.randint(440, 850)
            draw.polygon(
                [(x, 1700), (x + 65, top), (x + 135, 1700)],
                fill=(3, 5, 8, 255)
            )
        figure_x = 535 + rng.randint(-90, 90)
        draw.ellipse((figure_x - 34, 1110, figure_x + 34, 1178),
                     fill=(1, 2, 3, 255))
        draw.polygon(
            [(figure_x - 55, 1170), (figure_x + 55, 1170),
             (figure_x + 90, 1600), (figure_x - 90, 1600)],
            fill=(1, 2, 3, 255)
        )

    image = image.convert("RGB").filter(ImageFilter.GaussianBlur(1.3))
    target = SCENES_DIR / f"scene_{index}.png"
    image.save(target, quality=92)
    return target

def main():
    story_file = OUTPUT / "story.json"
    if not story_file.exists():
        raise FileNotFoundError("Missing output/story.json; run story.py first.")

    story = json.loads(story_file.read_text(encoding="utf-8"))
    scenes = story.get("scenes", [])
    if len(scenes) != 6:
        raise ValueError("Expected exactly six scene descriptions.")

    SCENES_DIR.mkdir(parents=True, exist_ok=True)
    concat_file = OUTPUT / "concat.txt"
    clip_paths = []

    for index, description in enumerate(scenes, start=1):
        image_path = make_scene(index, description)
        clip_path = SCENES_DIR / f"clip_{index}.mp4"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-loop", "1", "-framerate", "24", "-i", str(image_path),
            "-t", "7.5", "-r", "24",
            "-vf", "scale=1080:1920,format=yuv420p",
            "-an", "-c:v", "libx264", "-preset", "ultrafast",
            "-crf", "28", str(clip_path)
        ], check=True)
        clip_paths.append(clip_path.resolve())

    concat_file.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in clip_paths),
        encoding="utf-8"
    )

    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-an", "-c:v", "libx264", "-preset", "ultrafast",
        "-crf", "27", "-pix_fmt", "yuv420p",
        str(OUTPUT / "visual.mp4")
    ], check=True)

    print("Six-scene vertical visual video created.")

if __name__ == "__main__":
    main()
