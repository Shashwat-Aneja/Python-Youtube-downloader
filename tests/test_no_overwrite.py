from pathlib import Path
import pytest
from yt_downloader import download_stream
class Stream:
    default_filename='video.mp4'
    def download(self,output_path,**kwargs):
        p=Path(output_path)/kwargs.get('filename',self.default_filename);p.write_bytes(b'new video');return str(p)
def test_staged_download_publishes_and_cleans_up(tmp_path):
    result=download_stream(Stream(),tmp_path,no_overwrite=True)
    assert Path(result).read_bytes()==b'new video'
    assert sorted(p.name for p in tmp_path.iterdir())==['video.mp4']
def test_existing_download_is_not_replaced(tmp_path):
    p=tmp_path/'video.mp4';p.write_bytes(b'keep')
    with pytest.raises(FileExistsError):download_stream(Stream(),tmp_path,no_overwrite=True)
    assert p.read_bytes()==b'keep'
def test_concurrent_destination_creation_does_not_overwrite(tmp_path):
    class Racing(Stream):
        def download(self,**kwargs):
            (tmp_path/'video.mp4').write_bytes(b'concurrent')
            return super().download(**kwargs)
    with pytest.raises(FileExistsError):download_stream(Racing(),tmp_path,no_overwrite=True)
    assert (tmp_path/'video.mp4').read_bytes()==b'concurrent'
    assert len(list(tmp_path.iterdir()))==1

def test_partial_download_failure_is_cleaned_without_final_file(tmp_path):
    class Failing(Stream):
        def download(self,output_path,**kwargs):
            (Path(output_path)/'video.mp4').write_bytes(b'partial')
            raise OSError('network failure')
    with pytest.raises(OSError,match='network failure'):download_stream(Failing(),tmp_path,no_overwrite=True)
    assert list(tmp_path.iterdir())==[]
