# -*- coding: utf-8 -*-
"""Testing the spelling of numbers

:copyright: (c) 2013 by Szabolcs Blága
:license: BSD, see LICENSE in babel for more details.
"""
from __future__ import unicode_literals

import pytest

from babel import numbers

def test_public_interface():
    pass

def test_context_framework():
    pass

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
    assert numbers.spell_number(-.199923862, locale='en_GB') == "rounded to minus zero point two tenths"
    assert numbers.spell_number(-.1, locale='en_GB') == "minus zero point one tenth" # float to string conversion preserves precision

def test_en_GB_ordinal():
    assert numbers.spell_number(0, True, locale='en_GB') == "zeroth"
    assert numbers.spell_number(1, True, locale='en_GB') == "first"
    assert numbers.spell_number(2, True, locale='en_GB') == "second"
    assert numbers.spell_number(3, True, locale='en_GB') == "third"
    assert numbers.spell_number(4, True, locale='en_GB') == "fourth"
    assert numbers.spell_number(5, True, locale='en_GB') == "fifth"
    assert numbers.spell_number(6, True, locale='en_GB') == "sixth"
    assert numbers.spell_number(7, True, locale='en_GB') == "seventh"
    assert numbers.spell_number(8, True, locale='en_GB') == "eighth"
    assert numbers.spell_number(9, True, locale='en_GB') == "ninth"
    assert numbers.spell_number(10, True, locale='en_GB') == "tenth"
    assert numbers.spell_number(11, True, locale='en_GB') == "eleventh"
    assert numbers.spell_number(12, True, locale='en_GB') == "twelfth"
    assert numbers.spell_number(13, True, locale='en_GB') == "thirteenth"
    assert numbers.spell_number(20, True, locale='en_GB') == "twentieth"
    assert numbers.spell_number(30, True, locale='en_GB') == "thirtieth"
    assert numbers.spell_number(40, True, locale='en_GB') == "fourtieth"
    assert numbers.spell_number(123.25, True, locale='en_GB') == "cannot spell fractional numbers as ordinals :("
    assert numbers.spell_number(-12, True, locale='en_GB') == "minus twelfth"
    assert numbers.spell_number(23457829, True, locale='en_GB') == "twenty-three million four hundred and fifty-seven thousand eight hundred and twenty-ninth"
    assert numbers.spell_number(1950, True, locale='en_GB') == "one thousand nine hundred and fiftieth"
    assert numbers.spell_number(2001, True, locale='en_GB') == "two thousand first"
    assert numbers.spell_number('1999.23862', True, locale='en_GB') == "cannot spell fractional numbers as ordinals :("
    assert numbers.spell_number(-.199923862, True, locale='en_GB') == "cannot spell fractional numbers as ordinals :("



def test_hu_HU_cardinal():
    assert numbers.spell_number(0, locale='hu_HU') == "nulla"
    assert numbers.spell_number(1, locale='hu_HU') == "egy"
    assert numbers.spell_number(2, locale='hu_HU') == "kettő"
    assert numbers.spell_number(3, locale='hu_HU') == "három"
    assert numbers.spell_number('-0', locale='hu_HU') == "mínusz nulla"
    assert numbers.spell_number(123.25, locale='hu_HU') == "százhuszonhárom egész huszonöt század"
    assert numbers.spell_number(-12, locale='hu_HU') == "mínusz tizenkettő"
    assert numbers.spell_number(23457829, locale='hu_HU') == "huszonhárommillió-négyszázötvenhétezer-nyolcszázhuszonkilenc"
    assert numbers.spell_number(1950, locale='hu_HU') == "ezerkilencszázötven"
    assert numbers.spell_number(2001, locale='hu_HU') == "kétezer-egy"
    assert numbers.spell_number('1999.2386', locale='hu_HU') == "ezerkilencszázkilencvenkilenc egész kétezer-háromszáznyolcvanhat tízezred"
    assert numbers.spell_number(-.199923862, locale='hu_HU') == "kerekítve mínusz nulla egész százkilencvenkilencezer-kilencszázhuszonnégy milliomod"

def test_hu_HU_ordinal():
    assert numbers.spell_number(0, True, locale='hu_HU') == "nulladik"
    assert numbers.spell_number(1, True, locale='hu_HU') == "első"
    assert numbers.spell_number(2, True, locale='hu_HU') == "második"
    assert numbers.spell_number(3, True, locale='hu_HU') == "harmadik"
    assert numbers.spell_number(30, True, locale='hu_HU') == "harmincadik"
    assert numbers.spell_number(123.25, True, locale='hu_HU') == "százhuszonhárom egész huszonöt századodik"
    assert numbers.spell_number(-12, True, locale='hu_HU') == "mínusz tizenkettedik"
    assert numbers.spell_number(23457829, True, locale='hu_HU') == "huszonhárommillió-négyszázötvenhétezer-nyolcszázhuszonkilencedik"
    assert numbers.spell_number(1950, True, locale='hu_HU') == "ezerkilencszázötvenedik"
    assert numbers.spell_number(2001, True, locale='hu_HU') == "kétezer-egyedik"
    assert numbers.spell_number('1999.23862', True, locale='hu_HU') == "ezerkilencszázkilencvenkilenc egész huszonháromezer-nyolcszázhatvankettő százezrededik"
    assert numbers.spell_number(-.199923862, True, locale='hu_HU') == "kerekítve mínusz nulla egész százkilencvenkilencezer-kilencszázhuszonnégy milliomododik"
