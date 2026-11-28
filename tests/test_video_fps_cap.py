from types import SimpleNamespace
import pytest
from yt_downloader import filter_video_fps, main

def test_fps_cap_preserves_order_and_rejects_unknown():
    streams=[SimpleNamespace(fps=value) for value in [60,30,24,None,True,'30']]
    assert [s.fps for s in filter_video_fps(streams,30)]==[30,24]
    assert filter_video_fps(streams)==streams

@pytest.mark.parametrize('value',[True,0,1001,float('nan')])
def test_bad_fps_bound(value):
    with pytest.raises(ValueError):filter_video_fps([],value)

def test_audio_mode_rejects_fps_before_provider():
    with pytest.raises(SystemExit) as exc:main(['https://example.invalid','--audio-only','--max-fps','30'])
    assert exc.value.code==2
