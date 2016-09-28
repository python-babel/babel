import babel
from babel import dates
from datetime import date, datetime, time, timedelta
import unittest

from babel.Exceptions.ParseTimeException import ParseTimeException


class TestExceptions(unittest.TestCase):
    def test_digits(self):
        self.assertEqual(dates.parse_time('15:30', locale='en_US'), time(15, 30), "OK")
        self.assertEqual(dates.parse_time('3:30', locale='en_US'), time(3, 30), "OK")
        self.assertEqual(dates.parse_time('00:30', locale='en_US'), time(0, 30), "OK")

    def test_pm(self):
        self.assertEqual(dates.parse_time('03:30 PM', locale='en_US'), time(15, 30))
        self.assertEqual(dates.parse_time('03:30 pM', locale='en_US'), time(15, 30))
        self.assertEqual(dates.parse_time('03:30 pm', locale='en_US'), time(15, 30))
        self.assertEqual(dates.parse_time('03:30 Pm', locale='en_US'), time(15, 30))

    def test_am(self):
        self.assertEqual(dates.parse_time('03:30:21 AM', locale='en_US'), time(3, 30, 21))
        self.assertEqual(dates.parse_time('03:30:00 AM', locale='en_US'), time(3, 30))

    def test_badformatting(self):
        self.assertRaises(ParseTimeException, dates.parse_time, '', locale='en_US')
        self.assertRaises(ParseTimeException, dates.parse_time, 'a', locale='en_US')
        self.assertRaises(ParseTimeException, dates.parse_time, 'aaa', locale='en_US')


print(dates.parse_time('03:30 PM', locale='en_US'))

if __name__ == '__main__':
    unittest.main()
