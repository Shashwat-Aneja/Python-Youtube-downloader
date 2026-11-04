from types import SimpleNamespace

import pytest

from yt_downloader import download_stream, validate_timeout


class FakeStream:
    default_filename = "sample.mp4"

    def __init__(self):
        self.options = None

    def download(self, **options):
        self.options = options
        return "sample.mp4"


@pytest.mark.parametrize("value", [0, -1, float("inf"), float("nan"), True, "invalid"])
def test_validate_timeout_rejects_non_positive_or_non_finite_values(value):
    with pytest.raises(ValueError, match="positive finite number"):
        validate_timeout(value)


def test_download_stream_passes_timeout_without_custom_directory():
    stream = FakeStream()

    download_stream(stream, timeout=12.5)

    assert stream.options == {"timeout": 12.5}


def test_download_stream_passes_timeout_and_creates_output_directory(tmp_path):
    stream = FakeStream()
    destination = tmp_path / "downloads" / "videos"

    download_stream(stream, output_dir=destination, timeout=30)

    assert stream.options == {"output_path": str(destination), "timeout": 30.0}
    assert destination.is_dir()


def test_download_stream_preserves_default_timeout_when_not_configured():
    stream = FakeStream()

    download_stream(stream)

    assert stream.options == {}


def test_timeout_validator_rejects_boolean_values_even_though_bool_is_numeric():
    with pytest.raises(ValueError, match="positive finite number"):
        validate_timeout(False)
