from types import SimpleNamespace
import pytest
from yt_downloader import filter_audio_streams,sort_audio_streams,main

def test_audio_bitrate_cap_filters_unknown_and_over_budget_formats():
    streams=[SimpleNamespace(abr=value) for value in ['160kbps','64kbps',None,'128kbps']]
    selected=sort_audio_streams(filter_audio_streams(streams,128))
    assert [s.abr for s in selected]==['128kbps','64kbps']

def test_audio_cap_requires_audio_mode_before_network():
    with pytest.raises(SystemExit):main(['url','--max-audio-bitrate','128'])
