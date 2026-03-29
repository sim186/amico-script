FROM python:3.11-slim

WORKDIR /app

# ffmpeg: required by faster-whisper to decode mp3/m4a/ogg/flac
# libsndfile1: required by pyannote.audio
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY frontend/ ./frontend/

RUN mkdir -p uploads

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
