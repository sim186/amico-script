"""AmicoScript — path and storage configuration.

All modules should import STORAGE_ROOT, DB_PATH, and RECORDINGS_DIR from here
to ensure a single source of truth for where data is persisted.

Portable mode: set AMICOSCRIPT_PORTABLE=1 (or "true"/"yes") to store the DB
and all recordings in ./amicoscript-data/ relative to the current working
directory.  This makes the app fully self-contained (USB stick use case).
"""
import os
from pathlib import Path

PORTABLE_MODE: bool = os.environ.get("AMICOSCRIPT_PORTABLE", "").lower() in (
    "1", "true", "yes"
)

if PORTABLE_MODE:
    STORAGE_ROOT = Path.cwd() / "amicoscript-data"
else:
    STORAGE_ROOT = Path.home() / ".amicoscript" / "data"

DB_PATH = STORAGE_ROOT / "amicoscript.db"

RECORDINGS_DIR = STORAGE_ROOT / "recordings"


def ensure_storage_dirs() -> None:
    """Create storage directories. Called at app startup, not at import time."""
    STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
