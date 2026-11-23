import pytest
from yt_downloader import stream_metadata

class Stream:
    @property
    def filesize(self):
        raise AssertionError('exact size must not be read')
    @property
    def filesize_approx(self):
        return 1234

def test_optional_approximate_bytes():
    assert 'filesize_approx_bytes' not in stream_metadata([Stream()])[0]
    assert stream_metadata([Stream()], include_approx_size=True)[0]['filesize_approx_bytes'] == 1234

@pytest.mark.parametrize('value', [None, float('nan'), float('inf'), -1, True, '100'])
def test_invalid_size_is_json_null(value):
    class Unknown(Stream):
        filesize_approx = value
    assert stream_metadata([Unknown()], include_approx_size=True)[0]['filesize_approx_bytes'] is None

def test_default_never_reads_approximate_size():
    class NoSize(Stream):
        @property
        def filesize_approx(self):
            raise AssertionError('unexpected metadata access')
    stream_metadata([NoSize()])
