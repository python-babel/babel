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
import random
from operator import methodcaller

from babel import localedata


class MergeResolveTestCase(unittest.TestCase):

    def test_merge_items(self):
        d = {1: 'foo', 3: 'baz'}
        localedata.merge(d, {1: 'Foo', 2: 'Bar'})
        self.assertEqual({1: 'Foo', 2: 'Bar', 3: 'baz'}, d)

    def test_merge_nested_dict(self):
        d1 = {'x': {'a': 1, 'b': 2, 'c': 3}}
        d2 = {'x': {'a': 1, 'b': 12, 'd': 14}}
        localedata.merge(d1, d2)
        self.assertEqual({
            'x': {'a': 1, 'b': 12, 'c': 3, 'd': 14}
        }, d1)

    def test_merge_nested_dict_no_overlap(self):
        d1 = {'x': {'a': 1, 'b': 2}}
        d2 = {'y': {'a': 11, 'b': 12}}
        localedata.merge(d1, d2)
        self.assertEqual({
            'x': {'a': 1, 'b': 2},
            'y': {'a': 11, 'b': 12}
        }, d1)

    def test_merge_with_alias_and_resolve(self):
        alias = localedata.Alias('x')
        d1 = {
            'x': {'a': 1, 'b': 2, 'c': 3},
            'y': alias
        }
        d2 = {
            'x': {'a': 1, 'b': 12, 'd': 14},
            'y': {'b': 22, 'e': 25}
        }
        localedata.merge(d1, d2)
        self.assertEqual({
            'x': {'a': 1, 'b': 12, 'c': 3, 'd': 14},
            'y': (alias, {'b': 22, 'e': 25})
        }, d1)
        d = localedata.LocaleDataDict(d1)
        self.assertEqual({
            'x': {'a': 1, 'b': 12, 'c': 3, 'd': 14},
            'y': {'a': 1, 'b': 22, 'c': 3, 'd': 14, 'e': 25}
        }, dict(d.items()))


def test_load():
    assert localedata.load('en_US')['languages']['sv'] == 'Swedish'
    assert localedata.load('en_US') is localedata.load('en_US')


def test_merge():
    d = {1: 'foo', 3: 'baz'}
    localedata.merge(d, {1: 'Foo', 2: 'Bar'})
    assert d == {1: 'Foo', 2: 'Bar', 3: 'baz'}


def test_locale_identification():
    for l in localedata.locale_identifiers():
        assert localedata.exists(l)


def test_unique_ids():
    # Check all locale IDs are uniques.
    all_ids = localedata.locale_identifiers()
    assert len(all_ids) == len(set(all_ids))
    # Check locale IDs don't collide after lower-case normalization.
    lower_case_ids = list(map(methodcaller('lower'), all_ids))
    assert len(lower_case_ids) == len(set(lower_case_ids))


def test_mixedcased_locale():
    for l in localedata.locale_identifiers():
        locale_id = ''.join([
            methodcaller(random.choice(['lower', 'upper']))(c) for c in l])
        assert localedata.exists(locale_id)
