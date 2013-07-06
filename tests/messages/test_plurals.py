# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2011 Edgewall Software
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

from babel.messages import plurals


def test_get_plural():
    assert plurals.get_plural(locale='en') == (2, '(n != 1)')
    assert plurals.get_plural(locale='ga') == (3, '(n==1 ? 0 : n==2 ? 1 : 2)')

    tup = plurals.get_plural("ja")
    assert tup.num_plurals == 1
    assert tup.plural_expr == '0'
    assert tup.plural_forms == 'npurals=1; plural=0'
    assert str(tup) == 'npurals=1; plural=0'

def suite():
    suite = unittest.TestSuite()
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
