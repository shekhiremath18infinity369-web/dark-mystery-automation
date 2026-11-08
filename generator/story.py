
import os
import json
import urllib.request

API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-2.5-flash"

prompt = """
Create an original 45-second dark mystery horror story.

Rules:
- English narration.
- 90 to 110 words.
- Powerful first 3-second hook.
- Psychological horror.
- Unexpected twist ending.
- Six cinematic scene descriptions.

Return valid JSON with:
{
  "title": "Story title",
  "narration": "Complete narration",
  "scenes": [
    "Scene 1 description",
    "Scene 2 description",
    "Scene 3 description",
    "Scene 4 description",
    "Scene 5 description",
    "Scene 6 description"
  ]
}
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
        "responseMimeType": "application/json",
        "temperature": 0.9
    }
}

request = urllib.request.Request(
    url,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"}
)

with urllib.request.urlopen(request, timeout=60) as response:
    result = json.loads(response.read())

story = json.loads(
    result["candidates"][0]["content"]["parts"][0]["text"]
)

os.makedirs("output", exist_ok=True)

with open("output/story.txt", "w", encoding="utf-8") as f:
    f.write(story["narration"])

with open("output/story.json", "w", encoding="utf-8") as f:
    json.dump(story, f, indent=2)

print("Story generated:", story["title"])
