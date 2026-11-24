import os
import sys
from pathlib import Path
from unittest.mock import Mock
from zoneinfo import TZPATH

import pytest

from babel.localtime import get_localzone
from babel.localtime._helpers import _get_tzinfo_from_file


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Issue 1092 is not applicable on Windows",
)
def test_issue_1092(monkeypatch):
    pytest.importorskip("pytz", reason="pytz is not installed")
    monkeypatch.setenv("TZ", "/UTC")  # Malformed timezone name.
    with pytest.raises(LookupError):
        get_localzone()


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Issue 990 is not applicable on Windows",
)
def test_issue_990(monkeypatch):
    monkeypatch.setenv("TZ", "")
    fake_readlink = Mock(return_value="/usr/share/zoneinfo////UTC")  # Double slash, oops!
    monkeypatch.setattr(os, "readlink", fake_readlink)
    from babel.localtime._unix import _get_localzone

    assert _get_localzone() is not None
    fake_readlink.assert_called_with("/etc/localtime")


@pytest.mark.skipif(
    not TZPATH or not (Path(TZPATH[0]) / "UTC").exists(),
    reason="Test requires a timezone database",
)
def test_get_tzinfo_from_file():
    path = Path(TZPATH[0]) / "UTC"
    zone = _get_tzinfo_from_file(path)
    assert repr(zone) == f"zoneinfo.ZoneInfo.from_file(<_io.BufferedReader name='{path}'>)"
