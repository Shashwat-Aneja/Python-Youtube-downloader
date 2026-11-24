from types import SimpleNamespace
import pytest
from yt_downloader import filter_video_streams,main

def test_resolution_range_is_inclusive_and_excludes_unknown_formats():
    streams=[SimpleNamespace(resolution=value) for value in ['360p','720p','1080p','2160p',None]]
    assert [s.resolution for s in filter_video_streams(streams,max_resolution=1080,min_resolution=720)]==['720p','1080p']

def test_reversed_resolution_bounds_fail_before_network():
    with pytest.raises(SystemExit):main(['url','--min-resolution','1080','--max-resolution','720'])
