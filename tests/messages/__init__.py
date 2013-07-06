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

import unittest

def suite():
    from babel.messages.tests import (
        test_catalog, test_extract, test_frontend, test_mofile,
        test_plurals, test_pofile, test_checkers)
    suite = unittest.TestSuite()
    suite.addTest(test_catalog.suite())
    suite.addTest(test_extract.suite())
    suite.addTest(test_frontend.suite())
    suite.addTest(test_mofile.suite())
    suite.addTest(test_plurals.suite())
    suite.addTest(test_pofile.suite())
    suite.addTest(test_checkers.suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
