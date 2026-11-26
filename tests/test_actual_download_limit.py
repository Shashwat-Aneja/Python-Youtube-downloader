from pathlib import Path
from types import SimpleNamespace
import pytest
from yt_downloader import download_stream

@pytest.mark.parametrize('no_overwrite',[False,True])
def test_actual_bytes_are_checked_before_publishing_even_when_metadata_understates(tmp_path,no_overwrite):
    destination=tmp_path/'clip.mp4'
    if not no_overwrite:destination.write_bytes(b'keep')
    def download(output_path,**kwargs):
        p=Path(output_path)/'clip.mp4';p.write_bytes(b'x'*11);return str(p)
    stream=SimpleNamespace(filesize=1,default_filename='clip.mp4',download=download)
    with pytest.raises(ValueError,match='exceeds'):download_stream(stream,tmp_path,max_size_bytes=10,no_overwrite=no_overwrite)
    assert sorted(p.name for p in tmp_path.iterdir())==([] if no_overwrite else ['clip.mp4'])
    if not no_overwrite:assert destination.read_bytes()==b'keep'
