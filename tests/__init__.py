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
    from babel.tests import (test_core, test_dates, test_localedata,
                             test_numbers, test_plural, test_support,
                             test_util)
    from babel.messages import tests as test_messages
    suite = unittest.TestSuite()
    suite.addTest(test_core.suite())
    suite.addTest(test_dates.suite())
    suite.addTest(test_localedata.suite())
    suite.addTest(test_messages.suite())
    suite.addTest(test_numbers.suite())
    suite.addTest(test_plural.suite())
    suite.addTest(test_support.suite())
    suite.addTest(test_util.suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
