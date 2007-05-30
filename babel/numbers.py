# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

"""Locale dependent formatting and parsing of numeric data.

The default locale for the functions in this module is determined by the
following environment variables, in that order:

 * ``LC_NUMERIC``,
 * ``LC_ALL``, and
 * ``LANG``
"""
# TODO: percent and scientific formatting

import re

from babel.core import Locale
from babel.util import default_locale

__all__ = ['format_number', 'format_decimal', 'format_currency',
           'format_percent', 'format_scientific', 'parse_number',
           'parse_decimal']
__docformat__ = 'restructuredtext en'

LC_NUMERIC = default_locale('LC_NUMERIC')

def get_decimal_symbol(locale=LC_NUMERIC):
    """Return the symbol used by the locale to separate decimal fractions.
    
    >>> get_decimal_symbol('en_US')
    u'.'
    
    :param locale: the `Locale` object or locale identifier
    :return: the decimal symbol
    :rtype: `unicode`
    """
    return Locale.parse(locale).number_symbols.get('decimal', u'.')

def get_group_symbol(locale=LC_NUMERIC):
    """Return the symbol used by the locale to separate groups of thousands.
    
    >>> get_group_symbol('en_US')
    u','
    
    :param locale: the `Locale` object or locale identifier
    :return: the group symbol
    :rtype: `unicode`
    """
    return Locale.parse(locale).number_symbols.get('group', u',')

def format_number(number, locale=LC_NUMERIC):
    """Returns the given number formatted for a specific locale.
    
    >>> format_number(1099, locale='en_US')
    u'1,099'
    
    :param number: the number to format
    :param locale: the `Locale` object or locale identifier
    :return: the formatted number
    :rtype: `unicode`
    """
    # Do we really need this one?
    return format_decimal(number, locale=locale)

def format_decimal(number, format=None, locale=LC_NUMERIC):
    """Returns the given decimal number formatted for a specific locale.
    
    >>> format_decimal(1, locale='en_US')
    u'1'
    >>> format_decimal(1.2345, locale='en_US')
    u'1.234'
    >>> format_decimal(1.2345, locale='sv_SE')
    u'1,234'
    >>> format_decimal(12345, locale='de_DE')
    u'12.345'
    >>> format_decimal(-1.2345, format='#,##0.##;-#', locale='sv_SE')
    u'-1,23'
    >>> format_decimal(-1.2345, format='#,##0.##;(#)', locale='sv_SE')
    u'(1,23)'

    The appropriate thousands grouping and the decimal separator are used for
    each locale:
    
    >>> format_decimal(12345, locale='en_US')
    u'12,345'

    :param number: the number to format
    :param format: 
    :param locale: the `Locale` object or locale identifier
    :return: the formatted decimal number
    :rtype: `unicode`
    """
    locale = Locale.parse(locale)
    pattern = locale.decimal_formats.get(format)
    if not pattern:
        pattern = parse_pattern(format)
    return pattern.apply(number, locale)

def format_currency(value, locale=LC_NUMERIC):
    """Returns formatted currency value.
    
    >>> format_currency(1099.98, locale='en_US')
    u'1,099.98'
    
    :param value: the number to format
    :param locale: the `Locale` object or locale identifier
    :return: the formatted currency value
    :rtype: `unicode`
    """
    return format_decimal(value, locale=locale)

def format_percent(value, places=2, locale=LC_NUMERIC):
    raise NotImplementedError

def format_scientific(value, locale=LC_NUMERIC):
    raise NotImplementedError

def parse_number(string, locale=LC_NUMERIC):
    """Parse localized number string into a long integer.
    
    >>> parse_number('1,099', locale='en_US')
    1099L
    >>> parse_number('1.099', locale='de_DE')
    1099L
    
    :param string: the string to parse
    :param locale: the `Locale` object or locale identifier
    :return: the parsed number
    :rtype: `long`
    :raise `ValueError`: if the string can not be converted to a number
    """
    return long(string.replace(get_group_symbol(locale), ''))

def parse_decimal(string, locale=LC_NUMERIC):
    """Parse localized decimal string into a float.
    
    >>> parse_decimal('1,099.98', locale='en_US')
    1099.98
    >>> parse_decimal('1.099,98', locale='de_DE')
    1099.98
    
    :param string: the string to parse
    :param locale: the `Locale` object or locale identifier
    :return: the parsed decimal number
    :rtype: `float`
    :raise `ValueError`: if the string can not be converted to a decimal number
    """
    locale = Locale.parse(locale)
    string = string.replace(get_group_symbol(locale), '') \
                   .replace(get_decimal_symbol(locale), '.')
    return float(string)


PREFIX_END = r'[^0-9@#.,]'
NUMBER_TOKEN = r'[0-9@#.\-,E]'

PREFIX_PATTERN = r"(?P<prefix>(?:'[^']*'|%s)*)" % PREFIX_END
NUMBER_PATTERN = r"(?P<number>%s+)" % NUMBER_TOKEN
SUFFIX_PATTERN = r"(?P<suffix>.*)"

number_re = re.compile(r"%s%s%s" % (PREFIX_PATTERN, NUMBER_PATTERN, 
                                    SUFFIX_PATTERN))

# TODO:
#  Filling
#  Rounding
#  Scientific notation
#  Significant Digits
def parse_pattern(pattern):
    """Parse number format patterns"""
    if isinstance(pattern, NumberPattern):
        return pattern

    # Do we have a negative subpattern?
    if ';' in pattern:
        pattern, neg_pattern = pattern.split(';', 1)
        pos_prefix, number, pos_suffix = number_re.search(pattern).groups()
        neg_prefix, _, neg_suffix = number_re.search(neg_pattern).groups()
    else:
        pos_prefix, number, pos_suffix = number_re.search(pattern).groups()
        neg_prefix = '-' + pos_prefix
        neg_suffix = pos_suffix
    integer, fraction = number.rsplit('.', 1)
    min_frac = max_frac = 0

    def parse_precision(p):
        """Calculate the min and max allowed digits"""
        min = max = 0
        for c in p:
            if c == '0':
                min += 1
                max += 1
            elif c == '#':
                max += 1
            else:
                break
        return min, max

    def parse_grouping(p):
        """Parse primary and secondary digit grouping

        >>> parse_grouping('##')
        0, 0
        >>> parse_grouping('#,###')
        3, 3
        >>> parse_grouping('#,####,###')
        3, 4
        """
        width = len(p)
        g1 = p.rfind(',')
        if g1 == -1:
            return 1000, 1000
        g1 = width - g1 - 1
        g2 = p[:-g1 - 1].rfind(',')
        if g2 == -1:
            return g1, g1
        g2 = width - g1 - g2 - 2
        return g1, g2

    int_precision = parse_precision(integer)
    frac_precision = parse_precision(fraction)
    grouping = parse_grouping(integer)
    int_precision = (int_precision[0], 1000) # Unlimited
    return NumberPattern(pattern, (pos_prefix, neg_prefix), 
                         (pos_suffix, neg_suffix), grouping,
                         int_precision, frac_precision)


class NumberPattern(object):
    def __init__(self, pattern, prefix, suffix, grouping,
                 int_precision, frac_precision):
        self.pattern = pattern
        self.prefix = prefix
        self.suffix = suffix
        self.grouping = grouping
        self.int_precision = int_precision
        self.frac_precision = frac_precision

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.pattern)

    def apply(self, value, locale):
        negative = int(value < 0)
        a, b = str(value * 1.0).split('.')
        a = a.lstrip('-')
        return '%s%s%s%s' % (self.prefix[negative], 
                             self._format_int(a, locale), 
                             self._format_frac(b, locale),
                             self.suffix[negative])

    def _format_int(self, value, locale):
        min, max = self.int_precision
        width = len(value)
        if width < min:
            value += '0' * (min - width)
        gsize = self.grouping[0]
        ret = ''
        symbol = get_group_symbol(locale)
        while len(value) > gsize:
            ret = symbol + value[-gsize:] + ret
            value = value[:-gsize]
            gsize = self.grouping[1]
        return value + ret

    def _format_frac(self, value, locale):
        min, max = self.frac_precision
        if min == 0 and int(value) == 0:
            return ''
        width = len(value)
        if width < min:
            value += '0' * (min - width)
        if width > max:
            value = value[:max] # FIXME: Rounding?!?
        return get_decimal_symbol(locale) + value
