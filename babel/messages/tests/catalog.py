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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(catalog))
    suite.addTest(unittest.makeSuite(MessageTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
