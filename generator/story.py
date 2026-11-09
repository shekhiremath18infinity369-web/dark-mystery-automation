import json
import os
import urllib.error
import urllib.request
from pathlib import Path

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = "gemini-3.5-flash-lite"

PROMPT = """
Write one original dark mystery / psychological horror story for a 45-second
vertical video.

Return ONLY valid JSON with exactly these keys:
{
  "title": "short clickable title",
  "narration": "90 to 110 words of natural spoken English",
  "scenes": [
    "visual description for scene 1",
    "visual description for scene 2",
    "visual description for scene 3",
    "visual description for scene 4",
    "visual description for scene 5",
    "visual description for scene 6"
  ]
}

The first sentence must hook viewers immediately. Build suspense and finish
with a surprising but understandable twist. Make the six visual descriptions
cinematic, specific, and consistent with the same story. Do not include gore,
instructions for harm, markdown fences, or commentary.
"""

def main():
    if not API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY repository secret.")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{MODEL}:generateContent"
    )
    payload = {
        "contents": [{"parts": [{"text": PROMPT}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.85,
            "maxOutputTokens": 1800
        }
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Gemini API returned HTTP {exc.code}: {details[:1200]}"
        ) from exc

    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(
            f"Gemini returned no candidates: {data.get('promptFeedback', data)}"
        )

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts).strip()
    if not text:
        raise RuntimeError("Gemini returned an empty story.")

    story = json.loads(text)
    title = str(story.get("title", "")).strip()
    narration = str(story.get("narration", "")).strip()
    scenes = story.get("scenes")

    if not title or not narration or not isinstance(scenes, list) or len(scenes) != 6:
        raise ValueError("Gemini output must contain title, narration, and exactly six scenes.")

    story["title"] = title
    story["narration"] = narration
    story["scenes"] = [str(scene).strip() for scene in scenes]

    Path("output").mkdir(exist_ok=True)
    Path("output/story.json").write_text(
        json.dumps(story, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    Path("output/story.txt").write_text(narration, encoding="utf-8")
    print(f"Generated story: {title}")

if __name__ == "__main__":
    main()
