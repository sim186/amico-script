"""Structured logging utilities for backend workers."""
import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Any


class _JsonFormatter(logging.Formatter):
    """Render logs as a compact JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "job_id"):
            payload["job_id"] = record.job_id
        if record.exc_info:
            payload["traceback"] = "".join(traceback.format_exception(*record.exc_info))
        return json.dumps(payload, ensure_ascii=True)


_LOGGING_INITIALIZED = False


def _init_logging() -> None:
    global _LOGGING_INITIALIZED
    if _LOGGING_INITIALIZED:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(_JsonFormatter())

    root = logging.getLogger("amicoscript")
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    root.propagate = False

    _LOGGING_INITIALIZED = True


def get_logger(name: str) -> logging.Logger:
    """Return a configured JSON logger under the amicoscript namespace."""
    _init_logging()
    return logging.getLogger(name)
