from types import SimpleNamespace

from yt_downloader import audio_bitrate_kbps, sort_audio_streams, video_resolution_height


def test_unknown_audio_bitrate_is_ranked_after_known_streams():
    streams = [
        SimpleNamespace(abr=None),
        SimpleNamespace(abr="96kbps"),
        SimpleNamespace(abr="160kbps"),
    ]
    result = sort_audio_streams(streams)
    assert [stream.abr for stream in result] == ["160kbps", "96kbps", None]
    assert audio_bitrate_kbps(streams[0]) == -1.0


def test_video_resolution_parser_rejects_unrecognized_values():
    for resolution in ("", None, "auto", "4k", "1080"):
        assert video_resolution_height(SimpleNamespace(resolution=resolution)) is None
