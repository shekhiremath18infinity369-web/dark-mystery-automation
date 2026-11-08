
import subprocess
import os

os.makedirs("output", exist_ok=True)

subprocess.run([
    "ffmpeg", "-y",
    "-i", "output/visual.mp4",
    "-i", "output/voice.wav",
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-vf",
    "scale=1080:1920:force_original_aspect_ratio=increase,"
    "crop=1080:1920,format=yuv420p",
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-crf", "24",
    "-c:a", "aac",
    "-b:a", "128k",
    "-shortest",
    "-movflags", "+faststart",
    "output/horror_short.mp4"
], check=True)

print("FINAL VIDEO CREATED!")
