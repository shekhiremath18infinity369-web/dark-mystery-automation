import os
import wave
from pathlib import Path
from piper import PiperVoice

MODEL_PATH = Path("models/en_US-lessac-medium.onnx")
TEXT_PATH = Path("output/story.txt")
OUTPUT_PATH = Path("output/voice.wav")

def main():
    if not TEXT_PATH.exists():
        raise FileNotFoundError("Missing output/story.txt; run story.py first.")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Missing Piper voice model: {MODEL_PATH}. "
            "Check the workflow's Piper download step."
        )

    narration = TEXT_PATH.read_text(encoding="utf-8").strip()
    if not narration:
        raise ValueError("Story narration is empty.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    voice = PiperVoice.load(str(MODEL_PATH))
    with wave.open(str(OUTPUT_PATH), "wb") as wav_file:
        voice.synthesize_wav(narration, wav_file)

    if not OUTPUT_PATH.exists() or OUTPUT_PATH.stat().st_size < 1000:
        raise RuntimeError("Piper did not create a valid narration WAV.")
    print(f"Voice generated: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
