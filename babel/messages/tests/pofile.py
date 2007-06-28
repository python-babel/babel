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

from babel.messages.catalog import Catalog, Message
from babel.messages import pofile


class ReadPoTestCase(unittest.TestCase):

    def test_read_multiline(self):
        buf = StringIO(r'''msgid ""
"Here's some text that\n"
"includesareallylongwordthatmightbutshouldnt"
" throw us into an infinite "
"loop\n"
msgstr ""''')
        catalog = pofile.read_po(buf)
        self.assertEqual(1, len(catalog))
        message = list(catalog)[1]
        self.assertEqual("Here's some text that\nincludesareallylongwordthat"
                         "mightbutshouldnt throw us into an infinite loop\n",
                         message.id)
        
    def test_fuzzy_header(self):
        buf = StringIO(r'''\
# Translations template for AReallyReallyLongNameForAProject.
# Copyright (C) 2007 ORGANIZATION
# This file is distributed under the same license as the
# AReallyReallyLongNameForAProject project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2007.
#
#, fuzzy
''')
        catalog = pofile.read_po(buf)
        self.assertEqual(1, len(list(catalog)))
        self.assertEqual(True, list(catalog)[0].fuzzy)
        
    def test_not_fuzzy_header(self):
        buf = StringIO(r'''\
# Translations template for AReallyReallyLongNameForAProject.
# Copyright (C) 2007 ORGANIZATION
# This file is distributed under the same license as the
# AReallyReallyLongNameForAProject project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2007.
#
''')
        catalog = pofile.read_po(buf)
        self.assertEqual(1, len(list(catalog)))
        self.assertEqual(False, list(catalog)[0].fuzzy)


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
                    auto_comments=['Comment About `foo`'])
        catalog.add(u'bar', locations=[('utils.py', 3)],
                    user_comments=['Comment About `bar` with',
                                   'multiple lines.'])
        buf = StringIO()
        pofile.write_po(buf, catalog, omit_header=True)
        self.assertEqual('''#. Comment About `foo`
#: main.py:1
msgid "foo"
msgstr ""

# Comment About `bar` with
# multiple lines.
#: utils.py:3
msgid "bar"
msgstr ""''', buf.getvalue().strip())

    def test_po_with_obsolete_messages(self):
        catalog = Catalog()
        catalog.add(u'foo', u'Voh', locations=[('main.py', 1)])
        catalog.obsolete['bar'] = Message(u'bar', u'Bahr',
                                          locations=[('utils.py', 3)],
                                          user_comments=['User comment'])
        buf = StringIO()
        pofile.write_po(buf, catalog, omit_header=True)
        self.assertEqual('''#: main.py:1
msgid "foo"
msgstr "Voh"

# User comment
#~ msgid "bar"
#~ msgstr "Bahr"''', buf.getvalue().strip())


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(pofile))
    suite.addTest(unittest.makeSuite(ReadPoTestCase))
    suite.addTest(unittest.makeSuite(WritePoTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
