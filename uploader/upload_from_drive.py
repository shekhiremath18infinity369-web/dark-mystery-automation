"""Upload at most one Short per scheduled slot from the two Drive folders.

Secrets:
  YOUTUBE_TOKEN_JSON: OAuth token JSON authorized for Drive and YouTube upload.
  GOOGLE_DRIVE_FOLDER_IDS: JSON array containing the two source folder IDs.
"""
import json
import os
import re
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/youtube.upload",
]
MAX_BYTES = int(os.getenv("MAX_VIDEO_MB", "100")) * 1024 * 1024
HASHTAGS = os.getenv("HASHTAGS", "#Shorts").strip()
TOKEN_FILE = Path("/tmp/youtube_token.json")


def fail(message):
    print(f"::error::{message}")
    raise SystemExit(1)


def get_services():
    raw = os.environ.get("YOUTUBE_TOKEN_JSON", "").strip()
    if not raw:
        fail("Missing YOUTUBE_TOKEN_JSON repository secret.")
    try:
        token_data = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"YOUTUBE_TOKEN_JSON is not valid JSON: {exc}")
    TOKEN_FILE.write_text(json.dumps(token_data), encoding="utf-8")
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    if not creds.valid:
        fail("OAuth token is invalid/expired or has no refresh token. Re-authorize Drive + YouTube upload scopes.")
    return (
        build("drive", "v3", credentials=creds, cache_discovery=False),
        build("youtube", "v3", credentials=creds, cache_discovery=False),
    )


def get_folder_ids():
    try:
        ids = json.loads(os.environ["GOOGLE_DRIVE_FOLDER_IDS"])
    except Exception:
        fail("GOOGLE_DRIVE_FOLDER_IDS must be a JSON array of two source folder IDs.")
    if not isinstance(ids, list) or len(ids) != 2 or not all(isinstance(x, str) and x for x in ids):
        fail("GOOGLE_DRIVE_FOLDER_IDS must contain exactly two folder IDs.")
    return ids


def list_next_video(drive, folder_ids):
    candidates = []
    for folder_id in folder_ids:
        page_token = None
        while True:
            response = drive.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="nextPageToken,files(id,name,mimeType,size,createdTime)",
                pageSize=100,
                orderBy="createdTime asc",
                pageToken=page_token,
            ).execute()
            for item in response.get("files", []):
                name = item.get("name", "")
                if not name.lower().endswith((".mp4", ".mov", ".m4v")):
                    continue
                size = int(item.get("size") or 0)
                if size <= 0 or size > MAX_BYTES:
                    if size > MAX_BYTES:
                        print(f"Skipping over 100 MB: {name} ({size / 1048576:.1f} MB)")
                    continue
                candidates.append((item.get("createdTime", ""), item, folder_id))
            page_token = response.get("nextPageToken")
            if not page_token:
                break
    candidates.sort(key=lambda row: row[0])
    return candidates[0] if candidates else None


def clean_title(filename):
    title = re.sub(r"[_-]+", " ", Path(filename).stem)
    title = re.sub(r"\s+", " ", title).strip()
    return title[:95] or "Amazing Dashcam Moment"


def main():
    folder_ids = get_folder_ids()
    drive, youtube = get_services()
    candidate = list_next_video(drive, folder_ids)
    if not candidate:
        print("No eligible video found in either source folder.")
        return

    _, item, source_folder = candidate
    file_id, filename = item["id"], item["name"]
    local = Path("/tmp") / re.sub(r"[^A-Za-z0-9._-]", "_", filename)

    with local.open("wb") as output:
        downloader = MediaIoBaseDownload(
            output, drive.files().get_media(fileId=file_id), chunksize=8 * 1024 * 1024
        )
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Downloaded {int(status.progress() * 100)}%")

    if local.stat().st_size > MAX_BYTES:
        fail("Downloaded file exceeds the configured 100 MB maximum.")

    hashtags = [tag for tag in HASHTAGS.split() if tag.startswith("#")]
    body = {
        "snippet": {
            "title": clean_title(filename),
            "description": "Watch till the end!\n\n" + " ".join(hashtags),
            "categoryId": "2",
            "tags": [tag[1:] for tag in hashtags[:6]],
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(local), mimetype="video/*", resumable=True, chunksize=8 * 1024 * 1024)
    uploaded = youtube.videos().insert(
        part="snippet,status", body=body, media_body=media
    ).execute()
    video_id = uploaded.get("id")
    if not video_id:
        fail("YouTube API did not return a video ID; leaving Drive file in source folder.")
    print(f"Published: https://www.youtube.com/watch?v={video_id}")

    drive.files().update(
        fileId=file_id,
        addParents=os.environ["UPLOADED_FOLDER_ID"],
        removeParents=source_folder,
        fields="id,parents",
    ).execute()
    print(f"Moved uploaded file to UPLOADED: {filename}")


if __name__ == "__main__":
    main()
