from pathlib import Path

from core import source_downloader


def test_is_supported_source_url_youtube_only():
    assert source_downloader.is_supported_source_url("https://www.youtube.com/watch?v=abc")
    assert source_downloader.is_supported_source_url("https://youtu.be/abc")
    assert source_downloader.is_supported_source_url("https://vimeo.com/123")
    assert not source_downloader.is_supported_source_url("ftp://youtube.com/file")


def test_resolve_source_candidates_playlist(monkeypatch):
    info_payload = {
        "entries": [
            {"id": "id1", "title": "First"},
            {"webpage_url": "https://www.youtube.com/watch?v=id2", "title": "Second"},
        ]
    }

    class _FakeYDL:
        def __init__(self, _opts):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def extract_info(self, _url, download=False):
            assert download is False
            return info_payload

    monkeypatch.setattr(source_downloader, "_get_yt_dlp_class", lambda: _FakeYDL)

    items = source_downloader.resolve_source_candidates(
        "https://www.youtube.com/playlist?list=abc",
        include_playlist=True,
    )

    assert len(items) == 2
    assert items[0].url == "https://www.youtube.com/watch?v=id1"
    assert items[0].title == "First"
    assert items[0].platform == "youtube"
    assert items[1].url == "https://www.youtube.com/watch?v=id2"


def test_download_source_audio_returns_requested_filepath(monkeypatch, tmp_path):
    events = []

    class _FakeYDL:
        def __init__(self, opts):
            self._opts = opts

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def extract_info(self, _url, download=True):
            assert download is True
            hook = self._opts["progress_hooks"][0]
            hook({"status": "downloading", "downloaded_bytes": 5, "total_bytes": 10})
            hook({"status": "finished"})
            return {
                "title": "Clip",
                "requested_downloads": [{"filepath": str(tmp_path / "clip.m4a")}],
            }

        def prepare_filename(self, _info):
            return str(tmp_path / "fallback.m4a")

    monkeypatch.setattr(source_downloader, "_get_yt_dlp_class", lambda: _FakeYDL)

    out_path, title = source_downloader.download_source_audio(
        "https://www.youtube.com/watch?v=abc",
        Path(tmp_path),
        on_progress=lambda status, progress, message: events.append((status, progress, message)),
    )

    assert out_path == tmp_path / "clip.m4a"
    assert title == "Clip"
    assert events[0][0] == "downloading"
    assert events[-1][0] == "postprocessing"


def test_detect_source_platform_known_hosts():
    assert source_downloader.detect_source_platform("https://www.youtube.com/watch?v=a") == "youtube"
    assert source_downloader.detect_source_platform("https://www.tiktok.com/@u/video/1") == "tiktok"
    assert source_downloader.detect_source_platform("https://www.instagram.com/reel/abc/") == "instagram"
    assert source_downloader.detect_source_platform("https://facebook.com/watch/?v=1") == "facebook"
    assert source_downloader.detect_source_platform("https://example.com/video") == "web"
