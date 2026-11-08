
import os
import subprocess

os.makedirs("output", exist_ok=True)

with open("output/story.txt", encoding="utf-8") as f:
    narration = f.read()

subprocess.run(
    [
        "piper",
        "--model", "en_US-lessac-medium",
        "--output_file", "output/voice.wav"
    ],
    input=narration,
    text=True,
    check=True
)

print("English horror narration created!")
