from types import SimpleNamespace

import pytest

from yt_downloader import filter_video_streams, video_resolution_height


def test_resolution_height_parses_common_pytube_values():
    assert video_resolution_height(SimpleNamespace(resolution="720p")) == 720
    assert video_resolution_height(SimpleNamespace(resolution="1080p60")) == 1080
    assert video_resolution_height(SimpleNamespace(resolution=None)) is None


def test_max_resolution_keeps_eligible_streams_in_existing_quality_order():
    streams = [
        SimpleNamespace(resolution="1080p"),
        SimpleNamespace(resolution="720p"),
        SimpleNamespace(resolution="480p"),
        SimpleNamespace(resolution=None),
    ]

    result = filter_video_streams(streams, max_resolution=720)

    assert [stream.resolution for stream in result] == ["720p", "480p"]


def test_missing_resolution_cap_preserves_all_streams():
    streams = [SimpleNamespace(resolution=None), SimpleNamespace(resolution="360p")]
    assert filter_video_streams(streams) == streams


@pytest.mark.parametrize("limit", [0, -1, True, 720.5])
def test_invalid_resolution_caps_are_rejected(limit):
    with pytest.raises(ValueError, match="positive integer"):
        filter_video_streams([], max_resolution=limit)
