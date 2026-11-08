
import os
import subprocess

def generate_voice(text, output="output/voice.wav"):
    os.makedirs("output", exist_ok=True)

    subprocess.run([
        "piper",
        "--model",
        "en_US-lessac-medium",
        "--output_file",
        output
    ], input=text, text=True, check=True)

    return output

if __name__ == "__main__":
    with open("output/story.txt", encoding="utf-8") as f:
        story = f.read()

    generate_voice(story)
    print("Voice generated successfully!")
  
