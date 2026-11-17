import sys
from types import SimpleNamespace
import pytest
from yt_downloader import main


@pytest.mark.parametrize("index", ["0", "-1"])
def test_invalid_index_is_rejected_before_metadata_request(index, monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("must not fetch video metadata")
    monkeypatch.setitem(sys.modules, "pytube", SimpleNamespace(YouTube=fail))
    with pytest.raises(SystemExit) as exc:
        main(["https://example.test/video", "--index", index])
    assert exc.value.code == 2
