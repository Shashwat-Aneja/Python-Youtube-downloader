import sys
from types import SimpleNamespace

import pytest

from yt_downloader import download_stream, main, select_stream


class FakeStream:
    def __init__(self, resolution):
        self.resolution = resolution
        self.default_filename = "video.mp4"
        self.download_calls = []

    def download(self, **kwargs):
        self.download_calls.append(kwargs)


class FakeAudioStream:
    def __init__(self, abr):
        self.abr = abr
        self.default_filename = "audio.webm"
        self.filesize = 2_000_000
        self.download_calls = []

    def download(self, **kwargs):
        self.download_calls.append(kwargs)


def test_default_selection_uses_first_highest_resolution_stream():
    streams = [FakeStream("1080p"), FakeStream("720p"), FakeStream("360p")]

    assert select_stream(streams).resolution == "1080p"


def test_one_based_index_selects_requested_stream():
    streams = [FakeStream("1080p"), FakeStream("720p"), FakeStream("360p")]

    assert select_stream(streams, 2).resolution == "720p"


@pytest.mark.parametrize("index", [0, -1, True, 1.5])
def test_invalid_stream_indices_are_rejected(index):
    with pytest.raises(ValueError, match="positive integer"):
        select_stream([FakeStream("720p")], index)


def test_out_of_range_and_empty_stream_lists_are_rejected():
    with pytest.raises(ValueError, match="out of range"):
        select_stream([FakeStream("720p")], 2)
    with pytest.raises(ValueError, match="No matching streams"):
        select_stream([])


def test_download_stream_creates_and_uses_requested_output_directory(tmp_path):
    stream = FakeStream("720p")
    destination = tmp_path / "nested" / "downloads"

    download_stream(stream, output_dir=destination)

    assert destination.is_dir()
    assert stream.download_calls == [{"output_path": str(destination)}]


def test_download_stream_preserves_pytube_default_when_no_directory_is_given():
    stream = FakeStream("720p")

    download_stream(stream)

    assert stream.download_calls == [{}]


def test_audio_only_cli_selects_by_bitrate_without_video_filters(monkeypatch, capsys):
    streams = [FakeAudioStream("160kbps"), FakeAudioStream("128kbps")]

    class FakeStreamQuery:
        def filter(self, **kwargs):
            assert kwargs == {"only_audio": True}
            return self

        def order_by(self, field):
            assert field == "abr"
            return self

        def desc(self):
            return streams

    class FakeYouTube:
        def __init__(self, _url):
            self.title = "Test video"
            self.author = "Test author"
            self.streams = FakeStreamQuery()

    monkeypatch.setitem(sys.modules, "pytube", SimpleNamespace(YouTube=FakeYouTube))
    downloads = []
    monkeypatch.setattr("yt_downloader.download_stream", lambda stream, output_dir=None: downloads.append(stream))

    main(["https://example.test/video", "--audio-only", "--index", "2"])

    assert downloads == [streams[1]]
    output = capsys.readouterr().out
    assert "Available Audio Streams:" in output
    assert "160kbps" in output
