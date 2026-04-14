"""Shared mutable state for the AmicoScript backend.

Centralising all globals here prevents circular imports between pipeline.py
and main.py while keeping the worker thread and the FastAPI event loop
decoupled.
"""
import asyncio
from typing import Optional

# ---------------------------------------------------------------------------
# Job store
# ---------------------------------------------------------------------------

# job_id -> job dict
jobs: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# Whisper model cache
# ---------------------------------------------------------------------------

_cached_model = None
_cached_model_name: Optional[str] = None
_cached_model_device: Optional[str] = None
_cached_model_key: Optional[tuple] = None

# ---------------------------------------------------------------------------
# Background job queue
# ---------------------------------------------------------------------------

JOB_QUEUE: asyncio.Queue[str] = asyncio.Queue()

# ---------------------------------------------------------------------------
# asyncio event loop — set by main.py at startup
# ---------------------------------------------------------------------------

# Kept for compatibility while older code paths are migrated.
event_loop: Optional[asyncio.AbstractEventLoop] = None
