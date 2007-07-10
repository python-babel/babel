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

import doctest
import unittest

from babel import numbers


class FormatDecimalTestCase(unittest.TestCase):

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
        self.assertEqual(numbers.format_decimal(0.1, '@@',locale='en_US'), 
                         '0.10')
def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(numbers))
    suite.addTest(unittest.makeSuite(FormatDecimalTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
