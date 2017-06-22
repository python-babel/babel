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

from babel import util
from babel._compat import BytesIO


def test_distinct():
    assert list(util.distinct([1, 2, 1, 3, 4, 4])) == [1, 2, 3, 4]
    assert list(util.distinct('foobar')) == ['f', 'o', 'b', 'a', 'r']


def test_pathmatch():
    assert util.pathmatch('**.py', 'bar.py')
    assert util.pathmatch('**.py', 'foo/bar/baz.py')
    assert not util.pathmatch('**.py', 'templates/index.html')
    assert util.pathmatch('**/templates/*.html', 'templates/index.html')
    assert not util.pathmatch('**/templates/*.html', 'templates/foo/bar.html')


def test_odict_pop():
    odict = util.odict()
    odict[0] = 1
    value = odict.pop(0)
    assert 1 == value
    assert [] == list(odict.items())
    assert odict.pop(2, None) is None
    try:
        odict.pop(2)
        assert False
    except KeyError:
        assert True


class FixedOffsetTimezoneTestCase(unittest.TestCase):

    def test_zone_negative_offset(self):
        self.assertEqual('Etc/GMT-60', util.FixedOffsetTimezone(-60).zone)

    def test_zone_zero_offset(self):
        self.assertEqual('Etc/GMT+0', util.FixedOffsetTimezone(0).zone)

    def test_zone_positive_offset(self):
        self.assertEqual('Etc/GMT+330', util.FixedOffsetTimezone(330).zone)


parse_encoding = lambda s: util.parse_encoding(BytesIO(s.encode('utf-8')))


def test_parse_encoding_defined():
    assert parse_encoding(u'# coding: utf-8') == 'utf-8'


def test_parse_encoding_undefined():
    assert parse_encoding(u'') is None


def test_parse_encoding_non_ascii():
    assert parse_encoding(u'K\xf6ln') is None
