# AmicoScript — Features & Notes

This document summarizes AmicoScript features, optional components, and tips.

Features

- Local-first transcription: audio is processed on your machine; nothing is sent to the cloud.
- Model choices: supports Whisper models from tiny → large-v3 (selectable in UI).
- Exports: JSON, SRT, TXT, and Markdown.
- Speaker diarization: optional `pyannote` integration for speaker labels.
- Web UI: single-file frontend (`frontend/index.html`) — no build step.

Speaker diarization (detailed)

1. Create or log in to a Hugging Face account.
2. Accept gated model licenses for both `pyannote/speaker-diarization-3.1` and `pyannote/segmentation-3.0` on huggingface.co.
3. Create a read-scoped access token (`hf_...`) at https://huggingface.co/settings/tokens.
4. In AmicoScript settings, enable Speaker diarization and paste your token. The token is saved locally at `~/.amicoscript/settings.json`.

Packaging notes

- Standalone builds use PyInstaller via `python package.py` and will bundle required Python packages.
- Diarization in standalone builds requires including `pyannote.audio` package data (the packaging script already attempts to collect these files).

Developer tips

- To run locally: use a Python 3.10+ venv and `pip install -r backend/requirements.txt`, then `python run.py`.
- The backend serves the frontend and API on `http://localhost:8002` by default.
- Temporary audio files are cleaned up automatically (about 1 hour).

Troubleshooting

- If diarization fails with `403 Client Error: Cannot access gated repo`, confirm both gated model pages were accepted.
- If packaging complains about missing telemetry/config files from `pyannote`, rebuild with the packaging script after ensuring `pyannote` data is available.

For more, see the main README and CHANGELOG.md.
