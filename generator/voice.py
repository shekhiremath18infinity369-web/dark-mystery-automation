
import os
import subprocess

os.makedirs("output", exist_ok=True)

def generate_voice():
    with open("output/story.txt", encoding="utf-8") as f:
        story = f.read()

    subprocess.run(
        [
            "python", "-m", "piper",
            "--model", "en_US-lessac-medium",
            "--output_file", "output/voice.wav",
            "--", story
        ],
        check=True
    )

    print("Horror narration generated!")

if __name__ == "__main__":
    generate_voice()
