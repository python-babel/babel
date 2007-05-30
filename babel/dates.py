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
    u'Monday'
    >>> get_day_names('abbreviated', locale='es')[1]
    u'lun'
    >>> get_day_names('narrow', context='stand-alone', locale='de_DE')[1]
    u'M'
    
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
    <DateTimeFormatPattern u'MMM d, yyyy'>
    >>> get_date_format('full', locale='de_DE')
    <DateTimeFormatPattern u'EEEE, d. MMMM yyyy'>
    
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
    <DateTimeFormatPattern u'h:mm:ss a'>
    >>> get_time_format('full', locale='de_DE')
    <DateTimeFormatPattern u"H:mm' Uhr 'z">
    
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


class DateTimeFormatPattern(object):

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
        if name[0] == 'G':
            return self.format_era(len(name))
        elif name[0] == 'y':
            return self.format_year(self.value.year, len(name))
        elif name[0] == 'Y':
            return self.format_year(self.value.isocalendar()[0], len(name))
        elif name[0] == 'Q':
            return self.format_quarter(len(name))
        elif name[0] == 'q':
            return self.format_quarter(len(name), context='stand-alone')
        elif name[0] == 'M':
            return self.format_month(len(name))
        elif name[0] == 'L':
            return self.format_month(len(name), context='stand-alone')
        elif name[0] == 'd':
            return self.format(self.value.day, len(name))
        elif name[0] == 'E':
            return self.format_weekday(len(name))
        elif name[0] == 'e':
            return self.format_weekday(len(name), add_firstday=True)
        elif name[0] == 'c':
            return self.format_weekday(len(name), context='stand-alone')
        elif name[0] == 'a':
            return self.format_period()
        elif name[0] == 'h':
            return self.format(self.value.hour % 12, len(name))
        elif name[0] == 'H':
            return self.format(self.value.hour, len(name))
        elif name[0] == 'm':
            return self.format(self.value.minute, len(name))
        elif name[0] == 's':
            return self.format(self.value.second, len(name))
        else:
            raise KeyError('Unsupported date/time field %r' % name[0])

    def format_era(self, num):
        width = {3: 'abbreviated', 4: 'wide', 5: 'narrow'}[max(3, num)]
        era = int(self.value.year >= 0)
        return get_era_names(width, self.locale)[era]

    def format_year(self, value, num):
        year = self.format(value, num)
        if num == 2:
            year = year[-2:]
        return year

    def format_month(self, num, context='format'):
        if num <= 2:
            return ('%%0%dd' % num) % self.value.month
        width = {3: 'abbreviated', 4: 'wide', 5: 'narrow'}[num]
        return get_month_names(width, context, self.locale)[self.value.month]

    def format_weekday(self, num, add_firstday=False, context='format'):
        width = {3: 'abbreviated', 4: 'wide', 5: 'narrow'}[max(3, num)]
        weekday = self.value.weekday() + 1
        if add_firstday:
            weekday += self.locale.first_week_day
        return get_day_names(width, context, self.locale)[weekday]

    def format_period(self):
        period = {0: 'am', 1: 'pm'}[int(self.value.hour > 12)]
        return get_period_names(locale=self.locale)[period]

    def format(self, value, length):
        return ('%%0%dd' % length) % value


PATTERN_CHARS = {
    'G': 5,                                 # era
    'y': None, 'Y': None, 'u': None,        # year
    'Q': 4, 'q': 4,                         # quarter
    'M': 5, 'L': 5,                         # month
    'w': 2, 'W': 1,                         # week
    'd': 2, 'D': 3, 'F': 1, 'g': None,      # day
    'E': 5, 'e': 5, 'c': 5,                 # week day
    'a': 1,                                 # period
    'h': 2, 'H': 2, 'K': 2, 'k': 2,         # hour
    'm': 2,                                 # minute
    's': 2, 'S': None, 'A': None,           # second
    'z': 4, 'Z': 4, 'v': 4                  # zone
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
    if type(pattern) is DateTimeFormatPattern:
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
        if limit is not None and fieldnum[0] > limit:
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

    return DateTimeFormatPattern(pattern, u''.join(result))
