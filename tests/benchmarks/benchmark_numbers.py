from __future__ import annotations

from decimal import Decimal

from babel.numbers import (
    format_compact_currency,
    format_compact_decimal,
    format_currency,
    format_decimal,
    format_percent,
    format_scientific,
    get_currency_name,
    get_territory_currencies,
    parse_decimal,
)


def test_format_decimal(benchmark, fi_locale):
    number = Decimal("1234567.891")
    assert benchmark(lambda: format_decimal(number, locale=fi_locale)) == "1\xa0234\xa0567,891"


def test_format_currency(benchmark, fi_locale):
    number = Decimal("1234.5")
    assert (
        benchmark(lambda: format_currency(number, "EUR", locale=fi_locale))
        == "1\xa0234,50\xa0€"
    )


def test_format_currency_name(benchmark):
    # The "name" format type additionally does a plural-form currency name lookup.
    number = Decimal("1234.5")
    assert (
        benchmark(lambda: format_currency(number, "EUR", locale="fi", format_type="name"))
        == "1\xa0234,50 euroa"
    )


def test_format_compact_decimal(benchmark):
    assert (
        benchmark(
            lambda: format_compact_decimal(
                1234567,
                format_type="long",
                locale="fi",
                fraction_digits=2,
            ),
        )
        == "1,23 miljoonaa"
    )


def test_format_compact_currency(benchmark):
    assert (
        benchmark(
            lambda: format_compact_currency(123456789, "EUR", locale="fi", fraction_digits=1),
        )
        == "123,5\xa0milj.\xa0€"
    )


def test_format_percent(benchmark):
    number = Decimal("0.3456")
    assert benchmark(lambda: format_percent(number, locale="fi")) == "35\xa0%"


def test_format_scientific(benchmark):
    number = Decimal("1234567.891")
    assert benchmark(lambda: format_scientific(number, locale="fi")) == "1,234567891E6"


def test_parse_decimal(benchmark, fi_locale):
    string = "1\xa0234\xa0567,891"
    assert benchmark(lambda: parse_decimal(string, locale=fi_locale, strict=True)) == Decimal(
        "1234567.891",
    )


def test_get_currency_name(benchmark):
    assert benchmark(lambda: get_currency_name("EUR", count=2, locale="fi")) == "euroa"


def test_get_territory_currencies(benchmark):
    assert benchmark(lambda: get_territory_currencies("FI")) == ["EUR"]
