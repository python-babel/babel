from __future__ import annotations

import datetime

from babel import Locale
from babel.dates import (
    _cached_parse_pattern,
    format_date,
    format_datetime,
    format_interval,
    format_skeleton,
    format_time,
    format_timedelta,
    get_timezone_name,
    parse_date,
    parse_pattern,
)


def test_format_date_standalone_month(benchmark, fi_locale):
    d = datetime.date(2025, 10, 15)
    assert benchmark(lambda: format_date(d, "LLLL", fi_locale)) == "lokakuu"


def test_locale_deep_data_read(benchmark):
    # Repeated alias-resolving deep reads through a long-lived Locale.
    locale = Locale.parse("fi")
    assert locale.months["stand-alone"]["wide"][10] == "lokakuu"
    benchmark(lambda: locale.months["stand-alone"]["wide"][10])


def test_format_datetime_medium(benchmark, helsinki_tz, fi_locale):
    dt = datetime.datetime(2025, 10, 15, 13, 45, 30)
    assert benchmark(lambda: format_datetime(dt, locale=fi_locale)) == "15.10.2025 13.45.30"


def test_format_time_with_tzinfo(benchmark, fi_locale, helsinki_tz):
    # Aware datetime, converted into another zone on the way out.
    dt = datetime.datetime(2025, 10, 15, 13, 45, 30, tzinfo=datetime.timezone.utc)
    assert (
        benchmark(lambda: format_time(dt, locale=fi_locale, tzinfo=helsinki_tz)) == "16.45.30"
    )


def test_format_timedelta_long(benchmark, fi_locale):
    delta = datetime.timedelta(days=3, hours=5)
    expected = "3 päivää"
    assert format_timedelta(delta, locale=fi_locale) == expected
    assert benchmark(lambda: format_timedelta(delta, locale=fi_locale)) == expected


def test_format_timedelta_short_hours(benchmark, fi_locale):
    delta = datetime.timedelta(days=3, hours=5)
    assert (
        benchmark(
            lambda: format_timedelta(
                delta,
                granularity="hour",
                format="short",
                locale=fi_locale,
            ),
        )
        == "3 pv"
    )


def test_format_skeleton(benchmark, fi_locale):
    dt = datetime.datetime(2025, 10, 15, 13, 45, 30)
    assert benchmark(lambda: format_skeleton("yMMMd", dt, locale=fi_locale)) == "15.10.2025"


def test_format_skeleton_fuzzy(benchmark, fi_locale):
    # "EyMMMd" is not in the locale's skeleton table, so match_skeleton() has to run.
    dt = datetime.datetime(2025, 10, 15, 13, 45, 30)
    assert (
        benchmark(lambda: format_skeleton("EyMMMd", dt, fuzzy=True, locale=fi_locale))
        == "ke 15.10.2025"
    )


def test_format_interval_same_day(benchmark, fi_locale):
    start = datetime.datetime(2025, 10, 15, 9, 0)
    end = datetime.datetime(2025, 10, 15, 17, 30)
    assert (
        benchmark(lambda: format_interval(start, end, "Hm", locale=fi_locale)) == "9.00–17.30"
    )


def test_parse_pattern_cached(benchmark):
    assert benchmark(lambda: parse_pattern("MMM d, yyyy").format) == "%(MMM)s %(d)s, %(yyyy)s"


def test_parse_pattern_uncached(benchmark):
    # Bypass the lru_cache to measure actual tokenization + parsing.
    parse = _cached_parse_pattern.__wrapped__
    assert benchmark(lambda: parse("MMM d, yyyy").format) == "%(MMM)s %(d)s, %(yyyy)s"


def test_parse_date_short(benchmark, fi_locale):
    assert benchmark(lambda: parse_date("15.10.2025", locale=fi_locale)) == datetime.date(
        2025,
        10,
        15,
    )


def test_get_timezone_name(benchmark, fi_locale, helsinki_tz):
    assert (
        benchmark(lambda: get_timezone_name(helsinki_tz, locale=fi_locale))
        == "Itä-Euroopan aika"
    )
