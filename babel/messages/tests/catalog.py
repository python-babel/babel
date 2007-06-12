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

from babel.messages import catalog


class MessageTestCase(unittest.TestCase):

    def test_python_format(self):
        assert catalog.PYTHON_FORMAT('foo %d bar')
        assert catalog.PYTHON_FORMAT('foo %s bar')
        assert catalog.PYTHON_FORMAT('foo %r bar')        
    
    def test_translator_comments(self):
        mess = catalog.Message('foo', comments=['Comment About `foo`'])
        self.assertEqual(mess.comments, ['Comment About `foo`'])        
        mess = catalog.Message('foo',
                               comments=['Comment 1 About `foo`',
                                         'Comment 2 About `foo`'])
        self.assertEqual(mess.comments, ['Comment 1 About `foo`',
                                         'Comment 2 About `foo`'])


class CatalogTestCase(unittest.TestCase):

    def test_two_messages_with_same_singular(self):
        cat = catalog.Catalog()
        cat.add('foo')
        cat.add(('foo', 'foos'))
        self.assertEqual(1, len(cat))

    def test_update_message_updates_comments(self):
        cat = catalog.Catalog()
        cat[u'foo'] = catalog.Message('foo', locations=[('main.py', 5)])
        self.assertEqual(cat[u'foo'].comments, [])
        # Update cat[u'foo'] with a new location and a comment
        cat[u'foo'] = catalog.Message('foo', locations=[('main.py', 7)],
                                      comments=['Foo Bar comment 1'])
        self.assertEqual(cat[u'foo'].comments, ['Foo Bar comment 1'])
        # now add yet another location with another comment
        cat[u'foo'] = catalog.Message('foo', locations=[('main.py', 9)],
                                      comments=['Foo Bar comment 2'])        
        self.assertEqual(cat[u'foo'].comments,
                         ['Foo Bar comment 1', 'Foo Bar comment 2'])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(catalog, optionflags=doctest.ELLIPSIS))
    suite.addTest(unittest.makeSuite(MessageTestCase))
    suite.addTest(unittest.makeSuite(CatalogTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
