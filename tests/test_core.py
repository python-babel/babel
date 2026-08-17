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

import pytest

from babel import core
from babel.core import Locale, default_locale


def test_can_return_default_locale(monkeypatch):
    monkeypatch.setenv('LC_MESSAGES', 'fr_FR.UTF-8')
    assert Locale('fr', 'FR') == Locale.default('LC_MESSAGES')


def test_ignore_invalid_locales_in_lc_ctype(monkeypatch):
    # This is a regression test specifically for a bad LC_CTYPE setting on
    # MacOS X 10.6 (#200)
    monkeypatch.setenv('LC_CTYPE', 'UTF-8')
    # must not throw an exception
    default_locale('LC_CTYPE')


def test_zone_aliases_and_territories():
    aliases = core.get_global('zone_aliases')
    territories = core.get_global('zone_territories')
    assert aliases['GMT'] == 'Etc/GMT'
    assert aliases['UTC'] == 'Etc/UTC'
    assert territories['Europe/Berlin'] == 'DE'
    # Check that the canonical (IANA) names are used in `territories`,
    # but that aliases are still available.
    assert territories['Africa/Asmara'] == 'ER'
    assert aliases['Africa/Asmera'] == 'Africa/Asmara'
    assert territories['Europe/Kyiv'] == 'UA'
    assert aliases['Europe/Kiev'] == 'Europe/Kyiv'


def test_default_locale(monkeypatch):
    for name in ['LANGUAGE', 'LANG', 'LC_ALL', 'LC_CTYPE', 'LC_MESSAGES']:
        monkeypatch.setenv(name, '')
    monkeypatch.setenv('LANG', 'fr_FR.UTF-8')
    assert default_locale('LC_MESSAGES') == 'fr_FR'
    monkeypatch.setenv('LC_MESSAGES', 'POSIX')
    assert default_locale('LC_MESSAGES') == 'en_US_POSIX'

    for value in ['C', 'C.UTF-8', 'POSIX']:
        monkeypatch.setenv('LANGUAGE', value)
        assert default_locale() == 'en_US_POSIX'


def test_default_locale_multiple_args(monkeypatch):
    for name in [
        'LANGUAGE',
        'LANG',
        'LC_ALL',
        'LC_CTYPE',
        'LC_MESSAGES',
        'LC_MONETARY',
        'LC_NUMERIC',
    ]:
        monkeypatch.setenv(name, '')
    assert default_locale(["", 0, None]) is None
    monkeypatch.setenv('LANG', 'en_US')

    # No LC_MONETARY or LC_NUMERIC set
    assert default_locale(('LC_MONETARY', 'LC_NUMERIC')) == 'en_US'

    # LC_NUMERIC set
    monkeypatch.setenv('LC_NUMERIC', 'fr_FR.UTF-8')
    assert default_locale(('LC_MONETARY', 'LC_NUMERIC')) == 'fr_FR'

    # LC_MONETARY set, it takes precedence
    monkeypatch.setenv('LC_MONETARY', 'fi_FI.UTF-8')
    assert default_locale(('LC_MONETARY', 'LC_NUMERIC')) == 'fi_FI'


def test_default_locale_bad_arg():
    with pytest.raises(TypeError):
        default_locale(42)


def test_negotiate_locale():
    assert core.negotiate_locale(['de_DE', 'en_US'], ['de_DE', 'de_AT']) == 'de_DE'
    assert core.negotiate_locale(['de_DE', 'en_US'], ['en', 'de']) == 'de'
    assert core.negotiate_locale(['de_DE', 'en_US'], ['de_de', 'de_at']) == 'de_DE'
    assert core.negotiate_locale(['de_DE', 'en_US'], ['de_de', 'de_at']) == 'de_DE'
    assert core.negotiate_locale(['ja', 'en_US'], ['ja_JP', 'en_US']) == 'ja_JP'
    assert core.negotiate_locale(['no', 'sv'], ['nb_NO', 'sv_SE']) == 'nb_NO'


def test_parse_locale():
    assert core.parse_locale('zh_CN') == ('zh', 'CN', None, None)
    assert core.parse_locale('zh_Hans_CN') == ('zh', 'CN', 'Hans', None)
    assert core.parse_locale('zh-CN', sep='-') == ('zh', 'CN', None, None)

    with pytest.raises(ValueError, match="'not_a_LOCALE_String' is not a valid locale identifier"):
        core.parse_locale('not_a_LOCALE_String')

    assert core.parse_locale('it_IT@euro') == ('it', 'IT', None, None, 'euro')
    assert core.parse_locale('it_IT@something') == ('it', 'IT', None, None, 'something')

    assert core.parse_locale('en_US.UTF-8') == ('en', 'US', None, None)
    assert core.parse_locale('de_DE.iso885915@euro') == ('de', 'DE', None, None, 'euro')

    with pytest.raises(ValueError, match="empty"):
        core.parse_locale("")


@pytest.mark.parametrize(
    'filename',
    [
        'babel/global.dat',
        'babel/locale-data/root.dat',
        'babel/locale-data/en.dat',
        'babel/locale-data/en_US.dat',
        'babel/locale-data/en_US_POSIX.dat',
        'babel/locale-data/zh_Hans_CN.dat',
        'babel/locale-data/zh_Hant_TW.dat',
        'babel/locale-data/es_419.dat',
    ],
)
def test_compatible_classes_in_global_and_localedata(filename):
    import pickle

    class Unpickler(pickle.Unpickler):
        def find_class(self, module, name):
            # *.dat files must have compatible classes between Python 2 and 3
            if module.split('.')[0] == 'babel':
                return pickle.Unpickler.find_class(self, module, name)
            raise pickle.UnpicklingError(f"global '{module}.{name}' is forbidden")

    with open(filename, 'rb') as f:
        assert Unpickler(f).load()


def test_issue_601_no_language_name_but_has_variant():
    # kw_GB has a variant for Finnish but no actual language name for Finnish,
    # so `get_display_name()` previously crashed with a TypeError as it attempted
    # to concatenate " (Finnish)" to None.
    # Instead, it's better to return None altogether, as we can't reliably format
    # part of a language name.

    assert Locale.parse('fi_FI').get_display_name('kw_GB') is None


def test_issue_814():
    loc = Locale.parse('ca_ES_valencia')
    assert loc.variant == "VALENCIA"
    assert loc.get_display_name() == 'català (Espanya, valencià)'


def test_issue_1112():
    """
    Test that an alternate spelling of `Türkei` doesn't inadvertently
    get imported from `de_AT` to replace the parent's non-alternate spelling.
    """
    assert (
        Locale.parse('de').territories['TR']
        == Locale.parse('de_AT').territories['TR']
        == Locale.parse('de_CH').territories['TR']
        == Locale.parse('de_DE').territories['TR']
        == 'Türkei'
    )


def test_locale_parse_empty():
    with pytest.raises(ValueError, match="Empty") as ei:
        Locale.parse("")
    assert isinstance(ei.value.args[0], str)
    with pytest.raises(TypeError, match="Empty"):
        Locale.parse(None)
    with pytest.raises(TypeError, match="Empty"):
        Locale.parse(False)  # weird...!


def test_get_cldr_version():
    assert core.get_cldr_version() == "48"
