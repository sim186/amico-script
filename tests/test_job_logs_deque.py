"""Tests for job log deque — O(1) truncation, max 1000 entries."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from collections import deque
import state
from api.routes.transcription import get_job_logs
from core.job_helpers import _append_job_log


def _make_job(job_id: str) -> dict:
    job = {
        "id": job_id,
        "status": "queued",
        "logs": [],
        "sse_queue": None,
    }
    state.jobs[job_id] = job
    return job


def test_logs_capped_at_1000():
    job_id = "test-deque-cap"
    _make_job(job_id)
    for i in range(1200):
        _append_job_log(job_id, "INFO", f"msg {i}")
    logs = state.jobs[job_id]["logs"]
    assert len(logs) <= 1000, f"Expected ≤1000 entries, got {len(logs)}"


def test_logs_use_deque():
    job_id = "test-deque-type"
    _make_job(job_id)
    _append_job_log(job_id, "INFO", "hello")
    assert isinstance(state.jobs[job_id]["logs"], deque)


def test_logs_preserve_order():
    job_id = "test-deque-order"
    _make_job(job_id)
    for i in range(5):
        _append_job_log(job_id, "INFO", f"msg {i}")
    messages = [e["message"] for e in state.jobs[job_id]["logs"]]
    assert messages == [f"msg {i}" for i in range(5)]


def test_get_job_logs_handles_deque():
    job_id = "test-deque-api"
    state.jobs[job_id] = {
        "id": job_id,
        "status": "done",
        "progress": 1.0,
        "message": "Complete",
        "logs": deque(
            [
                {"ts": 1.0, "level": "INFO", "message": "msg 1"},
                {"ts": 2.0, "level": "INFO", "message": "msg 2"},
            ],
            maxlen=1000,
        ),
    }

    result = get_job_logs(job_id, limit=1)

    assert result["logs"] == [{"ts": 2.0, "level": "INFO", "message": "msg 2"}]
