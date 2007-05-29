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
    return Locale.parse(locale).number_symbols.get('group', u'.')

def format_number(number, locale=LC_NUMERIC):
    """Returns the given number formatted for a specific locale.
    
    >>> format_number(1099, locale='en_US')
    u'1,099'
    
    :param number: the number to format
    :param locale: the `Locale` object or locale identifier
    :return: the formatted number
    :rtype: `unicode`
    """
    group = get_group_symbol(locale)
    if not group:
        return unicode(number)
    thou = re.compile(r'([0-9])([0-9][0-9][0-9]([%s]|$))' % group).search
    v = str(number)
    mo = thou(v)
    while mo is not None:
        l = mo.start(0)
        v = v[:l+1] + group + v[l+1:]
        mo = thou(v)
    return unicode(v)

def format_decimal(number, places=2, locale=LC_NUMERIC):
    """Returns the given decimal number formatted for a specific locale.
    
    >>> format_decimal(1099.98, locale='en_US')
    u'1,099.98'
    
    The appropriate thousands grouping and the decimal separator are used for
    each locale:
    
    >>> format_decimal(1099.98, locale='de_DE')
    u'1.099,98'
    
    The number of decimal places defaults to 2, but can also be specified
    explicitly:
    
    >>> format_decimal(1099.98, places=4, locale='en_US')
    u'1,099.9800'
    
    :param number: the number to format
    :param places: the number of digit behind the decimal point
    :param locale: the `Locale` object or locale identifier
    :return: the formatted decimal number
    :rtype: `unicode`
    """
    locale = Locale.parse(locale)
    a, b = (('%%.%df' % places) % number).split('.')
    return unicode(format_number(a, locale) + get_decimal_symbol(locale) + b)

def format_currency(value, locale=LC_NUMERIC):
    """Returns formatted currency value.
    
    >>> format_currency(1099.98, locale='en_US')
    u'1,099.98'
    
    :param value: the number to format
    :param locale: the `Locale` object or locale identifier
    :return: the formatted currency value
    :rtype: `unicode`
    """
    return format_decimal(value, places=2, locale=locale)

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
