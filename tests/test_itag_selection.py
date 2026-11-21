from types import SimpleNamespace
import pytest,sys
import yt_downloader as app
def test_itag_selection_survives_reordered_streams():
    first=SimpleNamespace(itag=140);second=SimpleNamespace(itag=141)
    assert app.select_stream([second,first],itag=140) is first
    with pytest.raises(ValueError):app.select_stream([first],itag=999)
    with pytest.raises(ValueError):app.select_stream([first,first],itag=140)
    with pytest.raises(ValueError):app.select_stream([first],index=1,itag=140)
def test_cli_itag_downloads_matching_audio_stream(monkeypatch):
    first=SimpleNamespace(itag=140,abr='128kbps');second=SimpleNamespace(itag=141,abr='256kbps')
    class Streams:
        def filter(self,**kwargs):return [second,first]
    monkeypatch.setitem(sys.modules,'pytube',SimpleNamespace(YouTube=lambda _:SimpleNamespace(streams=Streams(),title='demo',author='demo')))
    selected=[];monkeypatch.setattr(app,'download_stream',lambda stream,**kwargs:selected.append(stream))
    app.main(['https://example.test/video','--audio-only','--itag','140'])
    assert selected==[first]
