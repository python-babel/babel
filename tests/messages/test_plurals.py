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
    """Test get_plural. See http://localization-guide.readthedocs.org/en/latest/l10n/pluralforms.html for more details."""
    assert plurals.get_plural(locale='en') == (2, '(n != 1)')
    assert plurals.get_plural(locale='ga') == (3, '(n==1 ? 0 : n==2 ? 1 : 2)')

    plural_ja = plurals.get_plural("ja")
    assert str(plural_ja) == 'nplurals=1; plural=0;'
    assert plural_ja.num_plurals == 1
    assert plural_ja.plural_expr == '0'
    assert plural_ja.plural_forms == 'nplurals=1; plural=0;'

    plural_en_US = plurals.get_plural('en_US')
    assert str(plural_en_US) == 'nplurals=2; plural=(n != 1);'
    assert plural_en_US.num_plurals == 2
    assert plural_en_US.plural_expr == '(n != 1)'

    plural_fr_FR = plurals.get_plural('fr_FR')
    assert str(plural_fr_FR) == 'nplurals=2; plural=(n > 1);'
    assert plural_fr_FR.num_plurals == 2
    assert plural_fr_FR.plural_expr == '(n > 1)'

    plural_pl_PL = plurals.get_plural('pl_PL')
    assert str(plural_pl_PL) == 'nplurals=3; plural=(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);'
    assert plural_pl_PL.num_plurals == 3
    assert plural_pl_PL.plural_expr == '(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
