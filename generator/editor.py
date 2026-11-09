import subprocess
from pathlib import Path

OUTPUT = Path("output")
VISUAL = OUTPUT / "visual.mp4"
VOICE = OUTPUT / "voice.wav"
FINAL = OUTPUT / "horror_short.mp4"

def main():
    for path in (VISUAL, VOICE):
        if not path.exists() or path.stat().st_size == 0:
            raise FileNotFoundError(f"Required input missing or empty: {path}")

    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(VISUAL),
        "-i", str(VOICE),
        "-map", "0:v:0", "-map", "1:a:0",
        "-vf", "scale=1080:1920,setsar=1,format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "25",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", "-movflags", "+faststart",
        str(FINAL)
    ], check=True)

    if not FINAL.exists() or FINAL.stat().st_size < 10000:
        raise RuntimeError("Final MP4 was not created correctly.")

    probe = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(FINAL)
    ], check=True, capture_output=True, text=True)

    duration = float(probe.stdout.strip())
    if duration < 10:
        raise RuntimeError(f"Final video is unexpectedly short: {duration:.1f}s")

    print(f"Final video created: {FINAL} ({duration:.1f} seconds)")

if __name__ == "__main__":
    main()
