from types import SimpleNamespace
import pytest
from yt_downloader import filter_audio_streams, main

def test_inclusive_audio_quality_window_and_unknown_rates():
    streams=[SimpleNamespace(abr=value) for value in ['64kbps','128kbps','192kbps',None]]
    assert [s.abr for s in filter_audio_streams(streams,min_bitrate=128,max_bitrate=192)]==['128kbps','192kbps']
    with pytest.raises(ValueError):filter_audio_streams(streams,min_bitrate=200,max_bitrate=100)

def test_invalid_cli_quality_window_fails_before_provider_access():
    with pytest.raises(SystemExit) as exc:main(['https://example.invalid','--audio-only','--min-audio-bitrate','200','--max-audio-bitrate','100'])
    assert exc.value.code==2
