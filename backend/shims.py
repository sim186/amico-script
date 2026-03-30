"""torchcodec compatibility shim for pyannote.audio.

pyannote.audio tries to import torchcodec's C extension for audio decoding.
That extension is unavailable in several common deployment scenarios:
  - Docker containers on ARM64 (no pre-built wheel)
  - PyInstaller bundles (FFmpeg/CUDA shared libs absent)
  - Standalone Windows/macOS executables

This module injects a torchaudio-backed mock into sys.modules *before*
pyannote is imported, so the real C extension is never attempted.

Call inject_torchcodec_shim() once (it is idempotent) before the first
`from pyannote.audio import Pipeline` statement.
"""
import sys
import types


def inject_torchcodec_shim() -> None:
    """Inject the torchaudio-backed torchcodec shim (no-op if already injected)."""
    if "torchcodec" in sys.modules:
        return

    import torchaudio as _ta

    _tc = types.ModuleType("torchcodec")
    _tc_decoders = types.ModuleType("torchcodec.decoders")

    class _AudioStreamMetadata:
        """Mimics torchcodec.decoders.AudioStreamMetadata."""

        def __init__(self, sample_rate: int, num_frames: int) -> None:
            self.sample_rate = sample_rate
            self.num_frames = num_frames
            self.duration_seconds_from_header = (
                num_frames / sample_rate if sample_rate else 0.0
            )

    class _AudioSamples:
        """Mimics torchcodec.AudioSamples."""

        def __init__(self, data, sample_rate: int) -> None:
            self.data = data
            self.sample_rate = sample_rate

    class _AudioDecoder:
        """torchaudio-backed replacement for torchcodec.decoders.AudioDecoder."""

        def __init__(self, source: str) -> None:
            self._source = source
            info = _ta.info(source)
            self.metadata = _AudioStreamMetadata(
                sample_rate=info.sample_rate,
                num_frames=info.num_frames,
            )

        def get_all_samples(self) -> "_AudioSamples":
            waveform, sr = _ta.load(self._source)
            return _AudioSamples(waveform, sr)

        def get_samples_played_in_range(self, start: float, end: float) -> "_AudioSamples":
            info = _ta.info(self._source)
            sr = info.sample_rate
            frame_offset = int(start * sr)
            num_frames = int((end - start) * sr)
            waveform, sr = _ta.load(
                self._source, frame_offset=frame_offset, num_frames=num_frames
            )
            return _AudioSamples(waveform, sr)

    _tc_decoders.AudioDecoder = _AudioDecoder
    _tc_decoders.AudioStreamMetadata = _AudioStreamMetadata
    _tc.AudioSamples = _AudioSamples
    _tc.decoders = _tc_decoders
    sys.modules["torchcodec"] = _tc
    sys.modules["torchcodec.decoders"] = _tc_decoders
