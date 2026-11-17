from yt_downloader import list_streams


def test_default_listing_never_requests_exact_network_size(capsys):
    class Stream:
        resolution = "720p"
        filesize_approx = 2_000_000
        @property
        def filesize(self):
            raise AssertionError("must not perform an exact-size request")
    list_streams([Stream()])
    assert "2.00MB" in capsys.readouterr().out
