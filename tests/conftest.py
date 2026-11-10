import datetime
import zoneinfo

import pytest
from freezegun import freeze_time

try:
    import pytz
except ModuleNotFoundError:
    pytz = None


def pytest_generate_tests(metafunc):
    if hasattr(metafunc.function, "pytestmark"):
        for mark in metafunc.function.pytestmark:
            if mark.name == "all_locales":
                from babel.localedata import locale_identifiers

                metafunc.parametrize("locale", list(locale_identifiers()))
                break


@pytest.fixture(params=["pytz.timezone", "zoneinfo.ZoneInfo"], scope="package")
def timezone_getter(request):
    if request.param == "pytz.timezone":
        if pytz:
            return pytz.timezone
        else:
            pytest.skip("pytz not available")
    elif request.param == "zoneinfo.ZoneInfo":
        return zoneinfo.ZoneInfo
    else:
        raise NotImplementedError


#: Frozen datetime used in various tests.
FROZEN_DATETIME = datetime.datetime(1994, 11, 11, 00, 00)


@pytest.fixture
def frozen_time() -> datetime.datetime:
    with freeze_time(FROZEN_DATETIME) as frozen:
        yield frozen.time_to_freeze
