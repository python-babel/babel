# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2011 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

from decimal import Decimal
import unittest
import pytest

from babel import numbers


class FormatDecimalTestCase(unittest.TestCase):

    def test_patterns(self):
        self.assertEqual(numbers.format_decimal(12345, '##0',
                         locale='en_US'), '12345')
        self.assertEqual(numbers.format_decimal(6.5, '0.00', locale='sv'),
                         '6,50')
        self.assertEqual(numbers.format_decimal(10.0**20,
                                                '#.00', locale='en_US'),
                         '100000000000000000000.00')
        # regression test for #183, fraction digits were not correctly cutted
        # if the input was a float value and the value had more than 7
        # significant digits
        self.assertEqual(u'12,345,678.05',
                         numbers.format_decimal(12345678.051, '#,##0.00',
                         locale='en_US'))

    def test_subpatterns(self):
        self.assertEqual(numbers.format_decimal(-12345, '#,##0.##;-#',
                         locale='en_US'), '-12,345')
        self.assertEqual(numbers.format_decimal(-12345, '#,##0.##;(#)',
                         locale='en_US'), '(12,345)')

    def test_default_rounding(self):
        """
        Testing Round-Half-Even (Banker's rounding)

        A '5' is rounded to the closest 'even' number
        """
        self.assertEqual(numbers.format_decimal(5.5, '0', locale='sv'), '6')
        self.assertEqual(numbers.format_decimal(6.5, '0', locale='sv'), '6')
        self.assertEqual(numbers.format_decimal(6.5, '0', locale='sv'), '6')
        self.assertEqual(numbers.format_decimal(1.2325, locale='sv'), '1,232')
        self.assertEqual(numbers.format_decimal(1.2335, locale='sv'), '1,234')

    def test_significant_digits(self):
        """Test significant digits patterns"""
        self.assertEqual(numbers.format_decimal(123004, '@@',locale='en_US'),
                        '120000')
        self.assertEqual(numbers.format_decimal(1.12, '@', locale='sv'), '1')
        self.assertEqual(numbers.format_decimal(1.1, '@@', locale='sv'), '1,1')
        self.assertEqual(numbers.format_decimal(1.1, '@@@@@##', locale='sv'),
                         '1,1000')
        self.assertEqual(numbers.format_decimal(0.0001, '@@@', locale='sv'),
                         '0,000100')
        self.assertEqual(numbers.format_decimal(0.0001234, '@@@', locale='sv'),
                         '0,000123')
        self.assertEqual(numbers.format_decimal(0.0001234, '@@@#',locale='sv'),
                         '0,0001234')
        self.assertEqual(numbers.format_decimal(0.0001234, '@@@#',locale='sv'),
                         '0,0001234')
        self.assertEqual(numbers.format_decimal(0.12345, '@@@',locale='sv'),
                         '0,123')
        self.assertEqual(numbers.format_decimal(3.14159, '@@##',locale='sv'),
                         '3,142')
        self.assertEqual(numbers.format_decimal(1.23004, '@@##',locale='sv'),
                         '1,23')
        self.assertEqual(numbers.format_decimal(1230.04, '@@,@@',locale='en_US'),
                         '12,30')
        self.assertEqual(numbers.format_decimal(123.41, '@@##',locale='en_US'),
                         '123.4')
        self.assertEqual(numbers.format_decimal(1, '@@',locale='en_US'),
                         '1.0')
        self.assertEqual(numbers.format_decimal(0, '@',locale='en_US'),
                         '0')
        self.assertEqual(numbers.format_decimal(0.1, '@',locale='en_US'),
                         '0.1')
        self.assertEqual(numbers.format_decimal(0.1, '@#',locale='en_US'),
                         '0.1')
        self.assertEqual(numbers.format_decimal(0.1, '@@', locale='en_US'),
                         '0.10')

    def test_decimals(self):
        """Test significant digits patterns"""
        self.assertEqual(numbers.format_decimal(Decimal('1.2345'),
                                                '#.00', locale='en_US'),
                         '1.23')
        self.assertEqual(numbers.format_decimal(Decimal('1.2345000'),
                                                '#.00', locale='en_US'),
                         '1.23')
        self.assertEqual(numbers.format_decimal(Decimal('1.2345000'),
                                                '@@', locale='en_US'),
                         '1.2')
        self.assertEqual(numbers.format_decimal(Decimal('12345678901234567890.12345'),
                                                '#.00', locale='en_US'),
                         '12345678901234567890.12')

    def test_scientific_notation(self):
        fmt = numbers.format_scientific(0.1, '#E0', locale='en_US')
        self.assertEqual(fmt, '1E-1')
        fmt = numbers.format_scientific(0.01, '#E0', locale='en_US')
        self.assertEqual(fmt, '1E-2')
        fmt = numbers.format_scientific(10, '#E0', locale='en_US')
        self.assertEqual(fmt, '1E1')
        fmt = numbers.format_scientific(1234, '0.###E0', locale='en_US')
        self.assertEqual(fmt, '1.234E3')
        fmt = numbers.format_scientific(1234, '0.#E0', locale='en_US')
        self.assertEqual(fmt, '1.2E3')
        # Exponent grouping
        fmt = numbers.format_scientific(12345, '##0.####E0', locale='en_US')
        self.assertEqual(fmt, '12.345E3')
        # Minimum number of int digits
        fmt = numbers.format_scientific(12345, '00.###E0', locale='en_US')
        self.assertEqual(fmt, '12.345E3')
        fmt = numbers.format_scientific(-12345.6, '00.###E0', locale='en_US')
        self.assertEqual(fmt, '-12.346E3')
        fmt = numbers.format_scientific(-0.01234, '00.###E0', locale='en_US')
        self.assertEqual(fmt, '-12.34E-3')
        # Custom pattern suffic
        fmt = numbers.format_scientific(123.45, '#.##E0 m/s', locale='en_US')
        self.assertEqual(fmt, '1.23E2 m/s')
        # Exponent patterns
        fmt = numbers.format_scientific(123.45, '#.##E00 m/s', locale='en_US')
        self.assertEqual(fmt, '1.23E02 m/s')
        fmt = numbers.format_scientific(0.012345, '#.##E00 m/s', locale='en_US')
        self.assertEqual(fmt, '1.23E-02 m/s')
        fmt = numbers.format_scientific(Decimal('12345'), '#.##E+00 m/s',
        locale='en_US')
        self.assertEqual(fmt, '1.23E+04 m/s')
        # 0 (see ticket #99)
        fmt = numbers.format_scientific(0, '#E0', locale='en_US')
        self.assertEqual(fmt, '0E0')

    def test_formatting_of_very_small_decimals(self):
        # previously formatting very small decimals could lead to a type error
        # because the Decimal->string conversion was too simple (see #214)
        number = Decimal("7E-7")
        fmt = numbers.format_decimal(number, format="@@@", locale='en_US')
        self.assertEqual('0.000000700', fmt)


class BankersRoundTestCase(unittest.TestCase):
    def test_round_to_nearest_integer(self):
        self.assertEqual(1, numbers.bankersround(Decimal('0.5001')))

    def test_round_to_even_for_two_nearest_integers(self):
        self.assertEqual(0, numbers.bankersround(Decimal('0.5')))
        self.assertEqual(2, numbers.bankersround(Decimal('1.5')))
        self.assertEqual(-2, numbers.bankersround(Decimal('-2.5')))

        self.assertEqual(0, numbers.bankersround(Decimal('0.05'), ndigits=1))
        self.assertEqual(Decimal('0.2'), numbers.bankersround(Decimal('0.15'), ndigits=1))


class NumberParsingTestCase(unittest.TestCase):
    def test_can_parse_decimals(self):
        self.assertEqual(Decimal('1099.98'),
            numbers.parse_decimal('1,099.98', locale='en_US'))
        self.assertEqual(Decimal('1099.98'),
            numbers.parse_decimal('1.099,98', locale='de'))
        self.assertRaises(numbers.NumberFormatError,
                          lambda: numbers.parse_decimal('2,109,998', locale='de'))


def test_get_currency_name():
    assert numbers.get_currency_name('USD', locale='en_US') == u'US Dollar'
    assert numbers.get_currency_name('USD', count=2, locale='en_US') == u'US dollars'


def test_get_currency_symbol():
    assert numbers.get_currency_symbol('USD', 'en_US') == u'$'


def test_get_decimal_symbol():
    assert numbers.get_decimal_symbol('en_US') == u'.'


def test_get_plus_sign_symbol():
    assert numbers.get_plus_sign_symbol('en_US') == u'+'


def test_get_minus_sign_symbol():
    assert numbers.get_minus_sign_symbol('en_US') == u'-'


def test_get_exponential_symbol():
    assert numbers.get_exponential_symbol('en_US') == u'E'


def test_get_group_symbol():
    assert numbers.get_group_symbol('en_US') == u','


def test_format_number():
    assert numbers.format_number(1099, locale='en_US') == u'1,099'
    assert numbers.format_number(1099, locale='de_DE') == u'1.099'


def test_format_decimal():
    assert numbers.format_decimal(1.2345, locale='en_US') == u'1.234'
    assert numbers.format_decimal(1.2346, locale='en_US') == u'1.235'
    assert numbers.format_decimal(-1.2346, locale='en_US') == u'-1.235'
    assert numbers.format_decimal(1.2345, locale='sv_SE') == u'1,234'
    assert numbers.format_decimal(1.2345, locale='de') == u'1,234'
    assert numbers.format_decimal(12345.5, locale='en_US') == u'12,345.5'


def test_format_currency():
    assert (numbers.format_currency(1099.98, 'USD', locale='en_US')
            == u'$1,099.98')
    assert (numbers.format_currency(1099.98, 'USD', locale='es_CO')
            == u'1.099,98\xa0US$')
    assert (numbers.format_currency(1099.98, 'EUR', locale='de_DE')
            == u'1.099,98\xa0\u20ac')
    assert (numbers.format_currency(1099.98, 'EUR', u'\xa4\xa4 #,##0.00',
                                    locale='en_US')
            == u'EUR 1,099.98')


def test_format_percent():
    assert numbers.format_percent(0.34, locale='en_US') == u'34%'
    assert numbers.format_percent(25.1234, locale='en_US') == u'2,512%'
    assert (numbers.format_percent(25.1234, locale='sv_SE')
            == u'2\xa0512\xa0%')
    assert (numbers.format_percent(25.1234, u'#,##0\u2030', locale='en_US')
            == u'25,123\u2030')


def test_scientific_exponent_displayed_as_integer():
    assert numbers.format_scientific(100000, locale='en_US') == u'1E5'


def test_format_scientific():
    assert numbers.format_scientific(10000, locale='en_US') == u'1E4'
    assert (numbers.format_scientific(1234567, u'##0E00', locale='en_US')
            == u'1.23E06')


def test_parse_number():
    assert numbers.parse_number('1,099', locale='en_US') == 1099
    assert numbers.parse_number('1.099', locale='de_DE') == 1099

    with pytest.raises(numbers.NumberFormatError) as excinfo:
        numbers.parse_number('1.099,98', locale='de')
    assert excinfo.value.args[0] == "'1.099,98' is not a valid number"


def test_parse_decimal():
    assert (numbers.parse_decimal('1,099.98', locale='en_US')
            == Decimal('1099.98'))
    assert numbers.parse_decimal('1.099,98', locale='de') == Decimal('1099.98')

    with pytest.raises(numbers.NumberFormatError) as excinfo:
        numbers.parse_decimal('2,109,998', locale='de')
    assert excinfo.value.args[0] == "'2,109,998' is not a valid decimal number"


def test_bankersround():
    assert numbers.bankersround(5.5, 0) == 6.0
    assert numbers.bankersround(6.5, 0) == 6.0
    assert numbers.bankersround(-6.5, 0) == -6.0
    assert numbers.bankersround(1234.0, -2) == 1200.0


def test_parse_grouping():
    assert numbers.parse_grouping('##') == (1000, 1000)
    assert numbers.parse_grouping('#,###') == (3, 3)
    assert numbers.parse_grouping('#,####,###') == (3, 4)
