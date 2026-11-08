
import os
import subprocess

OUTPUT = "output"
VIDEO = f"{OUTPUT}/horror_short.mp4"
VOICE = f"{OUTPUT}/voice.wav"
VISUALS = f"{OUTPUT}/visual.mp4"

os.makedirs(OUTPUT, exist_ok=True)

def create_video():
    required = [VOICE, VISUALS]

    for file in required:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Missing file: {file}")

    command = [
        "ffmpeg", "-y",
        "-i", VISUALS,
        "-i", VOICE,
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
        VIDEO
    ]

    subprocess.run(command, check=True)
    print("Horror video created:", VIDEO)

if __name__ == "__main__":
    create_video()
  
