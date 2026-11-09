# AI Video Studio Integration Plan

This branch adds an integration plan for an AI video-production workflow. It does not copy or redistribute OpenMontage source code.

## Upstream project
- Project: OpenMontage
- Official repository: https://github.com/OpenMontageInc/OpenMontage
- License shown by GitHub: GNU Affero General Public License v3.0 (AGPL-3.0)
- Review the upstream LICENSE and comply with its network-use, notice, source-distribution, and attribution obligations before modifying, hosting, or distributing a derivative.

## Current repository modules
The existing project already contains:
- generator/story.py — story/script generation
- generator/visuals.py — visual asset generation
- generator/voice.py — voice generation
- generator/editor.py — editing/rendering
- .github/workflows/daily-video.yml — scheduled automation

These files are not modified by this integration branch.

## Integration architecture
1. Keep this repository's current story, visuals, voice, and editor modules intact.
2. Treat OpenMontage as an optional external production engine installed from its official repository.
3. Add an adapter layer that invokes a configured local OpenMontage CLI/workflow only after the operator approves the script, assets, and estimated costs.
4. Keep provider credentials in environment variables or a secret manager. Never commit .env, API keys, access tokens, or generated credentials.
5. Save output media outside Git (for example, a configured render directory or object storage). Do not commit large video files.
6. Provide a web/mobile interface as a separate frontend and a server-side job API; Android phones should control remote jobs rather than execute GPU-heavy inference locally.

## Planned workflow
Prompt -> script -> scene list -> visual assets -> narration -> assembly -> captions -> preview -> approved render -> MP4 export.

## Provider and cost controls
- Free/local tools can cover some narration, stock-footage, and assembly tasks.
- Text-to-video/image-to-video generation usually depends on an installed local model or an external provider.
- No claim of unlimited free generation is made.
- Require a per-job cost estimate and explicit approval before calling paid generation APIs.
- Add timeouts, retry limits, cancellation, and job status tracking.

## First validation milestone
1. Run the existing repository tests and inspect its current scheduled workflow.
2. Install OpenMontage separately following its current official README.
3. Create a short test project using only local/free components.
4. Confirm narration, media assembly, captions, and MP4 export.
5. Add one provider adapter at a time, with cost caps and error handling.

## What this branch does not claim
- It is not a complete OpenMontage fork.
- It has not deployed a public web service.
- It has not been executed on the user's Android phone.
- Video generation has not been tested in this GitHub-only environment.
