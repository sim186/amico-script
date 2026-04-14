"""Compatibility layer for legacy pipeline imports.

Core pipeline logic now lives under core/ modules.
"""

from core.analysis import _build_analysis_prompt, _process_analysis_job
from core.audio_utils import (
    _convert_audio_for_diarization,
    _convert_audio_for_transcription,
    _normalize_audio,
)
from core.colab_proxy import _handle_colab_job
from core.diarization import _assign_speaker, _run_diarization_phase
from core.job_helpers import (
    _append_job_log,
    _cleanup_job_temp_files,
    _handle_job_error,
    _push_event,
    _sync_job_to_db,
)
from core.transcription import (
    _finalize_transcription_result,
    _get_whisper_model,
    _is_missing_cuda_runtime_error,
    _is_missing_vad_asset_error,
    _process_job,
    _run_transcription_phase,
    _worker_loop,
    _worker_loop_async,
)
from core.translation import _process_translation_job, _translate_audio_chunk
