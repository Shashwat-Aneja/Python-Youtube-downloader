import sys
from types import SimpleNamespace
import pytest
from yt_downloader import main

def test_untrusted_provider_errors_cannot_emit_terminal_controls(monkeypatch,capsys):
    def fail(url):raise ValueError('café\x1b[2J\nspoofed')
    monkeypatch.setitem(sys.modules,'pytube',SimpleNamespace(YouTube=fail))
    with pytest.raises(SystemExit) as exc:main(['url','--json-streams'])
    output=capsys.readouterr()
    assert exc.value.code==1 and output.out==''
    assert '\x1b' not in output.err and 'café\\x1b[2J\\nspoofed' in output.err
