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

from datetime import datetime
import doctest
from StringIO import StringIO
import unittest

from babel.messages.catalog import Catalog
from babel.messages import pofile


class WritePoTestCase(unittest.TestCase):

    def test_join_locations(self):
        catalog = Catalog()
        catalog.add(u'foo', locations=[('main.py', 1)])
        catalog.add(u'foo', locations=[('utils.py', 3)])
        buf = StringIO()
        pofile.write_po(buf, catalog, omit_header=True)
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
        pofile.write_po(buf, catalog, no_location=True, omit_header=True,
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
        pofile.write_po(buf, catalog, no_location=True, omit_header=True,
                         width=32)
        self.assertEqual(r'''msgid ""
"Here's some text that\n"
"includesareallylongwordthatmightbutshouldnt"
" throw us into an infinite "
"loop\n"
msgstr ""''', buf.getvalue().strip())
        
    def test_wrap_long_lines_in_header(self):
        """
        Verify that long lines in the header comment are wrapped correctly.
        """
        catalog = Catalog(project='AReallyReallyLongNameForAProject',
                          revision_date=datetime(2007, 4, 1))
        buf = StringIO()
        pofile.write_po(buf, catalog)
        self.assertEqual('''\
# Translations template for AReallyReallyLongNameForAProject.
# Copyright (C) 2007 ORGANIZATION
# This file is distributed under the same license as the
# AReallyReallyLongNameForAProject project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2007.
#
#, fuzzy''', '\n'.join(buf.getvalue().splitlines()[:7]))

    def test_pot_with_translator_comments(self):
        catalog = Catalog()
        catalog.add(u'foo', locations=[('main.py', 1)],
                    comments=['Comment About `foo`'])
        catalog.add(u'bar', locations=[('utils.py', 3)],
                    comments=['Comment About `bar` with',
                              'multiple lines.'])
        buf = StringIO()
        pofile.write_po(buf, catalog, omit_header=True)
        self.assertEqual('''#. Comment About `foo`
#: main.py:1
msgid "foo"
msgstr ""

#. Comment About `bar` with
#. multiple lines.
#: utils.py:3
msgid "bar"
msgstr ""''', buf.getvalue().strip())


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(pofile))
    suite.addTest(unittest.makeSuite(WritePoTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
