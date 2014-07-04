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

import calendar
from datetime import date, datetime, time, timedelta
import types
import unittest

from pytz import timezone

from babel import dates, Locale
from babel.util import FixedOffsetTimezone


class DateTimeFormatTestCase(unittest.TestCase):

    def test_quarter_format(self):
        d = date(2006, 6, 8)
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('2', fmt['Q'])
        self.assertEqual('2nd quarter', fmt['QQQQ'])
        d = date(2006, 12, 31)
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('Q4', fmt['QQQ'])

    def test_month_context(self):
        d = date(2006, 2, 8)
        fmt = dates.DateTimeFormat(d, locale='cs_CZ')
        self.assertEqual(u'2', fmt['MMMMM']) # narrow format
        fmt = dates.DateTimeFormat(d, locale='cs_CZ')
        self.assertEqual(u'ú', fmt['LLLLL']) # narrow standalone

    def test_abbreviated_month_alias(self):
        d = date(2006, 3, 8)
        fmt = dates.DateTimeFormat(d, locale='de_DE')
        self.assertEqual(u'Mär', fmt['LLL'])

    def test_week_of_year_first(self):
        d = date(2006, 1, 8)
        fmt = dates.DateTimeFormat(d, locale='de_DE')
        self.assertEqual('1', fmt['w'])
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('02', fmt['ww'])

    def test_week_of_year_first_with_year(self):
        d = date(2006, 1, 1)
        fmt = dates.DateTimeFormat(d, locale='de_DE')
        self.assertEqual('52', fmt['w'])
        self.assertEqual('2005', fmt['YYYY'])

    def test_week_of_year_last(self):
        d = date(2006, 12, 26)
        fmt = dates.DateTimeFormat(d, locale='de_DE')
        self.assertEqual('52', fmt['w'])
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('52', fmt['w'])

    def test_week_of_year_last_us_extra_week(self):
        d = date(2005, 12, 26)
        fmt = dates.DateTimeFormat(d, locale='de_DE')
        self.assertEqual('52', fmt['w'])
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('53', fmt['w'])

    def test_week_of_month_first(self):
        d = date(2006, 1, 8)
        fmt = dates.DateTimeFormat(d, locale='de_DE')
        self.assertEqual('1', fmt['W'])
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('2', fmt['W'])

    def test_week_of_month_last(self):
        d = date(2006, 1, 29)
        fmt = dates.DateTimeFormat(d, locale='de_DE')
        self.assertEqual('4', fmt['W'])
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('5', fmt['W'])

    def test_day_of_year(self):
        d = date(2007, 4, 1)
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('91', fmt['D'])

    def test_day_of_year_works_with_datetime(self):
        d = datetime(2007, 4, 1)
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('91', fmt['D'])

    def test_day_of_year_first(self):
        d = date(2007, 1, 1)
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('001', fmt['DDD'])

    def test_day_of_year_last(self):
        d = date(2007, 12, 31)
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('365', fmt['DDD'])

    def test_day_of_week_in_month(self):
        d = date(2007, 4, 15)
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('3', fmt['F'])

    def test_day_of_week_in_month_first(self):
        d = date(2007, 4, 1)
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('1', fmt['F'])

    def test_day_of_week_in_month_last(self):
        d = date(2007, 4, 29)
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('5', fmt['F'])

    def test_local_day_of_week(self):
        d = date(2007, 4, 1) # a sunday
        fmt = dates.DateTimeFormat(d, locale='de_DE')
        self.assertEqual('7', fmt['e']) # monday is first day of week
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('01', fmt['ee']) # sunday is first day of week
        fmt = dates.DateTimeFormat(d, locale='bn_BD')
        self.assertEqual('03', fmt['ee']) # friday is first day of week

        d = date(2007, 4, 2) # a monday
        fmt = dates.DateTimeFormat(d, locale='de_DE')
        self.assertEqual('1', fmt['e']) # monday is first day of week
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('02', fmt['ee']) # sunday is first day of week
        fmt = dates.DateTimeFormat(d, locale='bn_BD')
        self.assertEqual('04', fmt['ee']) # friday is first day of week

    def test_local_day_of_week_standalone(self):
        d = date(2007, 4, 1) # a sunday
        fmt = dates.DateTimeFormat(d, locale='de_DE')
        self.assertEqual('7', fmt['c']) # monday is first day of week
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('1', fmt['c']) # sunday is first day of week
        fmt = dates.DateTimeFormat(d, locale='bn_BD')
        self.assertEqual('3', fmt['c']) # friday is first day of week

        d = date(2007, 4, 2) # a monday
        fmt = dates.DateTimeFormat(d, locale='de_DE')
        self.assertEqual('1', fmt['c']) # monday is first day of week
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('2', fmt['c']) # sunday is first day of week
        fmt = dates.DateTimeFormat(d, locale='bn_BD')
        self.assertEqual('4', fmt['c']) # friday is first day of week

    def test_fractional_seconds(self):
        t = time(15, 30, 12, 34567)
        fmt = dates.DateTimeFormat(t, locale='en_US')
        self.assertEqual('0346', fmt['SSSS'])

    def test_fractional_seconds_zero(self):
        t = time(15, 30, 0)
        fmt = dates.DateTimeFormat(t, locale='en_US')
        self.assertEqual('0000', fmt['SSSS'])

    def test_milliseconds_in_day(self):
        t = time(15, 30, 12, 345000)
        fmt = dates.DateTimeFormat(t, locale='en_US')
        self.assertEqual('55812345', fmt['AAAA'])

    def test_milliseconds_in_day_zero(self):
        d = time(0, 0, 0)
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('0000', fmt['AAAA'])

    def test_timezone_rfc822(self):
        tz = timezone('Europe/Berlin')
        t = time(15, 30, tzinfo=tz)
        fmt = dates.DateTimeFormat(t, locale='de_DE')
        self.assertEqual('+0100', fmt['Z'])

    def test_timezone_gmt(self):
        tz = timezone('Europe/Berlin')
        t = time(15, 30, tzinfo=tz)
        fmt = dates.DateTimeFormat(t, locale='de_DE')
        self.assertEqual('GMT+01:00', fmt['ZZZZ'])

    def test_timezone_name(self):
        tz = timezone('Europe/Paris')
        dt = datetime(2007, 4, 1, 15, 30, tzinfo=tz)
        fmt = dates.DateTimeFormat(dt, locale='fr_FR')
        self.assertEqual('Heure : France', fmt['v'])

    def test_timezone_location_format(self):
        tz = timezone('Europe/Paris')
        dt = datetime(2007, 4, 1, 15, 30, tzinfo=tz)
        fmt = dates.DateTimeFormat(dt, locale='fr_FR')
        self.assertEqual('Heure : France', fmt['VVVV'])

    def test_timezone_walltime_short(self):
        tz = timezone('Europe/Paris')
        t = time(15, 30, tzinfo=tz)
        fmt = dates.DateTimeFormat(t, locale='fr_FR')
        self.assertEqual('Heure : France', fmt['v'])

    def test_timezone_walltime_long(self):
        tz = timezone('Europe/Paris')
        t = time(15, 30, tzinfo=tz)
        fmt = dates.DateTimeFormat(t, locale='fr_FR')
        self.assertEqual(u'heure de l\u2019Europe centrale', fmt['vvvv'])

    def test_hour_formatting(self):
        l = 'en_US'
        t = time(0, 0, 0)
        self.assertEqual(dates.format_time(t, 'h a', locale=l), '12 AM')
        self.assertEqual(dates.format_time(t, 'H', locale=l), '0')
        self.assertEqual(dates.format_time(t, 'k', locale=l), '24')
        self.assertEqual(dates.format_time(t, 'K a', locale=l), '0 AM')
        t = time(12, 0, 0)
        self.assertEqual(dates.format_time(t, 'h a', locale=l), '12 PM')
        self.assertEqual(dates.format_time(t, 'H', locale=l), '12')
        self.assertEqual(dates.format_time(t, 'k', locale=l), '12')
        self.assertEqual(dates.format_time(t, 'K a', locale=l), '0 PM')


class FormatDateTestCase(unittest.TestCase):

    def test_with_time_fields_in_pattern(self):
        self.assertRaises(AttributeError, dates.format_date, date(2007, 4, 1),
                          "yyyy-MM-dd HH:mm", locale='en_US')

    def test_with_time_fields_in_pattern_and_datetime_param(self):
        self.assertRaises(AttributeError, dates.format_date,
                          datetime(2007, 4, 1, 15, 30),
                          "yyyy-MM-dd HH:mm", locale='en_US')

    def test_with_day_of_year_in_pattern_and_datetime_param(self):
        # format_date should work on datetimes just as well (see #282)
        d = datetime(2007, 4, 1)
        self.assertEqual('14', dates.format_date(d, 'w', locale='en_US'))


class FormatDatetimeTestCase(unittest.TestCase):

    def test_with_float(self):
        d = datetime(2012, 4, 1, 15, 30, 29, tzinfo=timezone('UTC'))
        epoch = float(calendar.timegm(d.timetuple()))
        formatted_string = dates.format_datetime(epoch, format='long', locale='en_US')
        self.assertEqual(u'April 1, 2012 at 3:30:29 PM +0000', formatted_string)


class FormatTimeTestCase(unittest.TestCase):

    def test_with_naive_datetime_and_tzinfo(self):
        string = dates.format_time(datetime(2007, 4, 1, 15, 30),
                                   'long', tzinfo=timezone('US/Eastern'),
                                   locale='en')
        self.assertEqual('11:30:00 AM EDT', string)

    def test_with_float(self):
        d = datetime(2012, 4, 1, 15, 30, 29, tzinfo=timezone('UTC'))
        epoch = float(calendar.timegm(d.timetuple()))
        formatted_time = dates.format_time(epoch, format='long', locale='en_US')
        self.assertEqual(u'3:30:29 PM +0000', formatted_time)


    def test_with_date_fields_in_pattern(self):
        self.assertRaises(AttributeError, dates.format_time, date(2007, 4, 1),
                          "yyyy-MM-dd HH:mm", locale='en_US')

    def test_with_date_fields_in_pattern_and_datetime_param(self):
        self.assertRaises(AttributeError, dates.format_time,
                          datetime(2007, 4, 1, 15, 30),
                          "yyyy-MM-dd HH:mm", locale='en_US')


class FormatTimedeltaTestCase(unittest.TestCase):

    def test_zero_seconds(self):
        string = dates.format_timedelta(timedelta(seconds=0), locale='en')
        self.assertEqual('0 seconds', string)
        string = dates.format_timedelta(timedelta(seconds=0), locale='en',
                                        format='short')
        self.assertEqual('0 secs', string)
        string = dates.format_timedelta(timedelta(seconds=0),
                                        granularity='hour', locale='en')
        self.assertEqual('0 hours', string)
        string = dates.format_timedelta(timedelta(seconds=0),
                                        granularity='hour', locale='en',
                                        format='short')
        self.assertEqual('0 hrs', string)

    def test_small_value_with_granularity(self):
        string = dates.format_timedelta(timedelta(seconds=42),
                                        granularity='hour', locale='en')
        self.assertEqual('1 hour', string)
        string = dates.format_timedelta(timedelta(seconds=42),
                                        granularity='hour', locale='en',
                                        format='short')
        self.assertEqual('1 hr', string)

    def test_direction_adding(self):
        string = dates.format_timedelta(timedelta(hours=1),
                                        locale='en',
                                        add_direction=True)
        self.assertEqual('In 1 hour', string)
        string = dates.format_timedelta(timedelta(hours=-1),
                                        locale='en',
                                        add_direction=True)
        self.assertEqual('1 hour ago', string)


class TimeZoneAdjustTestCase(unittest.TestCase):
    def _utc(self):
        class EvilFixedOffsetTimezone(FixedOffsetTimezone):
            def localize(self, dt, is_dst=False):
                raise NotImplementedError()
        UTC = EvilFixedOffsetTimezone(0, 'UTC')
        # This is important to trigger the actual bug (#257)
        self.assertEqual(False, hasattr(UTC, 'normalize'))
        return UTC

    def test_can_format_time_with_non_pytz_timezone(self):
        # regression test for #257
        utc = self._utc()
        t = datetime(2007, 4, 1, 15, 30, tzinfo=utc)
        formatted_time = dates.format_time(t, 'long', tzinfo=utc, locale='en')
        self.assertEqual('3:30:00 PM +0000', formatted_time)


def test_get_period_names():
    assert dates.get_period_names(locale='en_US')['am'] == u'AM'


def test_get_day_names():
    assert dates.get_day_names('wide', locale='en_US')[1] == u'Tuesday'
    assert dates.get_day_names('abbreviated', locale='es')[1] == u'mar'
    de = dates.get_day_names('narrow', context='stand-alone', locale='de_DE')
    assert de[1] == u'D'


def test_get_month_names():
    assert dates.get_month_names('wide', locale='en_US')[1] == u'January'
    assert dates.get_month_names('abbreviated', locale='es')[1] == u'ene'
    de = dates.get_month_names('narrow', context='stand-alone', locale='de_DE')
    assert de[1] == u'J'


def test_get_quarter_names():
    assert dates.get_quarter_names('wide', locale='en_US')[1] == u'1st quarter'
    assert dates.get_quarter_names('abbreviated', locale='de_DE')[1] == u'Q1'


def test_get_era_names():
    assert dates.get_era_names('wide', locale='en_US')[1] == u'Anno Domini'
    assert dates.get_era_names('abbreviated', locale='de_DE')[1] == u'n. Chr.'


def test_get_date_format():
    us = dates.get_date_format(locale='en_US')
    assert us.pattern == u'MMM d, y'
    de = dates.get_date_format('full', locale='de_DE')
    assert de.pattern == u'EEEE, d. MMMM y'


def test_get_datetime_format():
    assert dates.get_datetime_format(locale='en_US') == u'{1}, {0}'


def test_get_time_format():
    assert dates.get_time_format(locale='en_US').pattern == u'h:mm:ss a'
    assert (dates.get_time_format('full', locale='de_DE').pattern ==
            u'HH:mm:ss zzzz')


def test_get_timezone_gmt():
    dt = datetime(2007, 4, 1, 15, 30)
    assert dates.get_timezone_gmt(dt, locale='en') == u'GMT+00:00'

    tz = timezone('America/Los_Angeles')
    dt = datetime(2007, 4, 1, 15, 30, tzinfo=tz)
    assert dates.get_timezone_gmt(dt, locale='en') == u'GMT-08:00'
    assert dates.get_timezone_gmt(dt, 'short', locale='en') == u'-0800'

    assert dates.get_timezone_gmt(dt, 'long', locale='fr_FR') == u'UTC-08:00'


def test_get_timezone_location():
    tz = timezone('America/St_Johns')
    assert (dates.get_timezone_location(tz, locale='de_DE') ==
            u"Kanada (St. John's) Zeit")
    tz = timezone('America/Mexico_City')
    assert (dates.get_timezone_location(tz, locale='de_DE') ==
            u'Mexiko (Mexiko-Stadt) Zeit')

    tz = timezone('Europe/Berlin')
    assert (dates.get_timezone_name(tz, locale='de_DE') ==
            u'Mitteleurop\xe4ische Zeit')


def test_get_timezone_name():
    dt = time(15, 30, tzinfo=timezone('America/Los_Angeles'))
    assert (dates.get_timezone_name(dt, locale='en_US') ==
            u'Pacific Standard Time')
    assert dates.get_timezone_name(dt, width='short', locale='en_US') == u'PST'

    tz = timezone('America/Los_Angeles')
    assert dates.get_timezone_name(tz, locale='en_US') == u'Pacific Time'
    assert dates.get_timezone_name(tz, 'short', locale='en_US') == u'PT'

    tz = timezone('Europe/Berlin')
    assert (dates.get_timezone_name(tz, locale='de_DE') ==
            u'Mitteleurop\xe4ische Zeit')
    assert (dates.get_timezone_name(tz, locale='pt_BR') ==
            u'Hor\xe1rio da Europa Central')

    tz = timezone('America/St_Johns')
    assert dates.get_timezone_name(tz, locale='de_DE') == u'Neufundland-Zeit'

    tz = timezone('America/Los_Angeles')
    assert dates.get_timezone_name(tz, locale='en', width='short',
                                   zone_variant='generic') == u'PT'
    assert dates.get_timezone_name(tz, locale='en', width='short',
                                   zone_variant='standard') == u'PST'
    assert dates.get_timezone_name(tz, locale='en', width='short',
                                   zone_variant='daylight') == u'PDT'
    assert dates.get_timezone_name(tz, locale='en', width='long',
                                   zone_variant='generic') == u'Pacific Time'
    assert dates.get_timezone_name(tz, locale='en', width='long',
                                   zone_variant='standard') == u'Pacific Standard Time'
    assert dates.get_timezone_name(tz, locale='en', width='long',
                                   zone_variant='daylight') == u'Pacific Daylight Time'


def test_format_date():
    d = date(2007, 4, 1)
    assert dates.format_date(d, locale='en_US') == u'Apr 1, 2007'
    assert (dates.format_date(d, format='full', locale='de_DE') ==
            u'Sonntag, 1. April 2007')
    assert (dates.format_date(d, "EEE, MMM d, ''yy", locale='en') ==
            u"Sun, Apr 1, '07")


def test_format_datetime():
    dt = datetime(2007, 4, 1, 15, 30)
    assert (dates.format_datetime(dt, locale='en_US') ==
            u'Apr 1, 2007, 3:30:00 PM')

    full = dates.format_datetime(dt, 'full', tzinfo=timezone('Europe/Paris'),
                                 locale='fr_FR')
    assert full == (u'dimanche 1 avril 2007 17:30:00 heure '
                    u'avanc\xe9e d\u2019Europe centrale')
    custom = dates.format_datetime(dt, "yyyy.MM.dd G 'at' HH:mm:ss zzz",
                                   tzinfo=timezone('US/Eastern'), locale='en')
    assert custom == u'2007.04.01 AD at 11:30:00 EDT'


def test_format_time():
    t = time(15, 30)
    assert dates.format_time(t, locale='en_US') == u'3:30:00 PM'
    assert dates.format_time(t, format='short', locale='de_DE') == u'15:30'

    assert (dates.format_time(t, "hh 'o''clock' a", locale='en') ==
            u"03 o'clock PM")

    t = datetime(2007, 4, 1, 15, 30)
    tzinfo = timezone('Europe/Paris')
    t = tzinfo.localize(t)
    fr = dates.format_time(t, format='full', tzinfo=tzinfo, locale='fr_FR')
    assert fr == u'15:30:00 heure avanc\xe9e d\u2019Europe centrale'
    custom = dates.format_time(t, "hh 'o''clock' a, zzzz",
                               tzinfo=timezone('US/Eastern'), locale='en')
    assert custom == u"09 o'clock AM, Eastern Daylight Time"

    t = time(15, 30)
    paris = dates.format_time(t, format='full',
                              tzinfo=timezone('Europe/Paris'), locale='fr_FR')
    assert paris == u'15:30:00 heure normale de l\u2019Europe centrale'
    us_east = dates.format_time(t, format='full',
                                tzinfo=timezone('US/Eastern'), locale='en_US')
    assert us_east == u'3:30:00 PM Eastern Standard Time'


def test_format_timedelta():
    assert (dates.format_timedelta(timedelta(weeks=12), locale='en_US')
            == u'3 months')
    assert (dates.format_timedelta(timedelta(seconds=1), locale='es')
            == u'1 segundo')

    assert (dates.format_timedelta(timedelta(hours=3), granularity='day',
                                   locale='en_US')
            == u'1 day')

    assert (dates.format_timedelta(timedelta(hours=23), threshold=0.9,
                                   locale='en_US')
            == u'1 day')
    assert (dates.format_timedelta(timedelta(hours=23), threshold=1.1,
                                   locale='en_US')
            == u'23 hours')


def test_parse_date():
    assert dates.parse_date('4/1/04', locale='en_US') == date(2004, 4, 1)
    assert dates.parse_date('01.04.2004', locale='de_DE') == date(2004, 4, 1)


def test_parse_time():
    assert dates.parse_time('15:30:00', locale='en_US') == time(15, 30)


def test_datetime_format_get_week_number():
    format = dates.DateTimeFormat(date(2006, 1, 8), Locale.parse('de_DE'))
    assert format.get_week_number(6) == 1

    format = dates.DateTimeFormat(date(2006, 1, 8), Locale.parse('en_US'))
    assert format.get_week_number(6) == 2


def test_parse_pattern():
    assert dates.parse_pattern("MMMMd").format == u'%(MMMM)s%(d)s'
    assert (dates.parse_pattern("MMM d, yyyy").format ==
            u'%(MMM)s %(d)s, %(yyyy)s')
    assert (dates.parse_pattern("H:mm' Uhr 'z").format ==
            u'%(H)s:%(mm)s Uhr %(z)s')
    assert dates.parse_pattern("hh' o''clock'").format == u"%(hh)s o'clock"
