import pytest
from types import SimpleNamespace
from yt_downloader import download_stream
@pytest.mark.parametrize('size',[101,None,-1,True])
def test_oversized_or_unknown_size_never_starts_download(size,tmp_path):
    def fail(**options):pytest.fail('download must not start')
    stream=SimpleNamespace(filesize=size,download=fail,default_filename='clip.mp4')
    with pytest.raises(ValueError):download_stream(stream,tmp_path/'out',max_size_bytes=100)
    assert not (tmp_path/'out').exists()
def test_exact_limit_is_allowed(tmp_path):
    calls=[];stream=SimpleNamespace(filesize=100,default_filename='clip.mp4',download=lambda **options:calls.append(options))
    download_stream(stream,tmp_path,max_size_bytes=100)
    assert len(calls)==1
