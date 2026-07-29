from __future__ import annotations

from babel import Locale
from babel.core import (
    get_global,
    get_locale_identifier,
    negotiate_locale,
    parse_locale,
)


def test_locale_parse_language(benchmark, fi_locale):
    # The most common shape: a plain language tag, or an already-parsed Locale.
    assert benchmark(lambda: Locale.parse(fi_locale)).language == "fi"


def test_locale_parse_full_tag(benchmark):
    assert str(benchmark(lambda: Locale.parse("zh-Hans-CN", sep="-"))) == "zh_Hans_CN"


def test_locale_parse_with_variant(benchmark):
    assert str(benchmark(lambda: Locale.parse("en_US_POSIX"))) == "en_US_POSIX"


def test_locale_parse_likely_subtags(benchmark):
    # zh_TW only exists via likely subtag resolution, i.e. the slow path.
    assert str(benchmark(lambda: Locale.parse("zh_TW"))) == "zh_Hant_TW"


def test_locale_construct(benchmark):
    assert str(benchmark(lambda: Locale("en", "US"))) == "en_US"


def test_negotiate_locale(benchmark):
    preferred = ["fi_FI", "en-US", "de"]
    available = ["en", "de", "fi"]
    assert benchmark(lambda: negotiate_locale(preferred, available)) == "fi"


def test_parse_locale(benchmark):
    assert benchmark(lambda: parse_locale("en_US.UTF-8")) == ("en", "US", None, None)


def test_get_locale_identifier(benchmark):
    parts = ("zh", "CN", "Hans", None)
    assert benchmark(lambda: get_locale_identifier(parts)) == "zh_Hans_CN"


def test_get_global(benchmark):
    assert benchmark(lambda: get_global("zone_territories")["Europe/Helsinki"]) == "FI"


def test_locale_get_display_name(benchmark):
    locale = Locale.parse("fi")
    en = Locale.parse("en")
    assert benchmark(lambda: locale.get_display_name(en)) == "Finnish"
