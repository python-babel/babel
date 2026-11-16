import pytest

from babel import Locale, lists, units


@pytest.mark.parametrize(
    ('list', 'locale', 'expected'),
    [
        ([], 'en', ''),
        (['string'], 'en', 'string'),
        (['string1', 'string2'], 'en', 'string1 and string2'),
        (['string1', 'string2', 'string3'], 'en', 'string1, string2, and string3'),
        (['string1', 'string2', 'string3'], 'zh', 'string1、string2和string3'),
        (
            ['string1', 'string2', 'string3', 'string4'],
            'ne',
            'string1, string2, string3 र string4',
        ),
    ],
)
def test_format_list(list, locale, expected):
    assert lists.format_list(list, locale=locale) == expected


def test_format_list_error():
    with pytest.raises(ValueError):
        lists.format_list(['a', 'b', 'c'], style='orange', locale='en')


def test_issue_1098():
    one_foot = units.format_unit(1, "length-foot", length="short", locale="zh_CN")
    five_inches = units.format_unit(5, "length-inch", length="short", locale="zh_CN")
    # zh-CN does not specify the "unit" style, so we fall back to "unit-short" style.
    assert (
        lists.format_list([one_foot, five_inches], style="unit", locale="zh_CN")
        == lists.format_list([one_foot, five_inches], style="unit-short", locale="zh_CN")
        ==
        # Translation verified using Google Translate. It would add more spacing, but the glyphs are correct.
        "1英尺5英寸"
    )


def test_lists_default_locale_deprecation():
    with pytest.warns(DeprecationWarning):
        _ = lists.DEFAULT_LOCALE


@pytest.mark.parametrize(
    ('list', 'style', 'locale', 'expected'),
    [
        # Styles defining only some parts get the missing ones from fallback styles.
        (['A', 'B', 'C'], 'unit', 'de', 'A, B und C'),
        (['A', 'B', 'C'], 'standard-narrow', 'fr', 'A, B, C'),
        (['A', 'B', 'C', 'D'], 'standard-narrow', 'fr', 'A, B, C, D'),
        (['A', 'B', 'C'], 'unit', 'hy', 'A, B և C'),
        (['A', 'B', 'C'], 'unit-narrow', 'is', 'A B og C'),
        (['A', 'B', 'C'], 'unit', 'ar_OM', 'A، وB، وC'),
        # The nearest fallback style wins: 'end' from standard-short, 'start' from standard.
        (['A', 'B', 'C'], 'standard-narrow', 'wo_SN', 'A, B, & C'),
        # Two items with no '2' part use the fallback '2' pattern.
        (['A', 'B'], 'standard-short', 'hi', 'A और B'),
        (['A', 'B'], 'standard-narrow', 'lo', 'A ແລະ B'),
        (['A', 'B'], 'unit-narrow', 'wo_SN', 'A, B'),
        (['A', 'B'], 'unit-narrow', 'sat', 'A, B'),
        (['A', 'B'], 'unit', 'ar_OM', 'A وB'),
        # Parts defined by the requested style take precedence.
        (['A', 'B', 'C'], 'standard-narrow', 'lo', 'A, B, C'),
        (['A', 'B'], 'unit-short', 'de', 'A, B'),
    ],
)
def test_format_list_partial_style_fallback(list, style, locale, expected):
    assert lists.format_list(list, style=style, locale=locale) == expected


def test_format_list_does_not_modify_locale_patterns():
    locale = Locale.parse('fr')
    before = {style: dict(parts) for style, parts in locale.list_patterns.items()}
    lists.format_list(['A', 'B', 'C', 'D'], style='standard-narrow', locale=locale)
    after = {style: dict(parts) for style, parts in locale.list_patterns.items()}
    assert after == before
