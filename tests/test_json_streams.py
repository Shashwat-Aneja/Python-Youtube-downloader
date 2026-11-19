import json,sys
from types import SimpleNamespace
import yt_downloader as app
def test_json_listing_is_parseable_and_never_downloads(monkeypatch,capsys):
    stream=SimpleNamespace(itag=140,abr='128kbps',mime_type='audio/mp4')
    class Streams:
        def filter(self,**kwargs):return [stream]
    monkeypatch.setitem(sys.modules,'pytube',SimpleNamespace(YouTube=lambda _:SimpleNamespace(streams=Streams())))
    monkeypatch.setattr(app,'download_stream',lambda *a,**k:(_ for _ in ()).throw(AssertionError('download')))
    app.main(['https://example.test/video','--audio-only','--json-streams'])
    records=json.loads(capsys.readouterr().out)
    assert records[0]['itag']==140 and records[0]['index']==1
