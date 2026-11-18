import pytest
from yt_downloader import list_streams


@pytest.mark.parametrize("error", [KeyError("approxDurationMs"), ValueError("invalid size"), TypeError("missing bitrate")])
def test_malformed_size_property_does_not_break_listing(error, capsys):
    class Stream:
        resolution = "720p"
        @property
        def filesize_approx(self):
            raise error
    list_streams([Stream()])
    text = capsys.readouterr().out
    assert "720p" in text and "size unknown" in text
