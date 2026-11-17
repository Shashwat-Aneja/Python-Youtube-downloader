from types import SimpleNamespace
import pytest
from yt_downloader import audio_bitrate_kbps, video_resolution_height


@pytest.mark.parametrize("abr", ["-160kbps", "0kbps", "abc160kbps", "160mbps", "9" * 400 + "kbps"])
def test_malformed_bitrates_are_unknown(abr):
    assert audio_bitrate_kbps(SimpleNamespace(abr=abr)) == -1


@pytest.mark.parametrize("resolution", ["0p", "720potato", "1080p60bad", "-720p"])
def test_malformed_resolution_is_unknown(resolution):
    assert video_resolution_height(SimpleNamespace(resolution=resolution)) is None


def test_valid_quality_metadata():
    assert audio_bitrate_kbps(SimpleNamespace(abr=" 128.5kbps ")) == 128.5
    assert video_resolution_height(SimpleNamespace(resolution="1080p60")) == 1080
