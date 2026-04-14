"""Audio conversion helpers for transcription and diarization."""
import shutil
import subprocess
from pathlib import Path

import state

from core.job_helpers import _append_job_log


def _normalize_audio(
    job_id: str,
    input_path: str,
    purpose: str,
    force: bool = False,
) -> str:
    """Normalize audio via ffmpeg to mono 16kHz WAV.

    When force=False and purpose is transcription, WAV/FLAC sources are reused.
    """
    ext = Path(input_path).suffix.lower()
    if not force and purpose == "transcription" and ext in {".wav", ".flac"}:
        return input_path

    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        _append_job_log(
            job_id,
            "WARN",
            "ffmpeg not found in PATH; using original file",
        )
        return input_path

    suffix = "norm" if purpose == "transcription" else "diar"
    normalized_path = str(Path(input_path).with_name(f"{Path(input_path).stem}_{suffix}.wav"))
    cmd = [
        ffmpeg_bin,
        "-y",
        "-v",
        "error",
        "-i",
        input_path,
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-sample_fmt",
        "s16",
        normalized_path,
    ]

    try:
        _append_job_log(job_id, "INFO", f"Normalizing audio for {purpose} (mono/16k PCM)")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=False)
        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            _append_job_log(
                job_id,
                "WARN",
                f"ffmpeg normalization failed: {stderr or f'code {proc.returncode}'}",
            )
            return input_path

        job = state.jobs.get(job_id)
        if job is not None:
            job.setdefault("temp_files", []).append(normalized_path)

        return normalized_path
    except Exception as exc:
        _append_job_log(job_id, "WARN", f"ffmpeg normalization exception: {exc}")
        return input_path


def _convert_audio_for_transcription(job_id: str, input_path: str, force: bool = False) -> str:
    """Compatibility wrapper around _normalize_audio for transcription."""
    return _normalize_audio(job_id, input_path, purpose="transcription", force=force)


def _convert_audio_for_diarization(job_id: str, input_path: str, force: bool = True) -> str:
    """Compatibility wrapper around _normalize_audio for diarization."""
    return _normalize_audio(job_id, input_path, purpose="diarization", force=force)
