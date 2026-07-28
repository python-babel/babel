#
# Copyright (C) 2007-2011 Edgewall Software, 2013-2025 the Babel team
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution. The terms
# are also available at https://github.com/python-babel/babel/blob/master/LICENSE.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at https://github.com/python-babel/babel/commits/master/.

import os
import pickle
import random
import sys
import tempfile

import pytest

from babel import Locale, UnknownLocaleError, localedata


def test_merge_items():
    d = {1: 'foo', 3: 'baz'}
    localedata.merge(d, {1: 'Foo', 2: 'Bar'})
    assert d == {1: 'Foo', 2: 'Bar', 3: 'baz'}


def test_merge_nested_dict():
    d1 = {'x': {'a': 1, 'b': 2, 'c': 3}}
    d2 = {'x': {'a': 1, 'b': 12, 'd': 14}}
    localedata.merge(d1, d2)
    assert d1 == {'x': {'a': 1, 'b': 12, 'c': 3, 'd': 14}}


def test_merge_nested_dict_no_overlap():
    d1 = {'x': {'a': 1, 'b': 2}}
    d2 = {'y': {'a': 11, 'b': 12}}
    localedata.merge(d1, d2)
    assert d1 == {'x': {'a': 1, 'b': 2}, 'y': {'a': 11, 'b': 12}}


def test_merge_with_alias_and_resolve():
    alias = localedata.Alias('x')
    d1 = {
        'x': {'a': 1, 'b': 2, 'c': 3},
        'y': alias,
    }
    d2 = {
        'x': {'a': 1, 'b': 12, 'd': 14},
        'y': {'b': 22, 'e': 25},
    }
    localedata.merge(d1, d2)
    assert d1 == {'x': {'a': 1, 'b': 12, 'c': 3, 'd': 14}, 'y': (alias, {'b': 22, 'e': 25})}
    d = localedata.LocaleDataDict(d1)
    assert dict(d.items()) == {'x': {'a': 1, 'b': 12, 'c': 3, 'd': 14}, 'y': {'a': 1, 'b': 22, 'c': 3, 'd': 14, 'e': 25}}


def test_localedatadict_resolving_alias_does_not_leak_into_shared_underlying_dict():
    """
    Regression test for
    https://github.com/python-babel/babel/issues/1234

    load() gives each locale its own top-level dict via a shallow
    .copy() of its parent's cached data, and merge() only copies a
    nested dict when the locale's own data file actually has an entry
    at that key. So a nested structure a locale's data file doesn't
    touch at all -- e.g. a "stand-alone" month-name alias, when the
    locale relies entirely on the inherited default -- remains the
    exact same object shared with whatever it last inherited it from,
    even while sibling keys the locale *does* override (e.g. its own
    "format" month names) are correctly independent per locale.

    Resolving an alias must not mutate that shared "stand-alone"
    structure in place, or the resolved value leaks into every other
    locale sharing the same object -- exactly what happened with
    Hebrew's resolved month name leaking into Norwegian's and French's
    month names in the issue.
    """
    # Shared, uncopied 'stand-alone' structure: neither "locale" below
    # overrides it, so (as load()'s shallow copy would produce) they
    # reference the exact same dict object for it.
    shared_standalone = {
        'wide': localedata.Alias(('months', 'format', 'wide')),
    }

    locale_a_data = {
        'months': {
            'format': {'wide': {10: 'LocaleAOctober'}},
            'stand-alone': shared_standalone,
        },
    }
    locale_b_data = {
        'months': {
            'format': {'wide': {10: 'LocaleBOctober'}},
            'stand-alone': shared_standalone,
        },
    }
    # Each locale's own "format" data is independent, but they share
    # the exact same "stand-alone" object -- the precise shape that
    # produces the bug.
    assert locale_a_data['months']['format'] is not locale_b_data['months']['format']
    assert locale_a_data['months']['stand-alone'] is locale_b_data['months']['stand-alone']

    locale_a = localedata.LocaleDataDict(locale_a_data)
    locale_b = localedata.LocaleDataDict(locale_b_data)

    resolved_a = locale_a['months']['stand-alone']['wide']
    assert resolved_a[10] == 'LocaleAOctober'

    # Resolving the alias for locale_a must not affect locale_b's
    # resolution of the same (shared) 'stand-alone' object.
    resolved_b = locale_b['months']['stand-alone']['wide']
    assert resolved_b[10] == 'LocaleBOctober'

    # Re-checking locale_a again afterwards must still be correct too.
    assert locale_a['months']['stand-alone']['wide'][10] == 'LocaleAOctober'


def test_load():
    assert localedata.load('en_US')['languages']['sv'] == 'Swedish'
    assert localedata.load('en_US') is localedata.load('en_US')


def test_load_inheritance(monkeypatch):
    from babel.localedata import _cache

    _cache.clear()
    localedata.load('hi_Latn')
    # Must not be ['root', 'hi_Latn'] even though 'hi_Latn' matches the 'lang_Script'
    # form used by 'nonLikelyScripts'. This is because 'hi_Latn' has an explicit parent locale 'en_IN'.
    assert list(_cache.keys()) == ['root', 'en', 'en_001', 'en_IN', 'hi_Latn']

    _cache.clear()
    localedata.load('az_Arab')
    # Must not include 'az' as 'Arab' is not a likely script for 'az'.
    assert list(_cache.keys()) == ['root', 'az_Arab']


def test_merge():
    d = {1: 'foo', 3: 'baz'}
    localedata.merge(d, {1: 'Foo', 2: 'Bar'})
    assert d == {1: 'Foo', 2: 'Bar', 3: 'baz'}


def test_locale_identification():
    for locale in localedata.locale_identifiers():
        assert localedata.exists(locale)


def test_unique_ids():
    # Check all locale IDs are uniques.
    all_ids = localedata.locale_identifiers()
    assert len(all_ids) == len(set(all_ids))
    # Check locale IDs don't collide after lower-case normalization.
    lower_case_ids = [id.lower() for id in all_ids]
    assert len(lower_case_ids) == len(set(lower_case_ids))


def test_mixedcased_locale():
    for locale in localedata.locale_identifiers():
        locale_id = ''.join(c.lower() if random.random() < 0.5 else c.upper() for c in locale)
        assert localedata.exists(locale_id)


def test_locale_argument_acceptance():
    # Testing None input.
    normalized_locale = localedata.normalize_locale(None)
    assert normalized_locale is None
    assert not localedata.exists(None)

    # Testing tuple input.
    normalized_locale = localedata.normalize_locale(['en_us', None])
    assert normalized_locale is None
    assert not localedata.exists(('en_us', None))


def test_locale_identifiers_cache(monkeypatch):
    original_listdir = localedata.os.listdir
    listdir_calls = []

    def listdir_spy(*args):
        rv = original_listdir(*args)
        listdir_calls.append((args, rv))
        return rv

    monkeypatch.setattr(localedata.os, 'listdir', listdir_spy)
    localedata.locale_identifiers.cache_clear()
    assert not listdir_calls
    l = localedata.locale_identifiers()
    assert len(listdir_calls) == 1
    assert localedata.locale_identifiers() is l
    assert len(listdir_calls) == 1
    localedata.locale_identifiers.cache_clear()
    assert localedata.locale_identifiers()
    assert len(listdir_calls) == 2


def test_locale_name_cleanup():
    """
    Test that locale identifiers are cleaned up to avoid directory traversal.
    """
    no_exist_name = os.path.join(tempfile.gettempdir(), "babel%d.dat" % random.randint(1, 99999))
    with open(no_exist_name, "wb") as f:
        pickle.dump({}, f)

    try:
        name = os.path.splitext(os.path.relpath(no_exist_name, localedata._dirname))[0]
    except ValueError:
        if sys.platform == "win32":
            pytest.skip("unable to form relpath")
        raise

    assert not localedata.exists(name)
    with pytest.raises(IOError):
        localedata.load(name)
    with pytest.raises(UnknownLocaleError):
        Locale(name)


@pytest.mark.skipif(sys.platform != "win32", reason="windows-only test")
def test_reserved_locale_names():
    for name in ("con", "aux", "nul", "prn", "com8", "lpt5"):
        with pytest.raises(ValueError):
            localedata.load(name)
        with pytest.raises(ValueError):
            Locale(name)
