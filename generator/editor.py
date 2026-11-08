
import os
import subprocess

os.makedirs("output", exist_ok=True)

def create_video():
    command = [
        "ffmpeg", "-y",
        "-i", "output/visual.mp4",
        "-i", "output/voice.wav",
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,format=yuv420p",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "24",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        "output/horror_short.mp4"
    ]

    subprocess.run(command, check=True)

    print("FINAL HORROR SHORT CREATED!")

if __name__ == "__main__":
    create_video()
    
