import pytest

from babel import Locale
from babel.numbers import format_currency, format_decimal, parse_pattern


@pytest.mark.parametrize(
    ('pattern', 'expected'),
    [
        ('0.0', '12.5'),
        ("'quoted'0.0", 'quoted12.5'),
        ("''0.0", "'12.5"),
        ("'''x'''0.0", "'x'12.5"),
        ("'未完0.0", "'未完0.0"),
        ("0.0'end'", '12.5end'),
        ("0.0'", "12.5'"),
        ("0.0''''", "12.5''"),
        ("'🐍'0.0", '🐍12.5'),
    ],
)
def test_number_pattern_quote_cleanup(pattern, expected):
    result = format_decimal(12.5, pattern, locale='en_US')
    assert result == expected
    assert type(result) is str


def test_number_pattern_quote_cleanup_after_mutation():
    pattern = parse_pattern('0.0')
    assert pattern.apply(12.5, 'en_US') == '12.5'
    pattern.prefix = ("'prefix'", "'negative'")
    pattern.suffix = ("''", "''")
    assert pattern.apply(12.5, 'en_US') == "prefix12.5'"
    assert pattern.apply(-12.5, 'en_US') == "negative12.5'"


def test_number_pattern_quote_cleanup_after_currency_replacement(monkeypatch):
    locale = Locale('en_US')
    monkeypatch.setitem(locale.currency_symbols, 'USD', "'cash'")
    assert format_currency(12.5, 'USD', locale=locale) == 'cash12.50'
