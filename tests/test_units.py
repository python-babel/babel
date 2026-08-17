import pytest

from babel.units import format_unit, get_unit_name


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
    'count, unit, locale, length, expected',
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


def test_deprecated_unit_ids():
    for id in ("concentr-permillion", "concentr-portion", "concentr-portion-per-1e9"):
        with pytest.warns(DeprecationWarning, match=id):
            format_unit(1, id, locale='en')


@pytest.mark.parametrize(
    'count, unit, locale, length, expected',
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
