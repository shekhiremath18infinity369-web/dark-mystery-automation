"""Upload at most one Short per scheduled slot from the two Drive folders.

Required GitHub Actions secrets:
  YOUTUBE_TOKEN_JSON: OAuth token JSON file contents for the YouTube Google account.
  GOOGLE_DRIVE_FOLDER_IDS: JSON array of the two source Drive folder IDs.

The upload is public, category Autos & Vehicles, and file size is capped at 100 MB.
After successful upload, the Drive file is moved into the UPLOADED folder.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
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
CATEGORY_ID = "2"  # Autos & Vehicles
TOKEN_FILE = Path("/tmp/youtube_token.json")


def fail(message):
    print(f"::error::{message}")
    raise SystemExit(1)


def get_services():
    raw = os.environ.get("YOUTUBE_TOKEN_JSON", "").strip()
    if not raw:
        fail("Missing YOUTUBE_TOKEN_JSON secret.")
    try:
        token_data = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"YOUTUBE_TOKEN_JSON is not valid JSON: {exc}")
    TOKEN_FILE.write_text(json.dumps(token_data), encoding="utf-8")
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
        print("::warning::OAuth access token refreshed. Update the repository secret with refreshed token JSON if refresh tokens rotate.")
    if not creds.valid:
        fail("YouTube/Drive OAuth token is invalid or expired. Re-authorize it.")
    return (
        build("drive", "v3", credentials=creds, cache_discovery=False),
        build("youtube", "v3", credentials=creds, cache_discovery=False),
    )


def get_folder_ids():
    raw = os.environ.get("GOOGLE_DRIVE_FOLDER_IDS", "").strip()
    try:
        ids = json.loads(raw)
    except Exception:
        fail("GOOGLE_DRIVE_FOLDER_IDS must be a JSON array of folder IDs.")
    if not isinstance(ids, list) or len(ids) != 2 or not all(isinstance(x, str) and x for x in ids):
        fail("GOOGLE_DRIVE_FOLDER_IDS must contain exactly the two source folder IDs.")
    return ids


def list_next_video(drive, folder_ids):
    candidates = []
    for folder_id in folder_ids:
        response = drive.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id,name,mimeType,size,createdTime,webViewLink)",
            pageSize=100,
            orderBy="createdTime asc",
        ).execute()
        for item in response.get("files", []):
            name = item.get("name", "")
            if item.get("mimeType") != "video/mp4" and not name.lower().endswith((".mp4", ".mov", ".m4v")):
                continue
            size = int(item.get("size") or 0)
            if size <= 0:
                continue
            if size > MAX_BYTES:
                print(f"Skipping over 100 MB: {name} ({size / 1048576:.1f} MB)")
                continue
            candidates.append((item.get("createdTime", ""), item, folder_id))
    candidates.sort(key=lambda row: row[0])
    return candidates[0] if candidates else None


def clean_title(filename):
    stem = Path(filename).stem
    stem = re.sub(r"[_-]+", " ", stem)
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem[:95] or "Amazing Dashcam Moment"


def main():
    folder_ids = get_folder_ids()
    drive, youtube = get_services()
    candidate = list_next_video(drive, folder_ids)
    if not candidate:
        print("No eligible video found in either source folder. Nothing uploaded.")
        return

    _, item, source_folder = candidate
    file_id = item["id"]
    filename = item["name"]
    print(f"Selected: {filename} ({int(item['size']) / 1048576:.1f} MB)")
    local = Path("/tmp") / re.sub(r"[^A-Za-z0-9._-]", "_", filename)
    request = drive.files().get_media(fileId=file_id)
    with local.open("wb") as output:
        downloader = MediaIoBaseDownload(output, request, chunksize=8 * 1024 * 1024)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Downloaded {int(status.progress() * 100)}%")
    if local.stat().st_size > MAX_BYTES:
        fail("Downloaded file is larger than the configured 100 MB limit.")

    title = clean_title(filename)
    description = (
        "Watch till the end!\n\n"
        + HASHTAGS
    )
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "categoryId": CATEGORY_ID,
            "tags": [tag.lstrip("#") for tag in HASHTAGS.split() if tag.startswith("#")][:6],
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(local), mimetype="video/*", resumable=True, chunksize=8 * 1024 * 1024)
    uploaded = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    ).execute()
    video_id = uploaded.get("id")
    if not video_id:
        fail("YouTube upload response did not contain a video ID.")
    print(f"Uploaded publicly: https://www.youtube.com/watch?v={video_id}")

    # Move only after confirmed successful YouTube upload.
    drive.files().update(
        fileId=file_id,
        addParents=os.environ["UPLOADED_FOLDER_ID"],
        removeParents=source_folder,
        fields="id,parents",
    ).execute()
    print(f"Moved Drive source file into UPLOADED: {filename}")


if __name__ == "__main__":
    main()
