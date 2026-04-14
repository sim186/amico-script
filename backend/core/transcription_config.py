"""Typed configuration model for Whisper transcription options."""
from pydantic import BaseModel, Field


class TranscriptionConfig(BaseModel):
    """Runtime transcription options accepted per job."""

    model: str = Field(default="small")
    language: str = Field(default="")
    diarize: bool = Field(default=False)
    colab_url: str = Field(default="")
    hf_token: str = Field(default="")

    num_speakers: int | None = Field(default=None)
    min_speakers: int | None = Field(default=None)
    max_speakers: int | None = Field(default=None)

    compute_type: str = Field(default="int8")
    device: str = Field(default="auto")
    device_index: int = Field(default=0)

    vad_filter: bool = Field(default=True)
    word_timestamps: bool = Field(default=False)
    beam_size: int = Field(default=5)
    best_of: int = Field(default=5)
    force_normalize_audio: bool = Field(default=False)
