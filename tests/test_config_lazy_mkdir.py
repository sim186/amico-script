"""Tests that config.py does NOT create directories at import time."""
import sys
import importlib
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_config_import_does_not_mkdir(tmp_path, monkeypatch):
    """Importing config must not create any directories on disk."""
    mkdir_calls = []

    real_Path = Path

    class SpyPath(type(tmp_path)):
        def mkdir(self, **kwargs):
            mkdir_calls.append(str(self))
            super().mkdir(**kwargs)

    # Remove cached module so it re-imports
    if "config" in sys.modules:
        del sys.modules["config"]
    if "backend.config" in sys.modules:
        del sys.modules["backend.config"]

    # Patch Path.mkdir to track calls
    with patch.object(Path, "mkdir", side_effect=lambda **kw: mkdir_calls.append("mkdir")) as m:
        import config  # noqa: F401

    assert len(mkdir_calls) == 0, f"mkdir called {len(mkdir_calls)} times during import: {mkdir_calls}"

    # Re-add to sys.modules for other tests
    if "config" not in sys.modules:
        import config  # noqa: F811


def test_ensure_storage_dirs_creates_dirs(tmp_path, monkeypatch):
    """ensure_storage_dirs() must create the required directories."""
    import config

    monkeypatch.setattr(config, "STORAGE_ROOT", tmp_path / "data")
    monkeypatch.setattr(config, "RECORDINGS_DIR", tmp_path / "data" / "recordings")

    config.ensure_storage_dirs()

    assert (tmp_path / "data").exists()
    assert (tmp_path / "data" / "recordings").exists()
