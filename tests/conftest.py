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
            if mark.name == "all_rbnf_locales":
                from babel.core import get_global
                metafunc.parametrize("locale", list(get_global('rbnf_locales')))
                break
