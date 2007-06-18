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

from datetime import date, datetime, time
import doctest
import unittest

from pytz import timezone

from babel import dates


class DateTimeFormatTestCase(unittest.TestCase):

    def test_local_day_of_week(self):
        d = datetime(2007, 4, 1) # a sunday
        fmt = dates.DateTimeFormat(d, locale='de_DE')
        self.assertEqual('7', fmt['e']) # monday is first day of week
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('01', fmt['ee']) # sunday is first day of week
        fmt = dates.DateTimeFormat(d, locale='dv_MV')
        self.assertEqual('03', fmt['ee']) # friday is first day of week

        d = datetime(2007, 4, 2) # a monday
        fmt = dates.DateTimeFormat(d, locale='de_DE')
        self.assertEqual('1', fmt['e']) # monday is first day of week
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('02', fmt['ee']) # sunday is first day of week
        fmt = dates.DateTimeFormat(d, locale='dv_MV')
        self.assertEqual('04', fmt['ee']) # friday is first day of week

    def test_local_day_of_week_standalone(self):
        d = datetime(2007, 4, 1) # a sunday
        fmt = dates.DateTimeFormat(d, locale='de_DE')
        self.assertEqual('7', fmt['c']) # monday is first day of week
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('1', fmt['c']) # sunday is first day of week
        fmt = dates.DateTimeFormat(d, locale='dv_MV')
        self.assertEqual('3', fmt['c']) # friday is first day of week

        d = datetime(2007, 4, 2) # a monday
        fmt = dates.DateTimeFormat(d, locale='de_DE')
        self.assertEqual('1', fmt['c']) # monday is first day of week
        fmt = dates.DateTimeFormat(d, locale='en_US')
        self.assertEqual('2', fmt['c']) # sunday is first day of week
        fmt = dates.DateTimeFormat(d, locale='dv_MV')
        self.assertEqual('4', fmt['c']) # friday is first day of week

    def test_timezone_rfc822(self):
        tz = timezone('Europe/Berlin')
        t = time(15, 30, tzinfo=tz)
        fmt = dates.DateTimeFormat(t, locale='de_DE')
        self.assertEqual('+0100', fmt['Z'])

    def test_timezone_gmt(self):
        tz = timezone('Europe/Berlin')
        t = time(15, 30, tzinfo=tz)
        fmt = dates.DateTimeFormat(t, locale='de_DE')
        self.assertEqual('GMT +01:00', fmt['ZZZZ'])

    def test_timezone_walltime_short(self):
        tz = timezone('Europe/Paris')
        t = time(15, 30, tzinfo=tz)
        fmt = dates.DateTimeFormat(t, locale='en_US')
        self.assertEqual('CET', fmt['v'])

    def test_timezone_walltime_long(self):
        tz = timezone('Europe/Paris')
        t = time(15, 30, tzinfo=tz)
        fmt = dates.DateTimeFormat(t, locale='en_US')
        self.assertEqual('Central European Time', fmt['vvvv'])


class FormatDateTestCase(unittest.TestCase):

    def test_with_time_fields_in_pattern(self):
        self.assertRaises(AttributeError, dates.format_date, date(2007, 04, 01),
                          "yyyy-MM-dd HH:mm", locale='en_US')

    def test_with_time_fields_in_pattern_and_datetime_param(self):
        self.assertRaises(AttributeError, dates.format_date,
                          datetime(2007, 04, 01, 15, 30),
                          "yyyy-MM-dd HH:mm", locale='en_US')


class FormatTimeTestCase(unittest.TestCase):

    def test_with_date_fields_in_pattern(self):
        self.assertRaises(AttributeError, dates.format_time, date(2007, 04, 01),
                          "yyyy-MM-dd HH:mm", locale='en_US')

    def test_with_date_fields_in_pattern_and_datetime_param(self):
        self.assertRaises(AttributeError, dates.format_time,
                          datetime(2007, 04, 01, 15, 30),
                          "yyyy-MM-dd HH:mm", locale='en_US')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(dates))
    suite.addTest(unittest.makeSuite(DateTimeFormatTestCase))
    suite.addTest(unittest.makeSuite(FormatDateTestCase))
    suite.addTest(unittest.makeSuite(FormatTimeTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
