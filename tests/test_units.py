import pytest

from babel.units import format_unit


# New units in CLDR 46
@pytest.mark.parametrize(('unit', 'count', 'expected'), [
    ('speed-light-speed', 1, '1 světlo'),
    ('speed-light-speed', 2, '2 světla'),
    ('speed-light-speed', 5, '5 světel'),
    ('concentr-portion-per-1e9', 1, '1 částice na miliardu'),
    ('concentr-portion-per-1e9', 2, '2 částice na miliardu'),
    ('concentr-portion-per-1e9', 5, '5 částic na miliardu'),
    ('duration-night', 1, '1 noc'),
    ('duration-night', 2, '2 noci'),
    ('duration-night', 5, '5 nocí'),
])
def test_new_cldr46_units(unit, count, expected):
    assert format_unit(count, unit, locale='cs_CZ') == expected


@pytest.mark.parametrize('count, unit, locale, length, expected', [
    (1, 'duration-month', 'et', 'long', '1 kuu'),
    (1, 'duration-minute', 'et', 'narrow', '1 min'),
    (2, 'duration-minute', 'et', 'narrow', '2 min'),
    (2, 'digital-byte', 'et', 'long', '2 baiti'),
    (1, 'duration-day', 'it', 'long', '1 giorno'),
    (1, 'duration-day', 'it', 'short', '1 giorno'),
])
def test_issue_1217(count, unit, locale, length, expected):
    assert format_unit(count, unit, length, locale=locale) == expected
