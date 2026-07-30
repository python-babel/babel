from __future__ import annotations

import datetime
import io

import pytest

from babel.support import Format, LazyProxy, Translations
from tests.benchmarks.helpers import build_catalog, dump_mo


@pytest.fixture()
def translations() -> Translations:
    return Translations(fp=io.BytesIO(dump_mo(build_catalog(20))))


def _greeting(name: str) -> str:
    return f"Hei, {name}!"


def test_format_decimal(benchmark):
    fmt = Format("fi")
    assert benchmark(lambda: fmt.decimal(1234567.891)) == "1\xa0234\xa0567,891"


def test_format_date(benchmark):
    fmt = Format("fi")
    d = datetime.date(2025, 10, 15)
    assert benchmark(lambda: fmt.date(d, "long")) == "15. lokakuuta 2025"


def test_lazy_proxy(benchmark):
    # Cache disabled so every access re-evaluates the wrapped function.
    proxy = LazyProxy(_greeting, "maailma", enable_cache=False)
    assert benchmark(lambda: f"{proxy} {proxy.upper()}") == "Hei, maailma! HEI, MAAILMA!"


def test_translations_gettext(benchmark, translations: Translations):
    # ugettext is an alias of gettext on Translations, so it measures the same path.
    assert benchmark(lambda: translations.gettext("Message number 19")) == "Viesti numero 19"


def test_translations_ngettext(benchmark, translations: Translations):
    assert benchmark(lambda: translations.ngettext("10 apple", "10 apples", 3)) == "10 omenaa"
