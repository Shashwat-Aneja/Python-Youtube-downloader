import pytest
from yt_downloader import validate_filename


@pytest.mark.parametrize("name", ["C:video.mp4", "D:video.mp4", "NUL", "aux.mp4", "COM1.webm", "COM¹.mp4", "video.", "video ", "bad?name.mp4", "bad\x01.mp4"])
def test_custom_filenames_cannot_use_drive_or_device_aliases(name):
    with pytest.raises(ValueError, match="Filename"):
        validate_filename(name)


def test_portable_unicode_filename_is_retained():
    assert validate_filename("café.mp4") == "café.mp4"
