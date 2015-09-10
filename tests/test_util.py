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

from datetime import datetime, timedelta
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

    # Attributes

    def test_zone(self):
        self.assertEqual('Etc/GMT-60', util.FixedOffsetTimezone(-60).zone)
        self.assertEqual('Etc/GMT+0', util.FixedOffsetTimezone(0).zone)
        self.assertEqual('Etc/GMT+330', util.FixedOffsetTimezone(330).zone)

        self.assertEqual('UTC', util.FixedOffsetTimezone(0, 'UTC').zone)
        self.assertEqual('WAT', util.FixedOffsetTimezone(60, 'WAT').zone)

    # Builtins

    def test_str(self):
        self.assertEqual('Etc/GMT+0', str(util.FixedOffsetTimezone(0)))
        self.assertEqual('UTC', str(util.FixedOffsetTimezone(0, 'UTC')))

    def test_repr(self):
        self.assertEqual('<FixedOffset "Etc/GMT-60" -1 day, 23:00:00>',
                         repr(util.FixedOffsetTimezone(-60)))
        self.assertEqual('<FixedOffset "Etc/GMT+0" 0:00:00>',
                         repr(util.FixedOffsetTimezone(0)))
        self.assertEqual('<FixedOffset "Etc/GMT+330" 5:30:00>',
                         repr(util.FixedOffsetTimezone(330)))

    # Methods

    def test_utcoffset(self):
        dt = datetime(2000, 1, 31, 23, 59, 0)
        self.assertEqual(timedelta(0),
                         util.FixedOffsetTimezone(0).utcoffset(dt))

    def test_tzname(self):
        dt = datetime(2000, 1, 31, 23, 59, 0)
        self.assertEqual('Etc/GMT+0', util.FixedOffsetTimezone(0).tzname(dt))
        self.assertEqual('UTC', util.FixedOffsetTimezone(0, 'UTC').tzname(dt))

    def test_dst_january(self):
        dt = datetime(2000, 1, 31, 23, 59, 0)
        self.assertEqual(timedelta(0), util.FixedOffsetTimezone(0).dst(dt))
        self.assertEqual(timedelta(0), util.FixedOffsetTimezone(60).dst(dt))

    def test_dst_august(self):
        dt = datetime(2000, 8, 31, 23, 59, 0)
        self.assertEqual(timedelta(0), util.FixedOffsetTimezone(0).dst(dt))
        self.assertEqual(timedelta(0), util.FixedOffsetTimezone(60).dst(dt))