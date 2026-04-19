"""Tests for _build_transcription_options int parsing."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import pytest
from api.routes.transcription import _build_transcription_options


def _build(**overrides):
    defaults = dict(
        model="small", language="", diarize="false", colab_url="",
        num_speakers="", min_speakers="", max_speakers="",
        compute_type="int8", device="auto", device_index="0",
        vad_filter="true", word_timestamps="false",
        beam_size="5", best_of="5", force_normalize_audio="false",
    )
    defaults.update(overrides)
    return _build_transcription_options(**defaults)


def test_valid_positive_ints():
    opts = _build(num_speakers="2", beam_size="3", best_of="4")
    assert opts["num_speakers"] == 2
    assert opts["beam_size"] == 3
    assert opts["best_of"] == 4


def test_negative_values_become_default():
    opts = _build(num_speakers="-1", beam_size="-1", best_of="-1")
    assert opts["num_speakers"] is None
    assert opts["beam_size"] == 5
    assert opts["best_of"] == 5


def test_non_numeric_becomes_default():
    opts = _build(num_speakers="abc", beam_size="xyz")
    assert opts["num_speakers"] is None
    assert opts["beam_size"] == 5


def test_empty_string_becomes_default():
    opts = _build(num_speakers="", min_speakers="", max_speakers="")
    assert opts["num_speakers"] is None
    assert opts["min_speakers"] is None
    assert opts["max_speakers"] is None


def test_zero_becomes_default_for_beam():
    opts = _build(beam_size="0", best_of="0")
    assert opts["beam_size"] == 5
    assert opts["best_of"] == 5
