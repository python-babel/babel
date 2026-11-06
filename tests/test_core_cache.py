import pytest

from babel import Locale
from babel.core import _cached_parse_locale, parse_locale


def test_locale_syntax_cache_keys():
    assert parse_locale('en_US') == ('en', 'US', None, None)
    assert parse_locale('en-US', sep='-') == ('en', 'US', None, None)
    with pytest.raises(ValueError, match='expected only letters'):
        parse_locale('en-US')
    assert parse_locale('de_DE.UTF-8@euro') == ('de', 'DE', None, None, 'euro')
    assert parse_locale('de_DE.UTF-8@custom') == ('de', 'DE', None, None, 'custom')


def test_locale_syntax_cache_does_not_share_locales():
    first = Locale.parse('en_US')
    first.language = 'de'
    second = Locale.parse('en_US')
    assert first is not second
    assert second.language == 'en'


def test_locale_syntax_string_subclass_is_not_cached():
    class Identifier(str):
        __hash__ = None
        calls = 0

        def partition(self, sep):
            self.calls += 1
            return ('en_US' if self.calls == 1 else 'de_DE').partition(sep)

    value = Identifier('en_US')
    assert parse_locale(value) == ('en', 'US', None, None)
    assert parse_locale(value) == ('de', 'DE', None, None)
    assert value.calls == 2


def test_locale_syntax_separator_subclass_is_not_hashed():
    class Separator(str):
        __hash__ = None

    assert parse_locale('en-US', sep=Separator('-')) == ('en', 'US', None, None)


@pytest.mark.parametrize('identifier', [[], {}, 0, None])
def test_locale_syntax_empty_unsupported_inputs(identifier):
    with pytest.raises(ValueError, match='^empty locale identifier$'):
        parse_locale(identifier)


def test_locale_syntax_cache_is_bounded():
    _cached_parse_locale.cache_clear()
    for i in range(1100):
        parse_locale(f'en_US@modifier{i}')
    assert _cached_parse_locale.cache_info().currsize == 1024
