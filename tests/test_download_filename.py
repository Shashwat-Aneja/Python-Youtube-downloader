from types import SimpleNamespace
import pytest
from yt_downloader import download_stream, validate_filename


@pytest.mark.parametrize("name", ["", " ", ".", "..", "../x.mp4", "folder/x", "folder\\x", "bad\0name"])
def test_filename_cannot_escape_output_directory(name):
    with pytest.raises(ValueError, match="Filename"):
        validate_filename(name)


def test_filename_forwarded_with_output_directory_and_timeout(tmp_path):
    calls = []
    stream = SimpleNamespace(default_filename="original.mp4", download=lambda **kwargs: calls.append(kwargs))
    download_stream(stream, tmp_path, timeout=5, filename="lesson.mp4")
    assert calls == [{"filename": "lesson.mp4", "timeout": 5.0, "output_path": str(tmp_path)}]
