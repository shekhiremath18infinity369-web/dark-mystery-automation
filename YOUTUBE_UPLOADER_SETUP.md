# dark-mystery-automation

This repository currently creates a dark mystery short. The YouTube uploader workflow is separate from that generator.

## Scheduled YouTube Shorts uploader

The workflow `.github/workflows/youtube-shorts.yml` runs daily at **5:30 PM and 9:30 PM India time** (12:00 and 16:00 UTC). Each run uploads at most one eligible MP4/MOV/M4V from the two configured Google Drive source folders.

- Public visibility
- Category: Autos & Vehicles
- Title: derived from the Drive filename
- Maximum input size: 100 MB
- On successful upload only, the source file is moved to the Drive `UPLOADED` folder
- Files are considered oldest first across both source folders

### Required account setup (not possible through the GitHub repository connector)

Create these two **Actions repository secrets** in Settings → Secrets and variables → Actions:

1. `GOOGLE_DRIVE_FOLDER_IDS` — exact value:
   `["1auXZb0xGArTJEKMWr88YzIEdMeMT6LVd","1hgkc_ADkyffzkM7UKNUoN58q7l5zHc7b"]`
2. `YOUTUBE_TOKEN_JSON` — OAuth authorized-user token JSON with Drive and YouTube upload scopes. It must be authorized for the Google account that owns or can edit both source folders and the UPLOADED folder, and the channel that should receive the videos.

Do not commit OAuth credentials or token JSON into this repository. The OAuth token JSON must contain a refresh token. YouTube Data API uploads may be subject to API quota, verification and project restrictions. Keep the repository public only if you are comfortable with its source code being public; secrets remain encrypted in Actions Secrets.

### Important

- GitHub scheduled runs are best-effort and can start late; the cron times are targets, not exact guarantees.
- This workflow selects one video per slot and will not upload the same item again after it is moved into UPLOADED.
- The six tags are included as requested: `#CarCrash #Dashcam #GTA #Viral #USA #Shorts`. Keep only tags that accurately describe each video.
- The action does not guarantee 100 MB if the codec/container causes the API to reject the upload; this is a local input-file cap.
