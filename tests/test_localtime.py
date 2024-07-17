import sys

import pytest

from babel.localtime import _helpers, get_localzone


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Issue 1092 is not applicable on Windows",
)
def test_issue_1092_without_pytz(monkeypatch):
    pytest.importorskip("zoneinfo", reason="zoneinfo is not available")
    monkeypatch.setenv("TZ", "/UTC")  # Malformed timezone name.
    # In case pytz _is_ also installed, we want to pretend it's not, so patch it out...
    monkeypatch.setattr(_helpers, "pytz", None)
    with pytest.raises(LookupError):
        get_localzone()


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Issue 1092 is not applicable on Windows",
)
def test_issue_1092_with_pytz(monkeypatch):
    pytest.importorskip("pytz", reason="pytz is not installed")
    monkeypatch.setenv("TZ", "/UTC")  # Malformed timezone name.
    with pytest.raises(LookupError):
        get_localzone()
