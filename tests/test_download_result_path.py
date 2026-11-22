from types import SimpleNamespace
from yt_downloader import download_stream
def test_default_download_returns_library_result_path():
    stream=SimpleNamespace(default_filename='video.mp4',download=lambda **kwargs:'returned/video.mp4')
    assert download_stream(stream)=='returned/video.mp4'
def test_custom_destination_returns_library_result_path(tmp_path):
    expected=str(tmp_path/'video.mp4')
    stream=SimpleNamespace(default_filename='video.mp4',download=lambda **kwargs:expected)
    assert download_stream(stream,output_dir=tmp_path)==expected
