
import os
import json
import urllib.request

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing")

MODEL = "gemini-3.8-flash"

prompt = """
You are a professional dark mystery and horror storyteller.

Create one original horror story for YouTube Shorts
and Instagram Reels.

Requirements:
- 90 to 110 words.
- Powerful hook in the first 3 seconds.
- Dark, mysterious atmosphere.
- Psychological horror.
- Unexpected ending.
- Six clearly separated visual scenes.
- Natural English narration.
- Include a title.

Return only the finished story and scene descriptions.
"""

url = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL}:generateContent?key={API_KEY}"
)

payload = {
    "contents": [{
        "parts": [{"text": prompt}]
    }],
    "generationConfig": {
        "temperature": 0.9,
        "maxOutputTokens": 1200
    }
}

request = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(request, timeout=60) as response:
    result = json.loads(response.read().decode("utf-8"))

story = result["candidates"][0]["content"]["parts"][0]["text"]

os.makedirs("output", exist_ok=True)

with open("output/story.txt", "w", encoding="utf-8") as file:
    file.write(story)

print("Horror story generated successfully!")
print(story)
