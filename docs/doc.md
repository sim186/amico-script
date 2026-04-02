# AmicoScript Documentation

## Overview

AmicoScript is a local-first audio transcription tool powered by Whisper.

It provides:

- audio transcription
- optional speaker diarization
- transcript management and search
- export in multiple formats

---

## Getting Started (Flow)

Typical usage:

1. Upload an audio file
2. Start a transcription job
3. Monitor progress
4. Retrieve the result
5. Export or edit the transcript

---

## API Reference

### Models

**GET /api/models**

Returns available Whisper models.

---

### Settings

**GET /api/settings**  
Retrieve saved settings (e.g., Hugging Face token)

**POST /api/settings**  
Save settings

---

### Transcription

**POST /api/transcribe**

Upload an audio file and start a transcription job.

Response:

```json
{
  "job_id": "string"
}
```

---

### Job Progress

**GET /api/jobs/{id}/stream**

Server-Sent Events (SSE) stream for real-time progress updates.

---

### Cancel Job

**POST /api/jobs/{id}/cancel**

Cancels a running transcription job.

---

### Job Result

**GET /api/jobs/{id}/result**

Returns the full transcription result in JSON format.

---

### Export

**GET /api/jobs/{id}/export/{fmt}**

Download transcript in one of the following formats:

- json
- srt
- txt
- md

---

## Speaker Diarization Setup

Speaker diarization uses `pyannote` and requires:

1. A Hugging Face account
2. Acceptance of model licenses
3. A valid `hf_` token

Add your token via the settings endpoint or UI.

---

## Architecture

- Backend: Python + FastAPI
- Frontend: Static HTML served by FastAPI
- Processing: Background threads for transcription

### Storage

- In-memory job state
- Temporary audio files (auto-deleted after ~1 hour)

---

## GPU Support

To enable GPU acceleration:

1. Use a CUDA-enabled PyTorch base image
2. Update the Dockerfile accordingly
3. Enable GPU support in docker-compose

---

## Notes

- All processing is local
- No audio data is uploaded externally
- Performance depends on hardware and selected model
