# Scheduled YouTube Shorts uploader

Workflow: `.github/workflows/youtube-shorts.yml`

It is configured for 5:30 PM and 9:30 PM India time (12:00 and 16:00 UTC), with one upload per slot. It scans the two source folders oldest-first, accepts MP4/MOV/M4V files up to 100 MB, derives the title from the filename, sets visibility to Public and category to Autos & Vehicles, then moves the successfully uploaded Drive file to `UPLOADED`.

## Required setup

The GitHub connector cannot create repository secrets or authorize Google OAuth. Add these in GitHub → this repository → Settings → Secrets and variables → Actions → New repository secret:

**GOOGLE_DRIVE_FOLDER_IDS**
```json
["1auXZb0xGArTJEKMWr88YzIEdMeMT6LVd","1hgkc_ADkyffzkM7UKNUoN58q7l5zHc7b"]
```

**YOUTUBE_TOKEN_JSON**

Paste the complete contents of a Google OAuth authorized-user token JSON file. It must include a refresh token and have both Drive access and YouTube upload scopes. Authorize the Google account that can access both source folders and the UPLOADED folder, and the YouTube channel you want to publish to.

Never commit credentials to the repository or paste them into chat. The GitHub workflow uses encrypted Actions secrets.

## Limitations

- Scheduled workflows are best-effort and may start late.
- YouTube API upload quota, Google Cloud project verification/restrictions, OAuth consent-screen testing status, and Drive access can prevent uploads.
- Six tags are included as requested: `#CarCrash #Dashcam #GTA #Viral #USA #Shorts`. Remove tags that do not accurately describe a particular video.
- An uploaded video is moved only after YouTube confirms a successful upload. If moving it fails, it could be selected again on a later run; check YouTube Studio and the UPLOADED folder before retrying manually.
- This setup is not an unlimited guarantee: GitHub Actions, Drive, and YouTube each apply usage limits and policies.
