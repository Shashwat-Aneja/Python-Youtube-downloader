from types import SimpleNamespace
import pytest
from yt_downloader import list_streams,validate_timeout
def test_oversized_integer_size_is_unknown(capsys):
    list_streams([SimpleNamespace(filesize_approx=10**1000)])
    assert 'size unknown' in capsys.readouterr().out
def test_oversized_timeout_has_public_validation_error():
    with pytest.raises(ValueError,match='timeout'):validate_timeout(10**1000)
