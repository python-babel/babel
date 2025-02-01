#
# Copyright (C) 2007-2011 Edgewall Software, 2013-2025 the Babel team
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution. The terms
# are also available at https://github.com/python-babel/babel/blob/master/LICENSE.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at https://github.com/python-babel/babel/commits/master/.

import decimal
import unittest
from datetime import date

import pytest

from babel import localedata, numbers
from babel.numbers import (
    UnknownCurrencyError,
    get_currency_precision,
    get_currency_unit_pattern,
    get_decimal_precision,
    is_currency,
    list_currencies,
    normalize_currency,
    validate_currency,
)


class FormatDecimalTestCase(unittest.TestCase):

    def test_patterns(self):
        assert numbers.format_decimal(12345, '##0', locale='en_US') == '12345'
        assert numbers.format_decimal(6.5, '0.00', locale='sv') == '6,50'
        assert numbers.format_decimal((10.0 ** 20), '#.00', locale='en_US') == '100000000000000000000.00'
        # regression test for #183, fraction digits were not correctly cut
        # if the input was a float value and the value had more than 7
        # significant digits
        assert numbers.format_decimal(12345678.051, '#,##0.00', locale='en_US') == '12,345,678.05'

    def test_subpatterns(self):
        assert numbers.format_decimal((- 12345), '#,##0.##;-#', locale='en_US') == '-12,345'
        assert numbers.format_decimal((- 12345), '#,##0.##;(#)', locale='en_US') == '(12,345)'

    def test_default_rounding(self):
        """
        Testing Round-Half-Even (Banker's rounding)

        A '5' is rounded to the closest 'even' number
        """
        assert numbers.format_decimal(5.5, '0', locale='sv') == '6'
        assert numbers.format_decimal(6.5, '0', locale='sv') == '6'
        assert numbers.format_decimal(1.2325, locale='sv') == '1,232'
        assert numbers.format_decimal(1.2335, locale='sv') == '1,234'

    def test_significant_digits(self):
        """Test significant digits patterns"""
        assert numbers.format_decimal(123004, '@@', locale='en_US') == '120000'
        assert numbers.format_decimal(1.12, '@', locale='sv') == '1'
        assert numbers.format_decimal(1.1, '@@', locale='sv') == '1,1'
        assert numbers.format_decimal(1.1, '@@@@@##', locale='sv') == '1,1000'
        assert numbers.format_decimal(0.0001, '@@@', locale='sv') == '0,000100'
        assert numbers.format_decimal(0.0001234, '@@@', locale='sv') == '0,000123'
        assert numbers.format_decimal(0.0001234, '@@@#', locale='sv') == '0,0001234'
        assert numbers.format_decimal(0.0001234, '@@@#', locale='sv') == '0,0001234'
        assert numbers.format_decimal(0.12345, '@@@', locale='sv') == '0,123'
        assert numbers.format_decimal(3.14159, '@@##', locale='sv') == '3,142'
        assert numbers.format_decimal(1.23004, '@@##', locale='sv') == '1,23'
        assert numbers.format_decimal(1230.04, '@@,@@', locale='en_US') == '12,30'
        assert numbers.format_decimal(123.41, '@@##', locale='en_US') == '123.4'
        assert numbers.format_decimal(1, '@@', locale='en_US') == '1.0'
        assert numbers.format_decimal(0, '@', locale='en_US') == '0'
        assert numbers.format_decimal(0.1, '@', locale='en_US') == '0.1'
        assert numbers.format_decimal(0.1, '@#', locale='en_US') == '0.1'
        assert numbers.format_decimal(0.1, '@@', locale='en_US') == '0.10'

    def test_decimals(self):
        """Test significant digits patterns"""
        assert numbers.format_decimal(decimal.Decimal('1.2345'), '#.00', locale='en_US') == '1.23'
        assert numbers.format_decimal(decimal.Decimal('1.2345000'), '#.00', locale='en_US') == '1.23'
        assert numbers.format_decimal(decimal.Decimal('1.2345000'), '@@', locale='en_US') == '1.2'
        assert numbers.format_decimal(decimal.Decimal('12345678901234567890.12345'), '#.00', locale='en_US') == '12345678901234567890.12'

    def test_scientific_notation(self):
        assert numbers.format_scientific(0.1, '#E0', locale='en_US') == '1E-1'
        assert numbers.format_scientific(0.01, '#E0', locale='en_US') == '1E-2'
        assert numbers.format_scientific(10, '#E0', locale='en_US') == '1E1'
        assert numbers.format_scientific(1234, '0.###E0', locale='en_US') == '1.234E3'
        assert numbers.format_scientific(1234, '0.#E0', locale='en_US') == '1.2E3'
        # Exponent grouping
        assert numbers.format_scientific(12345, '##0.####E0', locale='en_US') == '1.2345E4'
        # Minimum number of int digits
        assert numbers.format_scientific(12345, '00.###E0', locale='en_US') == '12.345E3'
        assert numbers.format_scientific(-12345.6, '00.###E0', locale='en_US') == '-12.346E3'
        assert numbers.format_scientific(-0.01234, '00.###E0', locale='en_US') == '-12.34E-3'
        # Custom pattern suffix
        assert numbers.format_scientific(123.45, '#.##E0 m/s', locale='en_US') == '1.23E2 m/s'
        # Exponent patterns
        assert numbers.format_scientific(123.45, '#.##E00 m/s', locale='en_US') == '1.23E02 m/s'
        assert numbers.format_scientific(0.012345, '#.##E00 m/s', locale='en_US') == '1.23E-02 m/s'
        assert numbers.format_scientific(decimal.Decimal('12345'), '#.##E+00 m/s', locale='en_US') == '1.23E+04 m/s'
        # 0 (see ticket #99)
        assert numbers.format_scientific(0, '#E0', locale='en_US') == '0E0'

    def test_formatting_of_very_small_decimals(self):
        # previously formatting very small decimals could lead to a type error
        # because the Decimal->string conversion was too simple (see #214)
        number = decimal.Decimal("7E-7")
        assert numbers.format_decimal(number, format="@@@", locale='en_US') == '0.000000700'

    def test_nan_and_infinity(self):
        assert numbers.format_decimal(decimal.Decimal('Infinity'), locale='en_US') == '∞'
        assert numbers.format_decimal(decimal.Decimal('-Infinity'), locale='en_US') == '-∞'
        assert numbers.format_decimal(decimal.Decimal('NaN'), locale='en_US') == 'NaN'
        assert numbers.format_compact_decimal(decimal.Decimal('Infinity'), locale='en_US', format_type="short") == '∞'
        assert numbers.format_compact_decimal(decimal.Decimal('-Infinity'), locale='en_US', format_type="short") == '-∞'
        assert numbers.format_compact_decimal(decimal.Decimal('NaN'), locale='en_US', format_type="short") == 'NaN'
        assert numbers.format_currency(decimal.Decimal('Infinity'), 'USD', locale='en_US') == '$∞'
        assert numbers.format_currency(decimal.Decimal('-Infinity'), 'USD', locale='en_US') == '-$∞'

    def test_group_separator(self):
        assert numbers.format_decimal(29567.12, locale='en_US', group_separator=False) == '29567.12'
        assert numbers.format_decimal(29567.12, locale='fr_CA', group_separator=False) == '29567,12'
        assert numbers.format_decimal(29567.12, locale='pt_BR', group_separator=False) == '29567,12'
        assert numbers.format_currency(1099.98, 'USD', locale='en_US', group_separator=False) == '$1099.98'
        assert numbers.format_currency(101299.98, 'EUR', locale='fr_CA', group_separator=False) == '101299,98\xa0€'
        assert numbers.format_currency(101299.98, 'EUR', locale='en_US', group_separator=False, format_type='name') == '101299.98 euros'
        assert numbers.format_percent(251234.1234, locale='sv_SE', group_separator=False) == '25123412\xa0%'

        assert numbers.format_decimal(29567.12, locale='en_US', group_separator=True) == '29,567.12'
        assert numbers.format_decimal(29567.12, locale='fr_CA', group_separator=True) == '29\xa0567,12'
        assert numbers.format_decimal(29567.12, locale='pt_BR', group_separator=True) == '29.567,12'
        assert numbers.format_currency(1099.98, 'USD', locale='en_US', group_separator=True) == '$1,099.98'
        assert numbers.format_currency(101299.98, 'EUR', locale='fr_CA', group_separator=True) == '101\xa0299,98\xa0€'
        assert numbers.format_currency(101299.98, 'EUR', locale='en_US', group_separator=True, format_type='name') == '101,299.98 euros'
        assert numbers.format_percent(251234.1234, locale='sv_SE', group_separator=True) == '25\xa0123\xa0412\xa0%'

    def test_compact(self):
        assert numbers.format_compact_decimal(1, locale='en_US', format_type="short") == '1'
        assert numbers.format_compact_decimal(999, locale='en_US', format_type="short") == '999'
        assert numbers.format_compact_decimal(1000, locale='en_US', format_type="short") == '1K'
        assert numbers.format_compact_decimal(9000, locale='en_US', format_type="short") == '9K'
        assert numbers.format_compact_decimal(9123, locale='en_US', format_type="short", fraction_digits=2) == '9.12K'
        assert numbers.format_compact_decimal(10000, locale='en_US', format_type="short") == '10K'
        assert numbers.format_compact_decimal(10000, locale='en_US', format_type="short", fraction_digits=2) == '10K'
        assert numbers.format_compact_decimal(1000000, locale='en_US', format_type="short") == '1M'
        assert numbers.format_compact_decimal(9000999, locale='en_US', format_type="short") == '9M'
        assert numbers.format_compact_decimal(9000900099, locale='en_US', format_type="short", fraction_digits=5) == '9.0009B'
        assert numbers.format_compact_decimal(1, locale='en_US', format_type="long") == '1'
        assert numbers.format_compact_decimal(999, locale='en_US', format_type="long") == '999'
        assert numbers.format_compact_decimal(1000, locale='en_US', format_type="long") == '1 thousand'
        assert numbers.format_compact_decimal(9000, locale='en_US', format_type="long") == '9 thousand'
        assert numbers.format_compact_decimal(9000, locale='en_US', format_type="long", fraction_digits=2) == '9 thousand'
        assert numbers.format_compact_decimal(10000, locale='en_US', format_type="long") == '10 thousand'
        assert numbers.format_compact_decimal(10000, locale='en_US', format_type="long", fraction_digits=2) == '10 thousand'
        assert numbers.format_compact_decimal(1000000, locale='en_US', format_type="long") == '1 million'
        assert numbers.format_compact_decimal(9999999, locale='en_US', format_type="long") == '10 million'
        assert numbers.format_compact_decimal(9999999999, locale='en_US', format_type="long", fraction_digits=5) == '10 billion'
        assert numbers.format_compact_decimal(1, locale='ja_JP', format_type="short") == '1'
        assert numbers.format_compact_decimal(999, locale='ja_JP', format_type="short") == '999'
        assert numbers.format_compact_decimal(1000, locale='ja_JP', format_type="short") == '1000'
        assert numbers.format_compact_decimal(9123, locale='ja_JP', format_type="short") == '9123'
        assert numbers.format_compact_decimal(10000, locale='ja_JP', format_type="short") == '1万'
        assert numbers.format_compact_decimal(1234567, locale='ja_JP', format_type="short") == '123万'
        assert numbers.format_compact_decimal(-1, locale='en_US', format_type="short") == '-1'
        assert numbers.format_compact_decimal(-1234, locale='en_US', format_type="short", fraction_digits=2) == '-1.23K'
        assert numbers.format_compact_decimal(-123456789, format_type='short', locale='en_US') == '-123M'
        assert numbers.format_compact_decimal(-123456789, format_type='long', locale='en_US') == '-123 million'
        assert numbers.format_compact_decimal(2345678, locale='mk', format_type='long') == '2 милиони'
        assert numbers.format_compact_decimal(21000000, locale='mk', format_type='long') == '21 милион'
        assert numbers.format_compact_decimal(21345, locale="gv", format_type="short") == '21K'
        assert numbers.format_compact_decimal(1000, locale='it', format_type='long') == 'mille'
        assert numbers.format_compact_decimal(1234, locale='it', format_type='long') == '1 mila'
        assert numbers.format_compact_decimal(1000, locale='fr', format_type='long') == 'mille'
        assert numbers.format_compact_decimal(1234, locale='fr', format_type='long') == '1 millier'
        assert numbers.format_compact_decimal(
            12345, format_type="short", locale='ar_EG', fraction_digits=2, numbering_system='default',
        ) == '12٫34\xa0ألف'
        assert numbers.format_compact_decimal(
            12345, format_type="short", locale='ar_EG', fraction_digits=2, numbering_system='latn',
        ) == '12.34\xa0ألف'


class NumberParsingTestCase(unittest.TestCase):

    def test_can_parse_decimals(self):
        assert decimal.Decimal('1099.98') == numbers.parse_decimal('1,099.98', locale='en_US')
        assert decimal.Decimal('1099.98') == numbers.parse_decimal('1.099,98', locale='de')
        assert decimal.Decimal('1099.98') == numbers.parse_decimal('1,099.98', locale='ar', numbering_system="default")
        assert decimal.Decimal('1099.98') == numbers.parse_decimal('1٬099٫98', locale='ar_EG', numbering_system="default")
        with pytest.raises(numbers.NumberFormatError):
            numbers.parse_decimal('2,109,998', locale='de')
        with pytest.raises(numbers.UnsupportedNumberingSystemError):
            numbers.parse_decimal('2,109,998', locale='de', numbering_system="unknown")

    def test_parse_decimal_strict_mode(self):
        # Numbers with a misplaced grouping symbol should be rejected
        with pytest.raises(numbers.NumberFormatError) as info:
            numbers.parse_decimal('11.11', locale='de', strict=True)
        assert info.value.suggestions == ['1.111', '11,11']
        # Numbers with two misplaced grouping symbols should be rejected
        with pytest.raises(numbers.NumberFormatError) as info:
            numbers.parse_decimal('80.00.00', locale='de', strict=True)
        assert info.value.suggestions == ['800.000']
        # Partially grouped numbers should be rejected
        with pytest.raises(numbers.NumberFormatError) as info:
            numbers.parse_decimal('2000,000', locale='en_US', strict=True)
        assert info.value.suggestions == ['2,000,000', '2,000']
        # Numbers with duplicate grouping symbols should be rejected
        with pytest.raises(numbers.NumberFormatError) as info:
            numbers.parse_decimal('0,,000', locale='en_US', strict=True)
        assert info.value.suggestions == ['0']
        # Return only suggestion for 0 on strict
        with pytest.raises(numbers.NumberFormatError) as info:
            numbers.parse_decimal('0.00', locale='de', strict=True)
        assert info.value.suggestions == ['0']
        # Properly formatted numbers should be accepted
        assert str(numbers.parse_decimal('1.001', locale='de', strict=True)) == '1001'
        # Trailing zeroes should be accepted
        assert str(numbers.parse_decimal('3.00', locale='en_US', strict=True)) == '3.00'
        # Numbers with a grouping symbol and no trailing zeroes should be accepted
        assert str(numbers.parse_decimal('3,400.6', locale='en_US', strict=True)) == '3400.6'
        # Numbers with a grouping symbol and trailing zeroes (not all zeroes after decimal) should be accepted
        assert str(numbers.parse_decimal('3,400.60', locale='en_US', strict=True)) == '3400.60'
        # Numbers with a grouping symbol and trailing zeroes (all zeroes after decimal) should be accepted
        assert str(numbers.parse_decimal('3,400.00', locale='en_US', strict=True)) == '3400.00'
        assert str(numbers.parse_decimal('3,400.0000', locale='en_US', strict=True)) == '3400.0000'
        # Numbers with a grouping symbol and no decimal part should be accepted
        assert str(numbers.parse_decimal('3,800', locale='en_US', strict=True)) == '3800'
        # Numbers without any grouping symbol should be accepted
        assert str(numbers.parse_decimal('2000.1', locale='en_US', strict=True)) == '2000.1'
        # Numbers without any grouping symbol and no decimal should be accepted
        assert str(numbers.parse_decimal('2580', locale='en_US', strict=True)) == '2580'
        # High precision numbers should be accepted
        assert str(numbers.parse_decimal('5,000001', locale='fr', strict=True)) == '5.000001'


def test_list_currencies():
    assert isinstance(list_currencies(), set)
    assert list_currencies().issuperset(['BAD', 'BAM', 'KRO'])

    assert isinstance(list_currencies(locale='fr'), set)
    assert list_currencies('fr').issuperset(['BAD', 'BAM', 'KRO'])

    with pytest.raises(ValueError, match="expected only letters, got 'yo!'"):
        list_currencies('yo!')

    assert list_currencies(locale='pa_Arab') == {'PKR', 'INR', 'EUR'}

    assert len(list_currencies()) == 307


def test_validate_currency():
    validate_currency('EUR')

    with pytest.raises(UnknownCurrencyError, match="Unknown currency 'FUU'."):
        validate_currency('FUU')


def test_is_currency():
    assert is_currency('EUR')
    assert not is_currency('eUr')
    assert not is_currency('FUU')
    assert not is_currency('')
    assert not is_currency(None)
    assert not is_currency('   EUR    ')
    assert not is_currency('   ')
    assert not is_currency([])
    assert not is_currency(set())


def test_normalize_currency():
    assert normalize_currency('EUR') == 'EUR'
    assert normalize_currency('eUr') == 'EUR'
    assert normalize_currency('FUU') is None
    assert normalize_currency('') is None
    assert normalize_currency(None) is None
    assert normalize_currency('   EUR    ') is None
    assert normalize_currency('   ') is None
    assert normalize_currency([]) is None
    assert normalize_currency(set()) is None


def test_get_currency_name():
    assert numbers.get_currency_name('USD', locale='en_US') == 'US Dollar'
    assert numbers.get_currency_name('USD', count=2, locale='en_US') == 'US dollars'


def test_get_currency_symbol():
    assert numbers.get_currency_symbol('USD', 'en_US') == '$'


def test_get_currency_precision():
    assert get_currency_precision('EUR') == 2
    assert get_currency_precision('JPY') == 0


def test_get_currency_unit_pattern():
    assert get_currency_unit_pattern('USD', locale='en_US') == '{0} {1}'
    assert get_currency_unit_pattern('USD', locale='sw') == '{1} {0}'

    # 'ro' locale various pattern according to count
    assert get_currency_unit_pattern('USD', locale='ro', count=1) == '{0} {1}'
    assert get_currency_unit_pattern('USD', locale='ro', count=2) == '{0} {1}'
    assert get_currency_unit_pattern('USD', locale='ro', count=100) == '{0} de {1}'
    assert get_currency_unit_pattern('USD', locale='ro') == '{0} de {1}'


def test_get_territory_currencies():
    assert numbers.get_territory_currencies('AT', date(1995, 1, 1)) == ['ATS']
    assert numbers.get_territory_currencies('AT', date(2011, 1, 1)) == ['EUR']

    assert numbers.get_territory_currencies('US', date(2013, 1, 1)) == ['USD']
    assert sorted(numbers.get_territory_currencies('US', date(2013, 1, 1),
                                                   non_tender=True)) == ['USD', 'USN', 'USS']

    assert numbers.get_territory_currencies('US', date(2013, 1, 1),
                                            include_details=True) == [{
                                                'currency': 'USD',
                                                'from': date(1792, 1, 1),
                                                'to': None,
                                                'tender': True,
                                            }]

    assert numbers.get_territory_currencies('LS', date(2013, 1, 1)) == ['ZAR', 'LSL']

    assert numbers.get_territory_currencies('QO', date(2013, 1, 1)) == []

    # Croatia uses Euro starting in January 2023; this is in CLDR 42.
    # See https://github.com/python-babel/babel/issues/942
    assert 'EUR' in numbers.get_territory_currencies('HR', date(2023, 1, 1))


def test_get_decimal_symbol():
    assert numbers.get_decimal_symbol('en_US') == '.'
    assert numbers.get_decimal_symbol('en_US', numbering_system="default") == '.'
    assert numbers.get_decimal_symbol('en_US', numbering_system="latn") == '.'
    assert numbers.get_decimal_symbol('sv_SE') == ','
    assert numbers.get_decimal_symbol('ar_EG') == '.'
    assert numbers.get_decimal_symbol('ar_EG', numbering_system="default") == '٫'
    assert numbers.get_decimal_symbol('ar_EG', numbering_system="latn") == '.'
    assert numbers.get_decimal_symbol('ar_EG', numbering_system="arab") == '٫'


def test_get_plus_sign_symbol():
    assert numbers.get_plus_sign_symbol('en_US') == '+'
    assert numbers.get_plus_sign_symbol('en_US', numbering_system="default") == '+'
    assert numbers.get_plus_sign_symbol('en_US', numbering_system="latn") == '+'
    assert numbers.get_plus_sign_symbol('ar_EG') == '\u200e+'
    assert numbers.get_plus_sign_symbol('ar_EG', numbering_system="default") == '\u061c+'
    assert numbers.get_plus_sign_symbol('ar_EG', numbering_system="arab") == '\u061c+'
    assert numbers.get_plus_sign_symbol('ar_EG', numbering_system="latn") == '\u200e+'


def test_get_minus_sign_symbol():
    assert numbers.get_minus_sign_symbol('en_US') == '-'
    assert numbers.get_minus_sign_symbol('en_US', numbering_system="default") == '-'
    assert numbers.get_minus_sign_symbol('en_US', numbering_system="latn") == '-'
    assert numbers.get_minus_sign_symbol('nl_NL') == '-'
    assert numbers.get_minus_sign_symbol('ar_EG') == '\u200e-'
    assert numbers.get_minus_sign_symbol('ar_EG', numbering_system="default") == '\u061c-'
    assert numbers.get_minus_sign_symbol('ar_EG', numbering_system="arab") == '\u061c-'
    assert numbers.get_minus_sign_symbol('ar_EG', numbering_system="latn") == '\u200e-'


def test_get_exponential_symbol():
    assert numbers.get_exponential_symbol('en_US') == 'E'
    assert numbers.get_exponential_symbol('en_US', numbering_system="latn") == 'E'
    assert numbers.get_exponential_symbol('en_US', numbering_system="default") == 'E'
    assert numbers.get_exponential_symbol('ja_JP') == 'E'
    assert numbers.get_exponential_symbol('ar_EG') == 'E'
    assert numbers.get_exponential_symbol('ar_EG', numbering_system="default") == 'أس'
    assert numbers.get_exponential_symbol('ar_EG', numbering_system="arab") == 'أس'
    assert numbers.get_exponential_symbol('ar_EG', numbering_system="latn") == 'E'


def test_get_group_symbol():
    assert numbers.get_group_symbol('en_US') == ','
    assert numbers.get_group_symbol('en_US', numbering_system="latn") == ','
    assert numbers.get_group_symbol('en_US', numbering_system="default") == ','
    assert numbers.get_group_symbol('ar_EG') == ','
    assert numbers.get_group_symbol('ar_EG', numbering_system="default") == '٬'
    assert numbers.get_group_symbol('ar_EG', numbering_system="arab") == '٬'
    assert numbers.get_group_symbol('ar_EG', numbering_system="latn") == ','


def test_get_infinity_symbol():
    assert numbers.get_infinity_symbol('en_US') == '∞'
    assert numbers.get_infinity_symbol('ar_EG', numbering_system="latn") == '∞'
    assert numbers.get_infinity_symbol('ar_EG', numbering_system="default") == '∞'
    assert numbers.get_infinity_symbol('ar_EG', numbering_system="arab") == '∞'


def test_decimal_precision():
    assert get_decimal_precision(decimal.Decimal('0.110')) == 2
    assert get_decimal_precision(decimal.Decimal('1.0')) == 0
    assert get_decimal_precision(decimal.Decimal('10000')) == 0


def test_format_decimal():
    assert numbers.format_decimal(1099, locale='en_US') == '1,099'
    assert numbers.format_decimal(1099, locale='de_DE') == '1.099'
    assert numbers.format_decimal(1.2345, locale='en_US') == '1.234'
    assert numbers.format_decimal(1.2346, locale='en_US') == '1.235'
    assert numbers.format_decimal(-1.2346, locale='en_US') == '-1.235'
    assert numbers.format_decimal(1.2345, locale='sv_SE') == '1,234'
    assert numbers.format_decimal(1.2345, locale='de') == '1,234'
    assert numbers.format_decimal(12345.5, locale='en_US') == '12,345.5'
    assert numbers.format_decimal(0001.2345000, locale='en_US') == '1.234'
    assert numbers.format_decimal(-0001.2346000, locale='en_US') == '-1.235'
    assert numbers.format_decimal(0000000.5, locale='en_US') == '0.5'
    assert numbers.format_decimal(000, locale='en_US') == '0'

    assert numbers.format_decimal(12345.5, locale='ar_EG') == '12,345.5'
    assert numbers.format_decimal(12345.5, locale='ar_EG', numbering_system="default") == '12٬345٫5'
    assert numbers.format_decimal(12345.5, locale='ar_EG', numbering_system="arab") == '12٬345٫5'

    with pytest.raises(numbers.UnsupportedNumberingSystemError):
        numbers.format_decimal(12345.5, locale='en_US', numbering_system="unknown")


@pytest.mark.parametrize('input_value, expected_value', [
    ('10000', '10,000'),
    ('1', '1'),
    ('1.0', '1'),
    ('1.1', '1.1'),
    ('1.11', '1.11'),
    ('1.110', '1.11'),
    ('1.001', '1.001'),
    ('1.00100', '1.001'),
    ('01.00100', '1.001'),
    ('101.00100', '101.001'),
    ('00000', '0'),
    ('0', '0'),
    ('0.0', '0'),
    ('0.1', '0.1'),
    ('0.11', '0.11'),
    ('0.110', '0.11'),
    ('0.001', '0.001'),
    ('0.00100', '0.001'),
    ('00.00100', '0.001'),
    ('000.00100', '0.001'),
])
def test_format_decimal_precision(input_value, expected_value):
    # Test precision conservation.
    assert numbers.format_decimal(
        decimal.Decimal(input_value), locale='en_US', decimal_quantization=False) == expected_value


def test_format_decimal_quantization():
    # Test all locales.
    for locale_code in localedata.locale_identifiers():
        assert numbers.format_decimal(
            '0.9999999999', locale=locale_code, decimal_quantization=False).endswith('9999999999') is True


def test_format_currency():
    assert (numbers.format_currency(1099.98, 'USD', locale='en_US')
            == '$1,099.98')
    assert (numbers.format_currency(1099.98, 'USD', locale='en_US', numbering_system="default")
            == '$1,099.98')
    assert (numbers.format_currency(0, 'USD', locale='en_US')
            == '$0.00')
    assert (numbers.format_currency(1099.98, 'USD', locale='es_CO')
            == 'US$1.099,98')
    assert (numbers.format_currency(1099.98, 'EUR', locale='de_DE')
            == '1.099,98\xa0\u20ac')
    assert (numbers.format_currency(1099.98, 'USD', locale='ar_EG', numbering_system="default")
            == '\u200f1٬099٫98\xa0US$')
    assert (numbers.format_currency(1099.98, 'EUR', '\xa4\xa4 #,##0.00',
                                    locale='en_US')
            == 'EUR 1,099.98')
    assert (numbers.format_currency(1099.98, 'EUR', locale='nl_NL')
            != numbers.format_currency(-1099.98, 'EUR', locale='nl_NL'))
    assert (numbers.format_currency(1099.98, 'USD', format=None,
                                    locale='en_US')
            == '$1,099.98')
    assert (numbers.format_currency(1, 'USD', locale='es_AR')
            == 'US$1,00')          # one
    assert (numbers.format_currency(1000000, 'USD', locale='es_AR')
            == 'US$1.000.000,00')  # many
    assert (numbers.format_currency(0, 'USD', locale='es_AR')
            == 'US$0,00')          # other


def test_format_currency_format_type():
    assert (numbers.format_currency(1099.98, 'USD', locale='en_US',
                                    format_type="standard")
            == '$1,099.98')
    assert (numbers.format_currency(0, 'USD', locale='en_US',
                                    format_type="standard")
            == '$0.00')

    assert (numbers.format_currency(1099.98, 'USD', locale='en_US',
                                    format_type="accounting")
            == '$1,099.98')
    assert (numbers.format_currency(0, 'USD', locale='en_US',
                                    format_type="accounting")
            == '$0.00')

    with pytest.raises(numbers.UnknownCurrencyFormatError, match="'unknown' is not a known currency format type"):
        numbers.format_currency(1099.98, 'USD', locale='en_US', format_type='unknown')

    assert (numbers.format_currency(1099.98, 'JPY', locale='en_US')
            == '\xa51,100')
    assert (numbers.format_currency(1099.98, 'COP', '#,##0.00', locale='es_ES')
            == '1.099,98')
    assert (numbers.format_currency(1099.98, 'JPY', locale='en_US',
                                    currency_digits=False)
            == '\xa51,099.98')
    assert (numbers.format_currency(1099.98, 'COP', '#,##0.00', locale='es_ES',
                                    currency_digits=False)
            == '1.099,98')


def test_format_compact_currency():
    assert numbers.format_compact_currency(1, 'USD', locale='en_US', format_type="short") == '$1'
    assert numbers.format_compact_currency(999, 'USD', locale='en_US', format_type="short") == '$999'
    assert numbers.format_compact_currency(123456789, 'USD', locale='en_US', format_type="short") == '$123M'
    assert numbers.format_compact_currency(123456789, 'USD', locale='en_US', fraction_digits=2, format_type="short") == '$123.46M'
    assert numbers.format_compact_currency(123456789, 'USD', locale='en_US', fraction_digits=2, format_type="short", numbering_system="default") == '$123.46M'
    assert numbers.format_compact_currency(-123456789, 'USD', locale='en_US', fraction_digits=2, format_type="short") == '-$123.46M'
    assert numbers.format_compact_currency(1, 'JPY', locale='ja_JP', format_type="short") == '￥1'
    assert numbers.format_compact_currency(1234, 'JPY', locale='ja_JP', format_type="short") == '￥1234'
    assert numbers.format_compact_currency(123456, 'JPY', locale='ja_JP', format_type="short") == '￥12万'
    assert numbers.format_compact_currency(123456, 'JPY', locale='ja_JP', format_type="short", fraction_digits=2) == '￥12.35万'
    assert numbers.format_compact_currency(123, 'EUR', locale='yav', format_type="short") == '€\xa0123'
    assert numbers.format_compact_currency(12345, 'EUR', locale='yav', format_type="short") == '€\xa012K'
    assert numbers.format_compact_currency(123456789, 'EUR', locale='de_DE', fraction_digits=1) == '123,5\xa0Mio.\xa0€'
    assert numbers.format_compact_currency(123456789, 'USD', locale='ar_EG', fraction_digits=2, format_type="short", numbering_system="default") == '123٫46\xa0مليون\xa0US$'


def test_format_compact_currency_invalid_format_type():
    with pytest.raises(numbers.UnknownCurrencyFormatError):
        numbers.format_compact_currency(1099.98, 'USD', locale='en_US', format_type='unknown')


@pytest.mark.parametrize('input_value, expected_value', [
    ('10000', '$10,000.00'),
    ('1', '$1.00'),
    ('1.0', '$1.00'),
    ('1.1', '$1.10'),
    ('1.11', '$1.11'),
    ('1.110', '$1.11'),
    ('1.001', '$1.001'),
    ('1.00100', '$1.001'),
    ('01.00100', '$1.001'),
    ('101.00100', '$101.001'),
    ('00000', '$0.00'),
    ('0', '$0.00'),
    ('0.0', '$0.00'),
    ('0.1', '$0.10'),
    ('0.11', '$0.11'),
    ('0.110', '$0.11'),
    ('0.001', '$0.001'),
    ('0.00100', '$0.001'),
    ('00.00100', '$0.001'),
    ('000.00100', '$0.001'),
])
def test_format_currency_precision(input_value, expected_value):
    # Test precision conservation.
    assert numbers.format_currency(
        decimal.Decimal(input_value),
        currency='USD',
        locale='en_US',
        decimal_quantization=False,
    ) == expected_value


def test_format_currency_quantization():
    # Test all locales.
    for locale_code in localedata.locale_identifiers():
        assert numbers.format_currency(
            '0.9999999999', 'USD', locale=locale_code, decimal_quantization=False).find('9999999999') > -1


def test_format_currency_long_display_name():
    assert (numbers.format_currency(1099.98, 'USD', locale='en_US', format_type='name')
            == '1,099.98 US dollars')
    assert (numbers.format_currency(1099.98, 'USD', locale='en_US', format_type='name', numbering_system="default")
            == '1,099.98 US dollars')
    assert (numbers.format_currency(1099.98, 'USD', locale='ar_EG', format_type='name', numbering_system="default")
            == '1٬099٫98 دولار أمريكي')
    assert (numbers.format_currency(1.00, 'USD', locale='en_US', format_type='name')
            == '1.00 US dollar')
    assert (numbers.format_currency(1.00, 'EUR', locale='en_US', format_type='name')
            == '1.00 euro')
    assert (numbers.format_currency(2, 'EUR', locale='en_US', format_type='name')
            == '2.00 euros')
    # This tests that '{1} {0}' unitPatterns are found:
    assert (numbers.format_currency(150, 'USD', locale='sw', format_type='name')
            == 'dola za Marekani 150.00')
    assert (numbers.format_currency(1, 'USD', locale='sw', format_type='name')
            == '1.00 dola ya Marekani')
    # This tests unicode chars:
    assert (numbers.format_currency(1099.98, 'USD', locale='es_GT', format_type='name')
            == '1,099.98 dólares estadounidenses')
    # Test for completely unknown currency, should fallback to currency code
    assert (numbers.format_currency(1099.98, 'XAB', locale='en_US', format_type='name')
            == '1,099.98 XAB')

    # Test for finding different unit patterns depending on count
    assert (numbers.format_currency(1, 'USD', locale='ro', format_type='name')
            == '1,00 dolar american')
    assert (numbers.format_currency(2, 'USD', locale='ro', format_type='name')
            == '2,00 dolari americani')
    assert (numbers.format_currency(100, 'USD', locale='ro', format_type='name')
            == '100,00 de dolari americani')


def test_format_currency_long_display_name_all():
    for locale_code in localedata.locale_identifiers():
        assert numbers.format_currency(
            1, 'USD', locale=locale_code, format_type='name').find('1') > -1
        assert numbers.format_currency(
            '1', 'USD', locale=locale_code, format_type='name').find('1') > -1


def test_format_currency_long_display_name_custom_format():
    assert (numbers.format_currency(1099.98, 'USD', locale='en_US',
                                    format_type='name', format='##0')
            == '1099.98 US dollars')
    assert (numbers.format_currency(1099.98, 'USD', locale='en_US',
                                    format_type='name', format='##0',
                                    currency_digits=False)
            == '1100 US dollars')


def test_format_percent():
    assert numbers.format_percent(0.34, locale='en_US') == '34%'
    assert numbers.format_percent(0.34, locale='en_US', numbering_system="default") == '34%'
    assert numbers.format_percent(0, locale='en_US') == '0%'
    assert numbers.format_percent(0.34, '##0%', locale='en_US') == '34%'
    assert numbers.format_percent(34, '##0', locale='en_US') == '34'
    assert numbers.format_percent(25.1234, locale='en_US') == '2,512%'
    assert (numbers.format_percent(25.1234, locale='sv_SE')
            == '2\xa0512\xa0%')
    assert (numbers.format_percent(25.1234, '#,##0\u2030', locale='en_US')
            == '25,123\u2030')
    assert numbers.format_percent(134.5, locale='ar_EG', numbering_system="default") == '13٬450%'



@pytest.mark.parametrize('input_value, expected_value', [
    ('100', '10,000%'),
    ('0.01', '1%'),
    ('0.010', '1%'),
    ('0.011', '1.1%'),
    ('0.0111', '1.11%'),
    ('0.01110', '1.11%'),
    ('0.01001', '1.001%'),
    ('0.0100100', '1.001%'),
    ('0.010100100', '1.01001%'),
    ('0.000000', '0%'),
    ('0', '0%'),
    ('0.00', '0%'),
    ('0.01', '1%'),
    ('0.011', '1.1%'),
    ('0.0110', '1.1%'),
    ('0.0001', '0.01%'),
    ('0.000100', '0.01%'),
    ('0.0000100', '0.001%'),
    ('0.00000100', '0.0001%'),
])
def test_format_percent_precision(input_value, expected_value):
    # Test precision conservation.
    assert numbers.format_percent(
        decimal.Decimal(input_value), locale='en_US', decimal_quantization=False) == expected_value


def test_format_percent_quantization():
    # Test all locales.
    for locale_code in localedata.locale_identifiers():
        assert numbers.format_percent(
            '0.9999999999', locale=locale_code, decimal_quantization=False).find('99999999') > -1


def test_format_scientific():
    assert numbers.format_scientific(10000, locale='en_US') == '1E4'
    assert numbers.format_scientific(10000, locale='en_US', numbering_system="default") == '1E4'
    assert numbers.format_scientific(4234567, '#.#E0', locale='en_US') == '4.2E6'
    assert numbers.format_scientific(4234567, '0E0000', locale='en_US') == '4.234567E0006'
    assert numbers.format_scientific(4234567, '##0E00', locale='en_US') == '4.234567E06'
    assert numbers.format_scientific(4234567, '##00E00', locale='en_US') == '42.34567E05'
    assert numbers.format_scientific(4234567, '0,000E00', locale='en_US') == '4,234.567E03'
    assert numbers.format_scientific(4234567, '##0.#####E00', locale='en_US') == '4.23457E06'
    assert numbers.format_scientific(4234567, '##0.##E00', locale='en_US') == '4.23E06'
    assert numbers.format_scientific(42, '00000.000000E0000', locale='en_US') == '42000.000000E-0003'
    assert numbers.format_scientific(0.2, locale="ar_EG", numbering_system="default") == '2أس\u061c-1'


def test_default_scientific_format():
    """ Check the scientific format method auto-correct the rendering pattern
    in case of a missing fractional part.
    """
    assert numbers.format_scientific(12345, locale='en_US') == '1.2345E4'
    assert numbers.format_scientific(12345.678, locale='en_US') == '1.2345678E4'
    assert numbers.format_scientific(12345, '#E0', locale='en_US') == '1.2345E4'
    assert numbers.format_scientific(12345.678, '#E0', locale='en_US') == '1.2345678E4'


@pytest.mark.parametrize('input_value, expected_value', [
    ('10000', '1E4'),
    ('1', '1E0'),
    ('1.0', '1E0'),
    ('1.1', '1.1E0'),
    ('1.11', '1.11E0'),
    ('1.110', '1.11E0'),
    ('1.001', '1.001E0'),
    ('1.00100', '1.001E0'),
    ('01.00100', '1.001E0'),
    ('101.00100', '1.01001E2'),
    ('00000', '0E0'),
    ('0', '0E0'),
    ('0.0', '0E0'),
    ('0.1', '1E-1'),
    ('0.11', '1.1E-1'),
    ('0.110', '1.1E-1'),
    ('0.001', '1E-3'),
    ('0.00100', '1E-3'),
    ('00.00100', '1E-3'),
    ('000.00100', '1E-3'),
])
def test_format_scientific_precision(input_value, expected_value):
    # Test precision conservation.
    assert numbers.format_scientific(
        decimal.Decimal(input_value), locale='en_US', decimal_quantization=False) == expected_value


def test_format_scientific_quantization():
    # Test all locales.
    for locale_code in localedata.locale_identifiers():
        assert numbers.format_scientific(
            '0.9999999999', locale=locale_code, decimal_quantization=False).find('999999999') > -1


def test_parse_number():
    assert numbers.parse_number('1,099', locale='en_US') == 1099
    assert numbers.parse_number('1.099', locale='de_DE') == 1099
    assert numbers.parse_number('1٬099', locale='ar_EG', numbering_system="default") == 1099

    with pytest.raises(numbers.NumberFormatError, match="'1.099,98' is not a valid number"):
        numbers.parse_number('1.099,98', locale='de')

    with pytest.raises(numbers.UnsupportedNumberingSystemError):
        numbers.parse_number('1.099,98', locale='en', numbering_system="unsupported")


@pytest.mark.parametrize('string', [
    '1 099',
    '1\xa0099',
    '1\u202f099',
])
def test_parse_number_group_separator_can_be_any_space(string):
    assert numbers.parse_number(string, locale='fr') == 1099


def test_parse_decimal():
    assert (numbers.parse_decimal('1,099.98', locale='en_US')
            == decimal.Decimal('1099.98'))
    assert numbers.parse_decimal('1.099,98', locale='de') == decimal.Decimal('1099.98')

    with pytest.raises(numbers.NumberFormatError, match="'2,109,998' is not a valid decimal number"):
        numbers.parse_decimal('2,109,998', locale='de')


@pytest.mark.parametrize('string', [
    '1 099,98',
    '1\xa0099,98',
    '1\u202f099,98',
])
def test_parse_decimal_group_separator_can_be_any_space(string):
    assert decimal.Decimal('1099.98') == numbers.parse_decimal(string, locale='fr')


def test_parse_grouping():
    assert numbers.parse_grouping('##') == (1000, 1000)
    assert numbers.parse_grouping('#,###') == (3, 3)
    assert numbers.parse_grouping('#,####,###') == (3, 4)


def test_parse_pattern():

    # Original pattern is preserved
    np = numbers.parse_pattern('¤#,##0.00')
    assert np.pattern == '¤#,##0.00'

    np = numbers.parse_pattern('¤#,##0.00;(¤#,##0.00)')
    assert np.pattern == '¤#,##0.00;(¤#,##0.00)'

    # Given a NumberPattern object, we don't return a new instance.
    # However, we don't cache NumberPattern objects, so calling
    # parse_pattern with the same format string will create new
    # instances
    np1 = numbers.parse_pattern('¤ #,##0.00')
    np2 = numbers.parse_pattern('¤ #,##0.00')
    assert np1 is not np2
    assert np1 is numbers.parse_pattern(np1)


def test_parse_pattern_negative():

    # No negative format specified
    np = numbers.parse_pattern('¤#,##0.00')
    assert np.prefix == ('¤', '-¤')
    assert np.suffix == ('', '')

    # Negative format is specified
    np = numbers.parse_pattern('¤#,##0.00;(¤#,##0.00)')
    assert np.prefix == ('¤', '(¤')
    assert np.suffix == ('', ')')

    # Negative sign is a suffix
    np = numbers.parse_pattern('¤ #,##0.00;¤ #,##0.00-')
    assert np.prefix == ('¤ ', '¤ ')
    assert np.suffix == ('', '-')


def test_numberpattern_repr():
    """repr() outputs the pattern string"""

    # This implementation looks a bit funny, but that's cause strings are
    # repr'd differently in Python 2 vs 3 and this test runs under both.
    format = '¤#,##0.00;(¤#,##0.00)'
    np = numbers.parse_pattern(format)
    assert repr(format) in repr(np)


def test_parse_static_pattern():
    assert numbers.parse_pattern('Kun')  # in the So locale in CLDR 30
    # TODO: static patterns might not be correctly `apply()`ed at present


def test_parse_decimal_nbsp_heuristics():
    # Re https://github.com/python-babel/babel/issues/637 –
    #    for locales (of which there are many) that use U+00A0 as the group
    #    separator in numbers, it's reasonable to assume that input strings
    #    with plain spaces actually should have U+00A0s instead.
    #    This heuristic is only applied when strict=False.
    n = decimal.Decimal("12345.123")
    assert numbers.parse_decimal("12 345.123", locale="fi") == n
    assert numbers.parse_decimal(numbers.format_decimal(n, locale="fi"), locale="fi") == n


def test_very_small_decimal_no_quantization():
    assert numbers.format_decimal(decimal.Decimal('1E-7'), locale='en', decimal_quantization=False) == '0.0000001'


def test_single_quotes_in_pattern():
    assert numbers.format_decimal(123, "'@0.#'00'@01'", locale='en') == '@0.#120@01'

    assert numbers.format_decimal(123, "'$'''0", locale='en') == "$'123"

    assert numbers.format_decimal(12, "'#'0 o''clock", locale='en') == "#12 o'clock"


def test_format_currency_with_none_locale_with_default(monkeypatch):
    """Test that the default locale is used when locale is None."""
    monkeypatch.setattr(numbers, "LC_MONETARY", "fi_FI")
    monkeypatch.setattr(numbers, "LC_NUMERIC", None)
    assert numbers.format_currency(0, "USD", locale=None) == "0,00\xa0$"


def test_format_currency_with_none_locale(monkeypatch):
    """Test that the API raises the "Empty locale identifier" error when locale is None, and the default is too."""
    monkeypatch.setattr(numbers, "LC_MONETARY", None)  # Pretend we couldn't find any locale when importing the module
    with pytest.raises(TypeError, match="Empty"):
        numbers.format_currency(0, "USD", locale=None)


def test_format_decimal_with_none_locale_with_default(monkeypatch):
    """Test that the default locale is used when locale is None."""
    monkeypatch.setattr(numbers, "LC_NUMERIC", "fi_FI")
    monkeypatch.setattr(numbers, "LC_MONETARY", None)
    assert numbers.format_decimal("1.23", locale=None) == "1,23"


def test_format_decimal_with_none_locale(monkeypatch):
    """Test that the API raises the "Empty locale identifier" error when locale is None, and the default is too."""
    monkeypatch.setattr(numbers, "LC_NUMERIC", None)  # Pretend we couldn't find any locale when importing the module
    with pytest.raises(TypeError, match="Empty"):
        numbers.format_decimal(0, locale=None)
