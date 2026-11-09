# OpenMontage Setup (Reference)

Official upstream: https://github.com/OpenMontageInc/OpenMontage

This project is a separate dependency. The current GitHub connection has read-only permission to upstream, so install or fork it through GitHub's own UI/your local machine.

## Before installing
- Read the current upstream README and LICENSE.
- Use a computer, cloud VM, or hosted development environment; a phone browser alone is not a suitable environment for running the full Python/Node/FFmpeg stack.
- Do not paste API keys into chat, source files, issues, or commits.
- Start with free/local pipelines and set provider spending limits.

## Typical upstream setup
Follow the exact, current commands in the upstream README. Do not assume commands in older tutorials are still current.

## Connect later
Once the upstream engine runs, implement a small adapter in this repository that:
- submits a job,
- polls job status,
- records logs and generated file paths,
- handles failure and cancellation,
- exports the final MP4 to configured storage.

Do not invoke paid provider APIs without showing the estimated cost and obtaining approval.
