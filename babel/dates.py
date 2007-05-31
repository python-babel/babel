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

"""Locale dependent formatting and parsing of dates and times.

The default locale for the functions in this module is determined by the
following environment variables, in that order:

 * ``LC_TIME``,
 * ``LC_ALL``, and
 * ``LANG``
"""

from datetime import date, datetime, time

from babel.core import Locale
from babel.util import default_locale

__all__ = ['format_date', 'format_datetime', 'format_time', 'parse_date',
           'parse_datetime', 'parse_time']
__docformat__ = 'restructuredtext en'

LC_TIME = default_locale('LC_TIME')

def get_period_names(locale=LC_TIME):
    """Return the names for day periods (AM/PM) used by the locale.
    
    >>> get_period_names(locale='en_US')['am']
    u'AM'
    
    :param locale: the `Locale` object, or a locale string
    :return: the dictionary of period names
    :rtype: `dict`
    """
    return Locale.parse(locale).periods

def get_day_names(width='wide', context='format', locale=LC_TIME):
    """Return the day names used by the locale for the specified format.
    
    >>> get_day_names('wide', locale='en_US')[1]
    u'Tuesday'
    >>> get_day_names('abbreviated', locale='es')[1]
    u'mar'
    >>> get_day_names('narrow', context='stand-alone', locale='de_DE')[1]
    u'D'
    
    :param width: the width to use, one of "wide", "abbreviated", or "narrow"
    :param context: the context, either "format" or "stand-alone"
    :param locale: the `Locale` object, or a locale string
    :return: the dictionary of day names
    :rtype: `dict`
    """
    return Locale.parse(locale).days[context][width]

def get_month_names(width='wide', context='format', locale=LC_TIME):
    """Return the month names used by the locale for the specified format.
    
    >>> get_month_names('wide', locale='en_US')[1]
    u'January'
    >>> get_month_names('abbreviated', locale='es')[1]
    u'ene'
    >>> get_month_names('narrow', context='stand-alone', locale='de_DE')[1]
    u'J'
    
    :param width: the width to use, one of "wide", "abbreviated", or "narrow"
    :param context: the context, either "format" or "stand-alone"
    :param locale: the `Locale` object, or a locale string
    :return: the dictionary of month names
    :rtype: `dict`
    """
    return Locale.parse(locale).months[context][width]

def get_quarter_names(width='wide', context='format', locale=LC_TIME):
    """Return the quarter names used by the locale for the specified format.
    
    >>> get_quarter_names('wide', locale='en_US')[1]
    u'1st quarter'
    >>> get_quarter_names('abbreviated', locale='de_DE')[1]
    u'Q1'
    
    :param width: the width to use, one of "wide", "abbreviated", or "narrow"
    :param context: the context, either "format" or "stand-alone"
    :param locale: the `Locale` object, or a locale string
    :return: the dictionary of quarter names
    :rtype: `dict`
    """
    return Locale.parse(locale).quarters[context][width]

def get_era_names(width='wide', locale=LC_TIME):
    """Return the era names used by the locale for the specified format.
    
    >>> get_era_names('wide', locale='en_US')[1]
    u'Anno Domini'
    >>> get_era_names('abbreviated', locale='de_DE')[1]
    u'n. Chr.'
    
    :param width: the width to use, either "wide" or "abbreviated"
    :param locale: the `Locale` object, or a locale string
    :return: the dictionary of era names
    :rtype: `dict`
    """
    return Locale.parse(locale).eras[width]

def get_date_format(format='medium', locale=LC_TIME):
    """Return the date formatting patterns used by the locale for the specified
    format.
    
    >>> get_date_format(locale='en_US')
    <DateTimePattern u'MMM d, yyyy'>
    >>> get_date_format('full', locale='de_DE')
    <DateTimePattern u'EEEE, d. MMMM yyyy'>
    
    :param format: the format to use, one of "full", "long", "medium", or
                   "short"
    :param locale: the `Locale` object, or a locale string
    :return: the date format pattern
    :rtype: `dict`
    """
    return Locale.parse(locale).date_formats[format]

def get_time_format(format='medium', locale=LC_TIME):
    """Return the time formatting patterns used by the locale for the specified
    format.
    
    >>> get_time_format(locale='en_US')
    <DateTimePattern u'h:mm:ss a'>
    >>> get_time_format('full', locale='de_DE')
    <DateTimePattern u"H:mm' Uhr 'z">
    
    :param format: the format to use, one of "full", "long", "medium", or
                   "short"
    :param locale: the `Locale` object, or a locale string
    :return: the time format pattern
    :rtype: `dict`
    """
    return Locale.parse(locale).time_formats[format]

def format_date(date, format='medium', locale=LC_TIME):
    """Returns a date formatted according to the given pattern.
    
    >>> d = date(2007, 04, 01)
    >>> format_date(d, locale='en_US')
    u'Apr 1, 2007'
    >>> format_date(d, format='full', locale='de_DE')
    u'Sonntag, 1. April 2007'
    
    :param date: the ``date`` object
    :param format: one of "full", "long", "medium", or "short"
    :param locale: a `Locale` object or a locale string
    :rtype: `unicode`
    """
    locale = Locale.parse(locale)
    if format in ('full', 'long', 'medium', 'short'):
        format = get_date_format(format, locale=locale)
    pattern = parse_pattern(format)
    return parse_pattern(format).apply(date, locale)

def format_datetime(datetime, format='medium', locale=LC_TIME):
    """Returns a date formatted according to the given pattern.
    
    :param datetime: the ``date`` object
    :param format: one of "full", "long", "medium", or "short"
    :param locale: a `Locale` object or a locale string
    :rtype: `unicode`
    """
    raise NotImplementedError

def format_time(time, format='medium', locale=LC_TIME):
    """Returns a time formatted according to the given pattern.
    
    >>> t = time(15, 30)
    >>> format_time(t, locale='en_US')
    u'3:30:00 PM'
    >>> format_time(t, format='short', locale='de_DE')
    u'15:30'
    
    :param time: the ``time`` object
    :param format: one of "full", "long", "medium", or "short"
    :param locale: a `Locale` object or a locale string
    :rtype: `unicode`
    """
    locale = Locale.parse(locale)
    if format in ('full', 'long', 'medium', 'short'):
        format = get_time_format(format, locale=locale)
    return parse_pattern(format).apply(time, locale)

def parse_date(string, locale=LC_TIME):
    raise NotImplementedError

def parse_datetime(string, locale=LC_TIME):
    raise NotImplementedError

def parse_time(string, locale=LC_TIME):
    raise NotImplementedError


class DateTimePattern(object):

    def __init__(self, pattern, format):
        self.pattern = pattern
        self.format = format

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.pattern)

    def __unicode__(self):
        return self.pattern

    def __mod__(self, other):
        assert type(other) is DateTimeFormat
        return self.format % other

    def apply(self, datetime, locale):
        return self % DateTimeFormat(datetime, locale)


class DateTimeFormat(object):

    def __init__(self, value, locale):
        assert isinstance(value, (date, datetime, time))
        self.value = value
        self.locale = Locale.parse(locale)

    def __getitem__(self, name):
        # TODO: a number of fields missing here
        char = name[0]
        num = len(name)
        if char == 'G':
            return self.format_era(char, num)
        elif char in ('y', 'Y'):
            return self.format_year(char, num)
        elif char in ('Q', 'q'):
            return self.format_quarter(char, num)
        elif char in ('M', 'L'):
            return self.format_month(char, num)
        elif char == 'd':
            return self.format(self.value.day, num)
        elif char in ('E', 'e', 'c'):
            return self.format_weekday(char, num)
        elif char == 'a':
            return self.format_period(char)
        elif char == 'h':
            return self.format(self.value.hour % 12, num)
        elif char == 'H':
            return self.format(self.value.hour, num)
        elif char == 'm':
            return self.format(self.value.minute, num)
        elif char == 's':
            return self.format(self.value.second, num)
        else:
            raise KeyError('Unsupported date/time field %r' % char)

    def format_era(self, char, num):
        width = {3: 'abbreviated', 4: 'wide', 5: 'narrow'}[max(3, num)]
        era = int(self.value.year >= 0)
        return get_era_names(width, self.locale)[era]

    def format_year(self, char, num):
        if char.islower():
            value = self.value.year
        else:
            value = self.value.isocalendar()[0]
        year = self.format(value, num)
        if num == 2:
            year = year[-2:]
        return year

    def format_month(self, char, num):
        if num <= 2:
            return ('%%0%dd' % num) % self.value.month
        width = {3: 'abbreviated', 4: 'wide', 5: 'narrow'}[num]
        context = {3: 'format', 4: 'format', 5: 'stand-alone'}[num]
        return get_month_names(width, context, self.locale)[self.value.month]

    def format_weekday(self, char, num):
        if num < 3:
            if char.islower():
                value = 7 - self.locale.first_week_day + self.value.weekday()
                return self.format(value % 7 + 1, num)
            num = 3
        weekday = self.value.weekday()
        width = {3: 'abbreviated', 4: 'wide', 5: 'narrow'}[num]
        context = {3: 'format', 4: 'format', 5: 'stand-alone'}[num]
        return get_day_names(width, context, self.locale)[weekday]

    def format_period(self, char):
        period = {0: 'am', 1: 'pm'}[int(self.value.hour > 12)]
        return get_period_names(locale=self.locale)[period]

    def format(self, value, length):
        return ('%%0%dd' % length) % value


PATTERN_CHARS = {
    'G': [1, 2, 3, 4, 5],                                           # era
    'y': None, 'Y': None, 'u': None,                                # year
    'Q': [1, 2, 3, 4], 'q': [1, 2, 3, 4],                           # quarter
    'M': [1, 2, 3, 4, 5], 'L': [1, 2, 3, 4, 5],                     # month
    'w': [1, 2], 'W': [1],                                          # week
    'd': [1, 2], 'D': [1, 2, 3], 'F': [1], 'g': None,               # day
    'E': [1, 2, 3, 4, 5], 'e': [1, 2, 3, 4, 5], 'c': [1, 3, 4, 5],  # week day
    'a': [1],                                                       # period
    'h': [1, 2], 'H': [1, 2], 'K': [1, 2], 'k': [1, 2],             # hour
    'm': [1, 2],                                                    # minute
    's': [1, 2], 'S': None, 'A': None,                              # second
    'z': [1, 2, 3, 4], 'Z': [1, 2, 3, 4], 'v': [1, 4]               # zone
}

def parse_pattern(pattern):
    """Parse date, time, and datetime format patterns.
    
    >>> parse_pattern("MMMMd").format
    u'%(MMMM)s%(d)s'
    >>> parse_pattern("MMM d, yyyy").format
    u'%(MMM)s %(d)s, %(yyyy)s'
    >>> parse_pattern("H:mm' Uhr 'z").format
    u'%(H)s:%(mm)s Uhr %(z)s'
    
    :param pattern: the formatting pattern to parse
    """
    if type(pattern) is DateTimePattern:
        return pattern

    result = []
    quotebuf = None
    charbuf = []
    fieldchar = ['']
    fieldnum = [0]

    def append_chars():
        result.append(''.join(charbuf).replace('%', '%%'))
        del charbuf[:]

    def append_field():
        limit = PATTERN_CHARS[fieldchar[0]]
        if limit and fieldnum[0] not in limit:
            raise ValueError('Invalid length for field: %r'
                             % (fieldchar[0] * fieldnum[0]))
        result.append('%%(%s)s' % (fieldchar[0] * fieldnum[0]))
        fieldchar[0] = ''
        fieldnum[0] = 0

    for idx, char in enumerate(pattern):
        if quotebuf is None:
            if char == "'": # quote started
                if fieldchar[0]:
                    append_field()
                elif charbuf:
                    append_chars()
                quotebuf = []
            elif char in PATTERN_CHARS:
                if charbuf:
                    append_chars()
                if char == fieldchar[0]:
                    fieldnum[0] += 1
                else:
                    if fieldchar[0]:
                        append_field()
                    fieldchar[0] = char
                    fieldnum[0] = 1
            else:
                if fieldchar[0]:
                    append_field()
                charbuf.append(char)

        elif quotebuf is not None:
            if char == "'": # quote ended
                charbuf.extend(quotebuf)
                quotebuf = None
            else: # inside quote
                quotebuf.append(char)

    if fieldchar[0]:
        append_field()
    elif charbuf:
        append_chars()

    return DateTimePattern(pattern, u''.join(result))
