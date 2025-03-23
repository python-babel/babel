import pytest

try:
    import zoneinfo
except ModuleNotFoundError:
    try:
        from backports import zoneinfo
    except ImportError:
        zoneinfo = None

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
        if zoneinfo:
            return zoneinfo.ZoneInfo
        else:
            pytest.skip("zoneinfo not available")
    else:
        raise NotImplementedError
