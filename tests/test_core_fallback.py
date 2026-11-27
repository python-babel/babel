import pytest

from babel import Locale, UnknownLocaleError


def test_locale_parse_preserves_subclass_construction():
    calls = []

    class CustomLocale(Locale):
        def __init__(self, *args):
            calls.append(args)
            super().__init__(*args)

    locale = CustomLocale.parse('en_US')
    assert type(locale) is CustomLocale
    assert calls == [('en', 'US', None, None)]
    calls.clear()
    locale = CustomLocale.parse('zh_TW')
    assert type(locale) is CustomLocale
    assert str(locale) == 'zh_Hant_TW'
    assert calls[0] == ('zh', 'TW', None, None)
    assert len(calls) > 1


def test_locale_parse_accepts_non_locale_constructor_result():
    sentinel = object()

    class CustomLocale(Locale):
        def __new__(cls, *args):
            return sentinel

    assert CustomLocale.parse('en_US') is sentinel


def test_locale_parse_none_constructor_result_falls_back():
    class CustomLocale(Locale):
        def __new__(cls, *args):
            return None

    with pytest.raises(UnknownLocaleError, match="unknown locale 'en_US'"):
        CustomLocale.parse('en_US', resolve_likely_subtags=False)


def test_locale_parse_does_not_catch_other_constructor_errors():
    class CustomLocale(Locale):
        def __init__(self, *args):
            raise ValueError('custom constructor failure')

    with pytest.raises(ValueError, match='^custom constructor failure$'):
        CustomLocale.parse('en_US')
