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
import unittest

from babel import util


def test_distinct():
    assert list(util.distinct([1, 2, 1, 3, 4, 4])) == [1, 2, 3, 4]
    assert list(util.distinct('foobar')) == ['f', 'o', 'b', 'a', 'r']


def test_pathmatch():
    assert util.pathmatch('**.py', 'bar.py')
    assert util.pathmatch('**.py', 'foo/bar/baz.py')
    assert not util.pathmatch('**.py', 'templates/index.html')
    assert util.pathmatch('**/templates/*.html', 'templates/index.html')
    assert not util.pathmatch('**/templates/*.html', 'templates/foo/bar.html')


def suite():
    suite = unittest.TestSuite()
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
