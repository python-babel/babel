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
import gettext
import os
import unittest
from StringIO import StringIO

from babel.messages import mofile, Catalog


class ReadMoTestCase(unittest.TestCase):

    def setUp(self):
        self.datadir = os.path.join(os.path.dirname(__file__), 'data')

    def test_basics(self):
        mo_file = open(os.path.join(self.datadir, 'project', 'i18n', 'de',
                                    'LC_MESSAGES', 'messages.mo'))
        try:
            catalog = mofile.read_mo(mo_file)
            self.assertEqual(2, len(catalog))
            self.assertEqual('TestProject', catalog.project)
            self.assertEqual('0.1', catalog.version)
            self.assertEqual('Stange', catalog['bar'].string)
            self.assertEqual(['Fuhstange', 'Fuhstangen'],
                             catalog['foobar'].string)
        finally:
            mo_file.close()


class WriteMoTestCase(unittest.TestCase):

    def test_sorting(self):
        # Ensure the header is sorted to the first entry so that its charset
        # can be applied to all subsequent messages by GNUTranslations
        # (ensuring all messages are safely converted to unicode)
        catalog = Catalog(locale='en_US')
        catalog.add(u'', '''\
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n''')
        catalog.add(u'foo', 'Voh')
        catalog.add((u'There is', u'There are'), (u'Es gibt', u'Es gibt'))
        catalog.add(u'Fizz', '')
        catalog.add(('Fuzz', 'Fuzzes'), ('', ''))
        buf = StringIO()
        mofile.write_mo(buf, catalog)
        buf.seek(0)
        translations = gettext.GNUTranslations(fp=buf)
        self.assertEqual(u'Voh', translations.ugettext('foo'))
        assert isinstance(translations.ugettext('foo'), unicode)
        self.assertEqual(u'Es gibt', translations.ungettext('There is', 'There are', 1))
        assert isinstance(translations.ungettext('There is', 'There are', 1), unicode)
        self.assertEqual(u'Fizz', translations.ugettext('Fizz'))
        assert isinstance(translations.ugettext('Fizz'), unicode)
        self.assertEqual(u'Fuzz', translations.ugettext('Fuzz'))
        assert isinstance(translations.ugettext('Fuzz'), unicode)
        self.assertEqual(u'Fuzzes', translations.ugettext('Fuzzes'))
        assert isinstance(translations.ugettext('Fuzzes'), unicode)

    def test_more_plural_forms(self):
        catalog2 = Catalog(locale='ru_RU')
        catalog2.add(('Fuzz', 'Fuzzes'), ('', '', ''))
        buf = StringIO()
        mofile.write_mo(buf, catalog2)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(mofile, optionflags=doctest.ELLIPSIS))
    suite.addTest(unittest.makeSuite(ReadMoTestCase))
    suite.addTest(unittest.makeSuite(WriteMoTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
