import pytest

from babel import lists, units


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


@pytest.mark.parametrize(
    ('items', 'style', 'expected'),
    [
        (['España', 'Italia'], 'standard', 'España e Italia'),
        (['España', 'Suiza', 'Italia'], 'standard', 'España, Suiza e Italia'),
        (['tos', 'HIPO'], 'standard-short', 'tos e HIPO'),
        (['agua', 'hielo'], 'standard', 'agua y hielo'),
        (['mañana', 'hoy'], 'or', 'mañana u hoy'),
        (['lunes', 'martes', 'HOY'], 'or-short', 'lunes, martes u HOY'),
        (['6', '8'], 'or', '6 u 8'),
        (['10', '11'], 'or', '10 u 11'),
        (['10 mil', '11 mil'], 'or', '10 mil u 11 mil'),
        (['10', '110'], 'or', '10 o 110'),
    ],
)
def test_format_spanish_list(items, style, expected):
    assert lists.format_list(items, style=style, locale='es_ES') == expected


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
