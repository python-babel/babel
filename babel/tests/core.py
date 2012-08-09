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

import doctest
import os
import unittest

from babel import core
from babel.core import default_locale, Locale


class LocaleTest(unittest.TestCase):
    
    def test_locale_provides_access_to_cldr_locale_data(self):
        locale = Locale('en', 'US')
        self.assertEqual(u'English (United States)', locale.display_name)
        self.assertEqual(u'.', locale.number_symbols['decimal'])
    
    def test_repr(self):
        self.assertEqual("Locale('de', territory='DE')", 
                         repr(Locale('de', 'DE')))
        self.assertEqual("Locale('zh', territory='CN', script='Hans')", 
                         repr(Locale('zh', 'CN', script='Hans')))
    

class DefaultLocaleTest(unittest.TestCase):
    
    def setUp(self):
        self._old_locale_settings = self._current_locale_settings()
    
    def tearDown(self):
        self._set_locale_settings(self._old_locale_settings)
    
    def _current_locale_settings(self):
        settings = {}
        for name in ('LANGUAGE', 'LC_ALL', 'LC_CTYPE', 'LANG'):
            settings[name] = os.environ[name]
        return settings
    
    def _set_locale_settings(self, settings):
        for name, value in settings.items():
            os.environ[name] = value
    
    def test_ignore_invalid_locales_in_lc_ctype(self):
        # This is a regression test specifically for a bad LC_CTYPE setting on
        # MacOS X 10.6 (#200)
        os.environ['LC_CTYPE'] = 'UTF-8'
        # must not throw an exception
        default_locale('LC_CTYPE')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(core))
    suite.addTest(unittest.makeSuite(LocaleTest))
    suite.addTest(unittest.makeSuite(DefaultLocaleTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
