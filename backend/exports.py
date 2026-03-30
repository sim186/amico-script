"""Export formatters for transcription results.

Each function takes the result dict produced by the pipeline and returns
a UTF-8 string ready to be sent as a file download.
"""
import json


# ---------------------------------------------------------------------------
# Time formatters
# ---------------------------------------------------------------------------

def _ms(seconds: float) -> str:
    """Format seconds as HH:MM:SS,mmm (SRT timestamp format)."""
    ms = int(round(seconds * 1000))
    h = ms // 3_600_000
    ms %= 3_600_000
    m = ms // 60_000
    ms %= 60_000
    s = ms // 1_000
    ms %= 1_000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _ts(seconds: float) -> str:
    """Format seconds as M:SS for human-readable display."""
    total = int(seconds)
    m = total // 60
    s = total % 60
    return f"{m}:{s:02d}"


# ---------------------------------------------------------------------------
# Format functions
# ---------------------------------------------------------------------------

def _format_json(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)


def _format_srt(result: dict) -> str:
    lines = []
    for i, seg in enumerate(result["segments"], 1):
        speaker_prefix = f"[{seg['speaker']}] " if seg.get("speaker") else ""
        lines.append(str(i))
        lines.append(f"{_ms(seg['start'])} --> {_ms(seg['end'])}")
        lines.append(f"{speaker_prefix}{seg['text']}")
        lines.append("")
    return "\n".join(lines)


def _format_txt(result: dict) -> str:
    lines = []
    prev_speaker = None
    for seg in result["segments"]:
        speaker = seg.get("speaker", "")
        if speaker and speaker != prev_speaker:
            if lines:
                lines.append("")
            lines.append(f"{speaker}:")
            prev_speaker = speaker
        ts = _ts(seg["start"])
        prefix = f"[{ts}] " if not speaker else f"  [{ts}] "
        lines.append(f"{prefix}{seg['text']}")
    return "\n".join(lines)


def _format_md(result: dict) -> str:
    lang = result.get("language", "").upper()
    dur = _ts(result.get("duration", 0))
    lines = [
        "# AmicoScript Transcript",
        "",
        f"**Language:** {lang or 'auto'} | **Duration:** {dur} | **Segments:** {result.get('num_segments', 0)}",
        "",
        "---",
        "",
    ]
    prev_speaker = None
    for seg in result["segments"]:
        speaker = seg.get("speaker", "")
        if speaker and speaker != prev_speaker:
            lines.append(f"**{speaker}**")
            prev_speaker = speaker
        ts_start = _ts(seg["start"])
        ts_end = _ts(seg["end"])
        lines.append(f"> `{ts_start} – {ts_end}` {seg['text']}")
        lines.append("")
    return "\n".join(lines)
