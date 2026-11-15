import os
import sys
from unittest.mock import Mock

import pytest

from babel.localtime import get_localzone


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
