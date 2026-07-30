from __future__ import annotations

from importlib.util import find_spec
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    import zoneinfo

    import babel

if not (find_spec("pytest_benchmark") or find_spec("pytest_codspeed")):
    pytest.skip("pytest-benchmark or pytest-codspeed required", allow_module_level=True)


@pytest.fixture(scope="function", params=["fresh", "cached"])
def fi_locale(request) -> str | babel.Locale:
    from babel import Locale

    if request.param == "fresh":
        return "fi"
    return Locale.parse("fi")  # Share the object in the test


@pytest.fixture(scope="session")
def helsinki_tz() -> zoneinfo.ZoneInfo:
    import zoneinfo

    return zoneinfo.ZoneInfo("Europe/Helsinki")
