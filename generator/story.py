
import os
import json
import urllib.request

API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-2.5-flash"

prompt = """
Create an original 45-second dark mystery horror story.

Return JSON with:
title: short title
narration: 90-110 words of English narration
scenes: exactly 6 cinematic visual descriptions

Start with a strong hook.
Use psychological horror and an unexpected twist.
Do not copy existing stories.
"""

url = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL}:generateContent?key={API_KEY}"
)

payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {
        "responseMimeType": "application/json",
        "temperature": 0.8
    }
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"}
)

with urllib.request.urlopen(req, timeout=90) as response:
    result = json.loads(response.read())

story = json.loads(
    result["candidates"][0]["content"]["parts"][0]["text"]
)

assert len(story["scenes"]) == 6
assert story["narration"].strip()

os.makedirs("output", exist_ok=True)

with open("output/story.json", "w", encoding="utf-8") as f:
    json.dump(story, f, indent=2)

with open("output/story.txt", "w", encoding="utf-8") as f:
    f.write(story["narration"])

print("Story generated:", story["title"])
