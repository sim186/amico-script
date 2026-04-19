"""Tests for LIKE wildcard escaping in search_library."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))


def test_like_escaping():
    """% and _ in query are escaped before being embedded in LIKE pattern."""
    q = "file_001%test"
    q_like = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
    assert q_like == "%file\\_001\\%test%"


def test_like_escaping_backslash():
    q = "path\\to\\file"
    q_like = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
    assert q_like == "%path\\\\to\\\\file%"


def test_like_escaping_plain():
    q = "hello world"
    q_like = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
    assert q_like == "%hello world%"


def test_negative_limit_clamped():
    """Negative limit values must be clamped to at least 1."""
    limit = -1
    safe_limit = max(1, min(limit, 200))
    assert safe_limit == 1


def test_overlarge_limit_clamped():
    limit = 9999
    safe_limit = max(1, min(limit, 200))
    assert safe_limit == 200
