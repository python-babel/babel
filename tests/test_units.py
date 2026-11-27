from functools import partial

import pytest

from babel.units import (
    _DEPRECATED_UNIT_IDS,
    UnknownUnitError,
    _find_compound_unit,
    _find_unit_pattern,
    format_compound_unit,
    format_unit,
    get_unit_name,
)


# New units in CLDR 46
@pytest.mark.parametrize(
    ('unit', 'count', 'expected'),
    [
        ('speed-light-speed', 1, '1 světlo'),
        ('speed-light-speed', 2, '2 světla'),
        ('speed-light-speed', 5, '5 světel'),
        ('concentr-part-per-1e9', 1, '1 částice na miliardu'),
        ('concentr-part-per-1e9', 2, '2 částice na miliardu'),
        ('concentr-part-per-1e9', 5, '5 částic na miliardu'),
        ('duration-night', 1, '1 noc'),
        ('duration-night', 2, '2 noci'),
        ('duration-night', 5, '5 nocí'),
    ],
)
def test_new_cldr46_units(unit, count, expected):
    assert format_unit(count, unit, locale='cs_CZ') == expected


@pytest.mark.parametrize(
    ('count', 'unit', 'locale', 'length', 'expected'),
    [
        (1, 'duration-month', 'et', 'long', '1 kuu'),
        (1, 'duration-minute', 'et', 'narrow', '1 min'),
        (2, 'duration-minute', 'et', 'narrow', '2 min'),
        (2, 'digital-byte', 'et', 'long', '2 baiti'),
        (1, 'duration-day', 'it', 'long', '1 giorno'),
        (1, 'duration-day', 'it', 'short', '1 giorno'),
    ],
)
def test_issue_1217(count, unit, locale, length, expected):
    assert format_unit(count, unit, length, locale=locale) == expected


@pytest.mark.parametrize(('unit_id', 'replacement'), _DEPRECATED_UNIT_IDS.items())
def test_deprecated_unit_ids(unit_id, replacement):
    for func in (partial(format_unit, 1), get_unit_name):
        with pytest.warns(DeprecationWarning, match=unit_id) as record:
            result = func(unit_id, locale='en')
        assert len(record) == 1
        assert result == func(replacement, locale='en')


@pytest.mark.parametrize(
    ('count', 'unit', 'locale', 'length', 'expected'),
    [
        # Root aliases `duration-*-person` to `duration-*`;
        # no locale defines the person variants at all.
        # These resolve length-preservingly (person long -> base long),
        # matching ICU's `-person`-stripping behavior
        # (see `getMeasureData` in https://github.com/unicode-org/icu/blob/main/icu4c/source/i18n/number_longnames.cpp
        # and https://unicode-org.atlassian.net/browse/ICU-20400).
        # This deliberately bends literal TR35 alias resolution.
        # See `parse_unit_patterns` in `scripts/import_cldr.py` for the full story.
        (2, 'duration-day-person', 'af', 'long', '2 dae'),
        (3, 'duration-day-person', 'fi', 'long', '3 päivää'),
        (3, 'duration-day-person', 'fi', 'short', '3 pv'),
        (3, 'duration-day-person', 'fi', 'narrow', '3pv'),
        (3, 'duration-year-person', 'fi', 'long', '3 vuotta'),
        # `fi` defines `energy-foodcalorie` at long and narrow but not short;
        # the root alias fills short in from `energy-kilocalorie`.
        (3, 'energy-foodcalorie', 'fi', 'short', '3 kcal'),
        # `fi` defines `graphics-dot` at short and narrow but not long;
        # the root alias fills long in from short.
        (3, 'graphics-dot', 'fi', 'long', '3 pistettä'),
        # `cs` defines `graphics-dot` itself but not its short forms;
        # the root aliases short to `graphics-pixel` short rather than the display name.
        (3, 'graphics-dot', 'cs', 'short', '3 px'),
    ],
)
def test_issue_1076_unit_aliases(count, unit, locale, length, expected):
    assert format_unit(count, unit, length, locale=locale) == expected


def test_issue_1076_unit_name_length_aliases():
    # Finnish defines no narrow display name for days; root aliases narrow to
    # short. This used to return None.
    assert get_unit_name('duration-day', length='narrow', locale='fi') == 'pv'
    # The person variant resolves length-preservingly to `duration-day`.
    assert get_unit_name('duration-day-person', length='long', locale='fi') == 'päivät'
    assert get_unit_name('duration-day-person', length='short', locale='fi') == 'pv'


@pytest.mark.parametrize('locale', ['en', 'fi', 'fr'])
@pytest.mark.parametrize('length', ['long', 'short', 'narrow'])
@pytest.mark.parametrize('value', [1, 5])
@pytest.mark.parametrize(
    ('numerator_unit', 'denominator_unit'),
    [('meter', 'hour'), ('length-meter', 'duration-hour')],
)
def test_compound_unit_does_not_replace_meter_with_kilometer(
    locale, length, value, numerator_unit, denominator_unit,
):
    # A preformatted numerator with no unit bypasses predefined compound lookup.
    numerator = format_unit(value, numerator_unit, locale=locale, length=length)
    expected = format_compound_unit(
        numerator, denominator_unit=denominator_unit, locale=locale, length=length,
    )
    assert format_compound_unit(
        value, numerator_unit, denominator_unit=denominator_unit, locale=locale, length=length,
    ) == expected


@pytest.mark.parametrize('locale', ['en', 'fi', 'fr'])
@pytest.mark.parametrize('length', ['long', 'short', 'narrow'])
@pytest.mark.parametrize('value', [1, 5])
def test_predefined_kilometer_per_hour_is_preserved(locale, length, value):
    assert _find_compound_unit('kilometer', 'hour', locale=locale) == 'speed-kilometer-per-hour'
    assert format_compound_unit(
        value, 'kilometer', denominator_unit='hour', locale=locale, length=length,
    ) == format_unit(value, 'speed-kilometer-per-hour', locale=locale, length=length)


@pytest.mark.parametrize(
    ('unit', 'expected'),
    [
        ('meter', 'length-meter'),
        ('length-meter', 'length-meter'),
        ('kilometer', 'length-kilometer'),
        ('meter-per-hour', None),
        ('kilometer-per-hour', 'speed-kilometer-per-hour'),
        ('radian', 'angle-radian'),
        ('adian', None),
        ('', None),
    ],
)
def test_unit_lookup_requires_a_name_boundary(unit, expected):
    assert _find_unit_pattern(unit, locale='en') == expected


@pytest.mark.parametrize('locale', ['en', 'fi', 'fr'])
@pytest.mark.parametrize('length', ['long', 'short', 'narrow'])
@pytest.mark.parametrize('numerator', [5, 'five widgets'])
@pytest.mark.parametrize('denominator', [1, 2])
def test_compound_unit_reports_the_unknown_denominator(locale, length, numerator, denominator):
    with pytest.raises(UnknownUnitError) as error:
        format_compound_unit(
            numerator, 'meter', denominator_value=denominator, denominator_unit='not-a-unit',
            locale=locale, length=length,
        )
    assert str(error.value) == f'not-a-unit is not a known unit in {locale}'


@pytest.mark.parametrize('denominator_unit', [None, 'not-a-unit', 'hour'])
def test_preformatted_compound_denominator_ignores_its_unit(denominator_unit):
    assert format_compound_unit(
        5, 'meter', denominator_value='widget', denominator_unit=denominator_unit, locale='en',
    ) == '5 meters per widget'


def test_compound_unit_without_a_denominator_unit():
    assert format_compound_unit(5, 'meter', locale='en') == '5 meters per 1'
