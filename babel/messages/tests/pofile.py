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
from StringIO import StringIO
import unittest

from babel.messages.catalog import Catalog
from babel.messages import pofile


class WritePotTestCase(unittest.TestCase):

    def test_join_locations(self):
        catalog = Catalog()
        catalog.add(u'foo', locations=[('main.py', 1)])
        catalog.add(u'foo', locations=[('utils.py', 3)])
        buf = StringIO()
        pofile.write_pot(buf, catalog, omit_header=True)
        self.assertEqual('''#: main.py:1 utils.py:3
msgid "foo"
msgstr ""''', buf.getvalue().strip())

    def test_wrap_long_lines(self):
        text = """Here's some text where       
white space and line breaks matter, and should

not be removed

"""
        catalog = Catalog()
        catalog.add(text, locations=[('main.py', 1)])
        buf = StringIO()
        pofile.write_pot(buf, catalog, no_location=True, omit_header=True,
                         width=42)
        self.assertEqual(r'''msgid ""
"Here's some text where       \n"
"white space and line breaks matter, and"
" should\n"
"\n"
"not be removed\n"
"\n"
msgstr ""''', buf.getvalue().strip())

    def test_wrap_long_lines_with_long_word(self):
        text = """Here's some text that
includesareallylongwordthatmightbutshouldnt throw us into an infinite loop
"""
        catalog = Catalog()
        catalog.add(text, locations=[('main.py', 1)])
        buf = StringIO()
        pofile.write_pot(buf, catalog, no_location=True, omit_header=True,
                         width=32)
        self.assertEqual(r'''msgid ""
"Here's some text that\n"
"includesareallylongwordthatmightbutshouldnt"
" throw us into an infinite "
"loop\n"
msgstr ""''', buf.getvalue().strip())


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(pofile))
    suite.addTest(unittest.makeSuite(WritePotTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
