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

import codecs
import doctest
from StringIO import StringIO
import unittest

from babel.messages import extract


class ExtractPythonTestCase(unittest.TestCase):

    def test_unicode_string_arg(self):
        buf = StringIO("msg = _(u'Foo Bar')")
        messages = list(extract.extract_python(buf, ('_',), [], {}))
        self.assertEqual(u'Foo Bar', messages[0][2])

    def test_comment_tag(self):
        buf = StringIO("""
# NOTE: A translation comment
msg = _(u'Foo Bar')
""")
        messages = list(extract.extract_python(buf, ('_',), ['NOTE:'], {}))
        self.assertEqual(u'Foo Bar', messages[0][2])
        self.assertEqual([u'A translation comment'], messages[0][3])

    def test_comment_tag_multiline(self):
        buf = StringIO("""
# NOTE: A translation comment
# with a second line
msg = _(u'Foo Bar')
""")
        messages = list(extract.extract_python(buf, ('_',), ['NOTE:'], {}))
        self.assertEqual(u'Foo Bar', messages[0][2])
        self.assertEqual([u'A translation comment', u'with a second line'],
                         messages[0][3])
        
    def test_translator_comments_with_previous_non_translator_comments(self):
        buf = StringIO("""
# This shouldn't be in the output
# because it didn't start with a comment tag
# NOTE: A translation comment
# with a second line
msg = _(u'Foo Bar')
""")
        messages = list(extract.extract_python(buf, ('_',), ['NOTE:'], {}))
        self.assertEqual(u'Foo Bar', messages[0][2])
        self.assertEqual([u'A translation comment', u'with a second line'],
                         messages[0][3])

    def test_comment_tags_not_on_start_of_comment(self):
        buf = StringIO("""
# This shouldn't be in the output
# because it didn't start with a comment tag
# do NOTE: this will no be a translation comment
# NOTE: This one will be
msg = _(u'Foo Bar')
""")
        messages = list(extract.extract_python(buf, ('_',), ['NOTE:'], {}))
        self.assertEqual(u'Foo Bar', messages[0][2])
        self.assertEqual([u'This one will be'], messages[0][3])

    def test_multiple_comment_tags(self):
        buf = StringIO("""
# NOTE1: A translation comment for tag1
# with a second line
msg = _(u'Foo Bar1')

# NOTE2: A translation comment for tag2
msg = _(u'Foo Bar2')
""")
        messages = list(extract.extract_python(buf, ('_',),
                                               ['NOTE1:', 'NOTE2:'], {}))
        self.assertEqual(u'Foo Bar1', messages[0][2])
        self.assertEqual([u'A translation comment for tag1',
                          u'with a second line'], messages[0][3])
        self.assertEqual(u'Foo Bar2', messages[1][2])
        self.assertEqual([u'A translation comment for tag2'], messages[1][3])

    def test_two_succeeding_comments(self):
        buf = StringIO("""
# NOTE: one
# NOTE: two
msg = _(u'Foo Bar')
""")
        messages = list(extract.extract_python(buf, ('_',), ['NOTE:'], {}))
        self.assertEqual(u'Foo Bar', messages[0][2])
        self.assertEqual([u'one', u'NOTE: two'], messages[0][3])
        
    def test_invalid_translator_comments(self):
        buf = StringIO("""
# NOTE: this shouldn't apply to any messages
hello = 'there'

msg = _(u'Foo Bar')
""")
        messages = list(extract.extract_python(buf, ('_',), ['NOTE:'], {}))
        self.assertEqual(u'Foo Bar', messages[0][2])
        self.assertEqual([], messages[0][3])

    def test_invalid_translator_comments2(self):
        buf = StringIO("""
# NOTE: Hi!
hithere = _('Hi there!')

# NOTE: you should not be seeing this in the .po
rows = [[v for v in range(0,10)] for row in range(0,10)]

# this (NOTE:) should not show up either
hello = _('Hello')
""")
        messages = list(extract.extract_python(buf, ('_',), ['NOTE:'], {}))
        self.assertEqual(u'Hi there!', messages[0][2])
        self.assertEqual([u'Hi!'], messages[0][3])
        self.assertEqual(u'Hello', messages[1][2])
        self.assertEqual([], messages[1][3])

    def test_invalid_translator_comments3(self):
        buf = StringIO("""
# NOTE: Hi,

# there!
hithere = _('Hi there!')
""")
        messages = list(extract.extract_python(buf, ('_',), ['NOTE:'], {}))
        self.assertEqual(u'Hi there!', messages[0][2])
        self.assertEqual([], messages[0][3])

    def test_utf8_message(self):
        buf = StringIO("""
# NOTE: hello
msg = _('Bonjour à tous')
""")
        messages = list(extract.extract_python(buf, ('_',), ['NOTE:'],
                                               {'encoding': 'utf-8'}))
        self.assertEqual(u'Bonjour à tous', messages[0][2])
        self.assertEqual([u'hello'], messages[0][3])

    def test_utf8_message_with_magic_comment(self):
        buf = StringIO("""# -*- coding: utf-8 -*-
# NOTE: hello
msg = _('Bonjour à tous')
""")
        messages = list(extract.extract_python(buf, ('_',), ['NOTE:'], {}))
        self.assertEqual(u'Bonjour à tous', messages[0][2])
        self.assertEqual([u'hello'], messages[0][3])

    def test_utf8_message_with_utf8_bom(self):
        buf = StringIO(codecs.BOM_UTF8 + """
# NOTE: hello
msg = _('Bonjour à tous')
""")
        messages = list(extract.extract_python(buf, ('_',), ['NOTE:'], {}))
        self.assertEqual(u'Bonjour à tous', messages[0][2])
        self.assertEqual([u'hello'], messages[0][3])

    def test_utf8_raw_strings_match_unicode_strings(self):
        buf = StringIO(codecs.BOM_UTF8 + """
msg = _('Bonjour à tous')
msgu = _(u'Bonjour à tous')
""")
        messages = list(extract.extract_python(buf, ('_',), ['NOTE:'], {}))
        self.assertEqual(u'Bonjour à tous', messages[0][2])
        self.assertEqual(messages[0][2], messages[1][2])

def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(extract))
    suite.addTest(unittest.makeSuite(ExtractPythonTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
