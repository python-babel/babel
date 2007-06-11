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

from babel.messages import extract


class ExtractPythonTestCase(unittest.TestCase):

    def test_unicode_string_arg(self):
        buf = StringIO("msg = _(u'Foo Bar')")
        messages = list(extract.extract_python(buf, ('_',), [], {}))
        self.assertEqual('Foo Bar', messages[0][2])

    def test_comment_tag(self):
        buf = StringIO("""
# NOTE: A translation comment
msg = _(u'Foo Bar')
""")
        messages = list(extract.extract_python(buf, ('_',), ['NOTE:'], {}))
        self.assertEqual('Foo Bar', messages[0][2])
        self.assertEqual(['A translation comment'], messages[0][3])

    def test_comment_tag_multiline(self):
        buf = StringIO("""
# NOTE: A translation comment
# with a second line
msg = _(u'Foo Bar')
""")
        messages = list(extract.extract_python(buf, ('_',), ['NOTE:'], {}))
        self.assertEqual('Foo Bar', messages[0][2])
        self.assertEqual(['A translation comment', 'with a second line'],
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
        self.assertEqual('Foo Bar', messages[0][2])
        self.assertEqual(['A translation comment', 'with a second line'],
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
        self.assertEqual('Foo Bar', messages[0][2])
        self.assertEqual(['This one will be'], messages[0][3])
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(extract))
    suite.addTest(unittest.makeSuite(ExtractPythonTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
