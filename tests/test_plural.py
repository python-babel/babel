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

from babel import plural


class test_plural_rule():
    rule = plural.PluralRule({'one': 'n is 1'})
    assert rule(1) == 'one'
    assert rule(2) == 'other'

    rule = plural.PluralRule({'one': 'n is 1'})
    assert rule.rules == {'one': 'n is 1'}


def test_to_javascript():
    assert (plural.to_javascript({'one': 'n is 1'})
            == "(function(n) { return (n == 1) ? 'one' : 'other'; })")


def test_to_python():
    func = plural.to_python({'one': 'n is 1', 'few': 'n in 2..4'})
    assert func(1) == 'one'
    assert func(3) == 'few'

    func = plural.to_python({'one': 'n in 1,11', 'few': 'n in 3..10,13..19'})
    assert func(11) == 'one'
    assert func(15) == 'few'


def test_to_gettext():
    assert (plural.to_gettext({'one': 'n is 1', 'two': 'n is 2'})
            == 'nplurals=3; plural=((n == 1) ? 0 : (n == 2) ? 1 : 2)')


def test_in_range_list():
    assert plural.in_range_list(1, [(1, 3)])
    assert plural.in_range_list(3, [(1, 3)])
    assert plural.in_range_list(3, [(1, 3), (5, 8)])
    assert not plural.in_range_list(1.2, [(1, 4)])
    assert not plural.in_range_list(10, [(1, 4)])
    assert not plural.in_range_list(10, [(1, 4), (6, 8)])


def test_within_range_list():
    assert plural.within_range_list(1, [(1, 3)])
    assert plural.within_range_list(1.0, [(1, 3)])
    assert plural.within_range_list(1.2, [(1, 4)])
    assert plural.within_range_list(8.8, [(1, 4), (7, 15)])
    assert not plural.within_range_list(10, [(1, 4)])
    assert not plural.within_range_list(10.5, [(1, 4), (20, 30)])


def test_cldr_modulo():
    assert plural.cldr_modulo(-3, 5) == -3
    assert plural.cldr_modulo(-3, -5) == -3
    assert plural.cldr_modulo(3, 5) == 3


def test_plural_within_rules():
    p = plural.PluralRule({'one': 'n is 1', 'few': 'n within 2,4,7..9'})
    assert repr(p) == "<PluralRule 'one: n is 1, few: n within 2,4,7..9'>"
    assert plural.to_javascript(p) == (
        "(function(n) { "
            "return ((n == 2) || (n == 4) || (n >= 7 && n <= 9))"
            " ? 'few' : (n == 1) ? 'one' : 'other'; })")
    assert plural.to_gettext(p) == (
        'nplurals=3; plural=(((n == 2) || (n == 4) || (n >= 7 && n <= 9))'
        ' ? 1 : (n == 1) ? 0 : 2)')
    assert p(0) == 'other'
    assert p(1) == 'one'
    assert p(2) == 'few'
    assert p(3) == 'other'
    assert p(4) == 'few'
    assert p(5) == 'other'
    assert p(6) == 'other'
    assert p(7) == 'few'
    assert p(8) == 'few'
    assert p(9) == 'few'


def test_locales_with_no_plural_rules_have_default():
    from babel import Locale
    aa_plural = Locale.parse('aa').plural_form
    assert aa_plural(1) == 'other'
    assert aa_plural(2) == 'other'
    assert aa_plural(15) == 'other'
