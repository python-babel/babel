#
# Copyright (C) 2007-2011 Edgewall Software, 2013-2026 the Babel team
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
    assert dict(d.items()) == {
        'x': {'a': 1, 'b': 12, 'c': 3, 'd': 14},
        'y': {'a': 1, 'b': 22, 'c': 3, 'd': 14, 'e': 25},
    }
    # Resolving the partial alias must not have written the result back into the underlying data (GH-1234)
    assert d1['y'] == (alias, {'b': 22, 'e': 25})


def test_alias_resolving_to_partially_overridden_alias():
    # An alias chain that lands on an `(alias, overrides)` tuple
    # must apply the overrides on top of the resolved target.
    x_alias = localedata.Alias(('x',))
    data = {
        'x': {'a': 1, 'b': 2},
        'y': (x_alias, {'b': 22, 'c': 33}),  # 'x', partially overridden
        'z': localedata.Alias(('y',)),  # an alias landing on the tuple
    }
    expected = {'a': 1, 'b': 22, 'c': 33}
    assert localedata.Alias(('z',)).resolve(data) == expected
    d = localedata.LocaleDataDict(data)
    assert dict(d['z']) == expected
    # Ensure original data is as before:
    assert data['x'] == {'a': 1, 'b': 2}
    assert data['y'] == (x_alias, {'b': 22, 'c': 33})


def test_load():
    assert localedata.load('en_US')['languages']['sv'] == 'Swedish'
    assert localedata.load('en_US') is localedata.load('en_US')


def _calendar_snapshot(name):
    locale = Locale.parse(name)
    return {
        'months': dict(locale.months['stand-alone']['wide']),
        'months_abbr': dict(locale.months['format']['abbreviated']),
        'days': dict(locale.days['stand-alone']['wide']),
        'quarters': dict(locale.quarters['stand-alone']['wide']),
        'eras': dict(locale.eras['wide']),
    }


@pytest.mark.parametrize('reverse', [False, True])
def test_no_cross_locale_contamination(reverse):
    """
    Alias-heavy calendar data (e.g. what `format_date(..., 'LLLL')` reads)
    must be identical whether a locale is loaded into a cold cache or after
    other locales have already been read: e.g.
    * reading 'he' must not turn Norwegian month names Hebrew
    * reading 'aa' must not turn everyone else's stand-alone quarters into root's 'Q1' placeholders.

    Regression test for https://github.com/python-babel/babel/issues/1234
    """
    locales = ('aa', 'de', 'fr', 'he', 'ja', 'no')
    cold = {}
    for name in locales:
        localedata.clear_caches()
        cold[name] = _calendar_snapshot(name)

    assert cold['he']['months'] != cold['de']['months']  # Sanity check

    localedata.clear_caches()
    warm = {
        name: _calendar_snapshot(name) for name in (reversed(locales) if reverse else locales)
    }
    assert warm == cold
    # Repeated reads in the warmed-up state must stay correct too
    assert {name: _calendar_snapshot(name) for name in locales} == cold


def test_manual_locale_data_writes(request):
    """Writes into `Locale(...)._data` (misguided as they may be) must be
    visible to subsequent reads."""

    # Note that this test codifies how Babel has traditionally worked;
    # if you're working on e.g. locale immutability, this test should not
    # be made to pass under that scheme.

    localedata.clear_caches()
    # This test mutates shared cached locale data; start others afresh
    request.addfinalizer(localedata.clear_caches)

    locale = Locale.parse('de')
    # Prime the memoization through both an alias and a plain path
    # (in 'de', stand-alone wide months are a plain Alias to format ones)
    assert locale.months['stand-alone']['wide'][10] == 'Oktober'
    assert locale.months['format']['wide'][10] == 'Oktober'

    # A leaf write must be visible on the next read...
    locale.months['format']['wide'][10] = 'Rocktober'
    assert locale.months['format']['wide'][10] == 'Rocktober'
    # ... also through an alias resolving to the written-to dict ...
    assert locale.months['stand-alone']['wide'][10] == 'Rocktober'
    # ... and (as has always been the case, since writes land in the
    # shared load() data) to other same-name Locale instances.
    assert Locale.parse('de').months['format']['wide'][10] == 'Rocktober'

    # Replacing a whole subtree must invalidate its memoized wrapper
    locale._data['months'] = {'format': {'wide': {10: 'blocktober'}}}
    assert locale.months['format']['wide'][10] == 'blocktober'

    # Deletions must be visible too
    del locale._data['months']
    with pytest.raises(KeyError):
        _ = locale.months['format']


def test_load_inheritance(monkeypatch):
    localedata.clear_caches()
    localedata.load('hi_Latn')
    # Must not be ['root', 'hi_Latn'] even though 'hi_Latn' matches the 'lang_Script'
    # form used by 'nonLikelyScripts'. This is because 'hi_Latn' has an explicit parent locale 'en_IN'.
    assert set(localedata._cache) == {'root', 'en', 'en_001', 'en_IN', 'hi_Latn'}

    localedata.clear_caches()
    localedata.load('az_Arab')
    # Must not include 'az' as 'Arab' is not a likely script for 'az'.
    assert set(localedata._cache) == {'root', 'az_Arab'}


def test_merge():
    d = {1: 'foo', 3: 'baz'}
    localedata.merge(d, {1: 'Foo', 2: 'Bar'})
    assert d == {1: 'Foo', 2: 'Bar', 3: 'baz'}


def test_locale_identification():
    for locale in localedata.locale_identifiers():
        assert localedata.exists(locale)


def test_locale_count():
    """
    Smoke test to keep track of how many locales babel defines
    now that CLDR 50 is planning to remove locales with below
    Basic coverage.
    """
    assert len(localedata.locale_identifiers()) == 1147


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


def test_locale_name_cleanup(tmp_path):
    """
    Test that locale identifiers are cleaned up to avoid directory traversal.
    """
    no_exist_path = tmp_path / f"babel{random.randint(1, 99999):d}.dat"
    no_exist_path.write_bytes(pickle.dumps({}))

    try:
        name = os.path.splitext(os.path.relpath(no_exist_path, localedata._dirname))[0]
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


@pytest.mark.parametrize('compression', [0, 8])
def test_zipimport_data(tmp_path, compression):
    """Read real package data from an archive without directory entries."""
    import subprocess
    import zipfile
    from pathlib import Path

    import babel

    package = Path(babel.__file__).parent
    archive = tmp_path / 'babel.zip'
    with zipfile.ZipFile(archive, 'w', compression=compression) as zf:
        for source in package.rglob('*.py'):
            zf.write(source, str(source.relative_to(package.parent)))
        for name in (
            'global.dat',
            'locale-data/root.dat',
            'locale-data/en.dat',
            'locale-data/en_US.dat',
            'locale-data/fr.dat',
        ):
            zf.write(package / name, f'babel/{name}')
    script = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
import babel
from babel import localedata
from babel.core import Locale, UnknownLocaleError, get_global
from babel.numbers import format_decimal
assert '.zip/' in babel.__file__.replace('\\', '/')
assert get_global('zone_aliases')['UTC'] == 'Etc/UTC'
assert set(localedata.locale_identifiers()) == {'en', 'en_US', 'fr'}
assert localedata.exists('en_US')
assert localedata.exists('EN_us')
assert not localedata.exists('xx_XX')
assert not localedata.exists('../unknown')
assert localedata.normalize_locale(' EN_us ') == 'en_US'
assert localedata.load('en_US')['languages']['sv'] == 'Swedish'
assert localedata.load('en_US') is localedata.load('en_US')
assert localedata.load('../en_US') is localedata.load('en_US')
assert format_decimal(12345.67, locale='en_US') == '12,345.67'
assert format_decimal(12345.67, locale='fr') == '12\u202f345,67'
try:
    localedata.load('xx')
except FileNotFoundError:
    pass
else:
    raise AssertionError('missing data did not raise FileNotFoundError')
try:
    Locale('xx_XX')
except UnknownLocaleError:
    pass
else:
    raise AssertionError('unknown locale did not raise UnknownLocaleError')
print('ok')
"""
    result = subprocess.run(
        [sys.executable, '-c', script, str(archive)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'ok'


def test_custom_locale_directory_is_not_replaced(tmp_path, monkeypatch):
    """A caller-provided data directory must never fall back to package data."""
    monkeypatch.setattr(localedata, '_dirname', str(tmp_path))
    localedata.clear_caches()
    localedata.exists.cache_clear()
    localedata.locale_identifiers.cache_clear()
    try:
        assert localedata.locale_identifiers() == []
        assert not localedata.exists('en_US')
        with pytest.raises(FileNotFoundError):
            localedata.load('en_US')
        (tmp_path / 'root.dat').write_bytes(pickle.dumps({'test': 'custom'}))
        (tmp_path / 'en.dat').write_bytes(pickle.dumps({'test': 'English'}))
        localedata.locale_identifiers.cache_clear()
        assert localedata.locale_identifiers() == ['en']
        assert localedata.load('root')['test'] == 'custom'
        assert localedata.load('en')['test'] == 'English'
    finally:
        localedata.clear_caches()
        localedata.exists.cache_clear()
        localedata.locale_identifiers.cache_clear()


@pytest.mark.parametrize('global_data', [None, b'not a pickle'])
def test_zipimport_invalid_global_data(tmp_path, global_data):
    import subprocess
    import zipfile
    from pathlib import Path

    import babel

    package = Path(babel.__file__).parent
    archive = tmp_path / 'babel.zip'
    with zipfile.ZipFile(archive, 'w') as zf:
        for source in package.rglob('*.py'):
            zf.write(source, str(source.relative_to(package.parent)))
        if global_data is not None:
            zf.writestr('babel/global.dat', global_data)
    expected = 'RuntimeError' if global_data is None else 'UnpicklingError'
    script = r"""
import pickle, sys
sys.path.insert(0, sys.argv[1])
from babel.core import get_global
try:
    get_global('zone_aliases')
except (RuntimeError, pickle.UnpicklingError) as exc:
    assert type(exc).__name__ == sys.argv[2], repr(exc)
    if isinstance(exc, RuntimeError):
        assert 'make import-cldr' in str(exc)
else:
    raise AssertionError('invalid global data did not raise')
"""
    result = subprocess.run(
        [sys.executable, '-c', script, str(archive), expected],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
