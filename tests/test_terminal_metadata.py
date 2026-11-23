from types import SimpleNamespace
from yt_downloader import list_streams, download_stream

def test_stream_quality_and_filename_escape_controls(capsys):
    stream = SimpleNamespace(resolution='café\x1b[2J\n720p', fps='30\rspoof', filesize_approx=None,
                             default_filename='café\x1b[2J.mp4', download=lambda **kwargs: 'file.mp4')
    list_streams([stream])
    download_stream(stream)
    output = capsys.readouterr().out
    assert '\x1b' not in output and '\r' not in output
    assert 'café\\x1b[2J\\n720p' in output
    assert 'café\\x1b[2J.mp4' in output

def test_published_download_path_escapes_nonprintable_filename(tmp_path,capsys):
    name='café\x9b2J.mp4'
    def download(output_path, **kwargs):
        p=__import__('pathlib').Path(output_path)/name;p.write_bytes(b'video');return str(p)
    stream=SimpleNamespace(default_filename=name,download=download)
    result=download_stream(stream,output_dir=tmp_path,no_overwrite=True)
    assert __import__('pathlib').Path(result).read_bytes()==b'video'
    output=capsys.readouterr().out
    assert '\x9b' not in output and 'café\\x9b2J.mp4' in output
