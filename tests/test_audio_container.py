from types import SimpleNamespace
import sys,json,pytest
import yt_downloader as app
def test_audio_container_filter_is_forwarded_before_listing(monkeypatch,capsys):
    observed=[]
    class Streams:
        def filter(self,**options):observed.append(options);return [SimpleNamespace(itag=140,abr='128kbps')]
    monkeypatch.setitem(sys.modules,'pytube',SimpleNamespace(YouTube=lambda _:SimpleNamespace(streams=Streams())))
    app.main(['https://example.test/video','--audio-only','--audio-format','mp4','--json-streams'])
    assert observed==[{'only_audio':True,'file_extension':'mp4'}]
    assert json.loads(capsys.readouterr().out)[0]['itag']==140
def test_audio_container_requires_audio_mode():
    with pytest.raises(SystemExit):app.main(['url','--audio-format','webm'])
