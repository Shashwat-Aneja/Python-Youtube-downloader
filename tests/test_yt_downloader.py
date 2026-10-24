import pytest

from yt_downloader import select_stream


class FakeStream:
    def __init__(self, resolution):
        self.resolution = resolution


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
    with pytest.raises(ValueError, match="No progressive MP4 streams"):
        select_stream([])
