from types import SimpleNamespace
import pytest
from yt_downloader import list_streams


@pytest.mark.parametrize("size", [None, "unknown", -1, float("nan"), float("inf"), True])
def test_unknown_size_does_not_break_stream_listing(size, capsys):
    list_streams([SimpleNamespace(resolution="720p", filesize=size)])
    assert "size unknown" in capsys.readouterr().out


def test_zero_size_remains_visible(capsys):
    list_streams([SimpleNamespace(resolution="720p", filesize=0)])
    assert "0.00MB" in capsys.readouterr().out
