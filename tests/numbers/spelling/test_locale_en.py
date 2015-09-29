# -*- coding: utf-8 -*-
"""Testing the spelling of numbers for locale: en_*

:copyright: (c) 2013 by Szabolcs Blága
:license: BSD, see LICENSE in babel for more details.
"""
from __future__ import unicode_literals

import pytest

from babel import numbers
from babel.numbers._spelling import exceptions


def test_en_GB_cardinal():
    assert numbers.spell_number(0, locale='en_GB') == "zero"
    assert numbers.spell_number(1, locale='en_GB') == "one"
    assert numbers.spell_number(2, locale='en_GB') == "two"
    assert numbers.spell_number(3, locale='en_GB') == "three"
    assert numbers.spell_number('-0', locale='en_GB') == "minus zero"
    assert numbers.spell_number(123.25, locale='en_GB') == "one hundred and twenty-three point twenty-five hundredths"
    assert numbers.spell_number(-12, locale='en_GB') == "minus twelve"
    assert numbers.spell_number(23457829, locale='en_GB') == "twenty-three million four hundred and fifty-seven thousand eight hundred and twenty-nine"
    assert numbers.spell_number(1950, locale='en_GB') == "one thousand nine hundred and fifty"
    assert numbers.spell_number(2001, locale='en_GB') == "two thousand one"
    assert numbers.spell_number('1999.238', locale='en_GB') == "one thousand nine hundred and ninety-nine point two hundred and thirty-eight thousandths"
    assert numbers.spell_number(-.199923862, locale='en_GB', precision=3, state_rounded=True) == "approximately minus zero point two tenths"
    assert numbers.spell_number(-.1, locale='en_GB') == "minus zero point one tenth" # float to string conversion preserves precision


def test_en_GB_ordinal():
    assert numbers.spell_number(0, ordinal=True, locale='en_GB') == "zeroth"
    assert numbers.spell_number(1, ordinal=True, locale='en_GB') == "first"
    assert numbers.spell_number(2, ordinal=True, locale='en_GB') == "second"
    assert numbers.spell_number(3, ordinal=True, locale='en_GB') == "third"
    assert numbers.spell_number(4, ordinal=True, locale='en_GB') == "fourth"
    assert numbers.spell_number(5, ordinal=True, locale='en_GB') == "fifth"
    assert numbers.spell_number(6, ordinal=True, locale='en_GB') == "sixth"
    assert numbers.spell_number(7, ordinal=True, locale='en_GB') == "seventh"
    assert numbers.spell_number(8, ordinal=True, locale='en_GB') == "eighth"
    assert numbers.spell_number(9, ordinal=True, locale='en_GB') == "ninth"
    assert numbers.spell_number(10, ordinal=True, locale='en_GB') == "tenth"
    assert numbers.spell_number(11, ordinal=True, locale='en_GB') == "eleventh"
    assert numbers.spell_number(12, ordinal=True, locale='en_GB') == "twelfth"
    assert numbers.spell_number(13, ordinal=True, locale='en_GB') == "thirteenth"
    assert numbers.spell_number(20, ordinal=True, locale='en_GB') == "twentieth"
    assert numbers.spell_number(30, ordinal=True, locale='en_GB') == "thirtieth"
    assert numbers.spell_number(40, ordinal=True, locale='en_GB') == "fourtieth"
    assert numbers.spell_number(-12, ordinal=True, locale='en_GB') == "minus twelfth"
    assert numbers.spell_number(23457829, ordinal=True, locale='en_GB') == "twenty-three million four hundred and fifty-seven thousand eight hundred and twenty-ninth"
    assert numbers.spell_number(1950, ordinal=True, locale='en_GB') == "one thousand nine hundred and fiftieth"
    assert numbers.spell_number(2001, ordinal=True, locale='en_GB') == "two thousand first"


def test_en_GB_error():
    with pytest.raises(exceptions.TooBigToSpell) as excinfo:
        numbers.spell_number(10**24, ordinal=True, locale='en_GB')

    with pytest.raises(exceptions.PrecisionError) as excinfo:
        numbers.spell_number(.4326752, locale='en_GB', precision=4)

    with pytest.raises(exceptions.PrecisionError) as excinfo:
        numbers.spell_number(.4326752, locale='en_GB')

    with pytest.raises(exceptions.NoFractionOrdinalsAllowed) as excinfo:
        numbers.spell_number('1999.23', ordinal=True, locale='en_GB')
