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

from babel.catalog import pofile


class PythonFormatFlagTestCase(unittest.TestCase):

    def test_without_name(self):
        assert pofile.PYTHON_FORMAT('foo %d bar')
        assert pofile.PYTHON_FORMAT('foo %s bar')
        assert pofile.PYTHON_FORMAT('foo %r bar')


class WritePotTestCase(unittest.TestCase):

    def test_join_locations(self):
        buf = StringIO()
        pofile.write_pot(buf, [
            ('main.py', 1, None, u'foo', None),
            ('utils.py', 3, None, u'foo', None),
        ], omit_header=True)
        self.assertEqual('''#: main.py:1 utils.py:3
msgid "foo"
msgstr ""''', buf.getvalue().strip())

    def test_wrap_long_lines(self):
        text = """Here's some text where       
white space and line breaks matter, and should

not be removed

"""
        buf = StringIO()
        pofile.write_pot(buf, [
            ('main.py', 1, None, text, None),
        ], no_location=True, omit_header=True, width=42)
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
        buf = StringIO()
        pofile.write_pot(buf, [
            ('main.py', 1, None, text, None),
        ], no_location=True, omit_header=True, width=32)
        self.assertEqual(r'''msgid ""
"Here's some text that\n"
"includesareallylongwordthatmightbutshouldnt"
" throw us into an infinite "
"loop\n"
msgstr ""''', buf.getvalue().strip())


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(pofile))
    suite.addTest(unittest.makeSuite(PythonFormatFlagTestCase))
    suite.addTest(unittest.makeSuite(WritePotTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
