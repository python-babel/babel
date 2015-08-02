# -*- coding: utf-8 -*-
"""Testing the spelling of numbers for locale: hu_*

:copyright: (c) 2013 by Szabolcs Blága
:license: BSD, see LICENSE in babel for more details.
"""
from __future__ import unicode_literals

import pytest

from babel import numbers
from babel.numbers._spelling import exceptions


def test_hu_HU_cardinal():
    assert numbers.spell_number(0, locale='hu_HU') == "nulla"
    assert numbers.spell_number(1, locale='hu_HU') == "egy"
    assert numbers.spell_number(2, locale='hu_HU') == "kettő"
    assert numbers.spell_number(3, locale='hu_HU') == "három"
    assert numbers.spell_number(10, locale='hu_HU') == "tíz"
    assert numbers.spell_number(20, locale='hu_HU') == "húsz"
    assert numbers.spell_number('-0', locale='hu_HU') == "mínusz nulla"
    assert numbers.spell_number(123.25, locale='hu_HU') == "százhuszonhárom egész huszonöt század"
    assert numbers.spell_number(-12, locale='hu_HU') == "mínusz tizenkettő"
    assert numbers.spell_number(23457829, locale='hu_HU') == "huszonhárommillió-négyszázötvenhétezer-nyolcszázhuszonkilenc"
    assert numbers.spell_number(1950, locale='hu_HU') == "ezerkilencszázötven"
    assert numbers.spell_number(2001, locale='hu_HU') == "kétezer-egy"
    assert numbers.spell_number('1999.2386', locale='hu_HU') == "ezerkilencszázkilencvenkilenc egész kétezer-háromszáznyolcvanhat tízezred"
    assert numbers.spell_number(-.199923862, locale='hu_HU', precision=6) == "mínusz nulla egész százkilencvenkilencezer-kilencszázhuszonnégy milliomod"
    assert numbers.spell_number(-.199923862, locale='hu_HU', precision=4, state_rounded=True) == "kerekítve mínusz nulla egész ezerkilencszázkilencvenkilenc tízezred"
    assert numbers.spell_number(.4326752, locale='hu_HU', precision=2) == "nulla egész negyvenhárom század"


def test_hu_HU_ordinal():
    assert numbers.spell_number(0, ordinal=True, locale='hu_HU') == "nulladik"
    assert numbers.spell_number(1, ordinal=True, locale='hu_HU') == "első"
    assert numbers.spell_number(2, ordinal=True, locale='hu_HU') == "második"
    assert numbers.spell_number(3, ordinal=True, locale='hu_HU') == "harmadik"
    assert numbers.spell_number(10, ordinal=True, locale='hu_HU') == "tizedik"
    assert numbers.spell_number(20, ordinal=True, locale='hu_HU') == "huszadik"
    assert numbers.spell_number(30, ordinal=True, locale='hu_HU') == "harmincadik"
    assert numbers.spell_number(-12, ordinal=True, locale='hu_HU') == "mínusz tizenkettedik"
    assert numbers.spell_number(23457829, ordinal=True, locale='hu_HU') == "huszonhárommillió-négyszázötvenhétezer-nyolcszázhuszonkilencedik"
    assert numbers.spell_number(1100, ordinal=True, locale='hu_HU') == "ezerszázadik"
    assert numbers.spell_number(1950, ordinal=True, locale='hu_HU') == "ezerkilencszázötvenedik"
    assert numbers.spell_number(2001, ordinal=True, locale='hu_HU') == "kétezer-egyedik"


def test_hu_HU_error():
    with pytest.raises(exceptions.TooBigToSpell) as excinfo:
        numbers.spell_number(10**66, ordinal=True, locale='hu_HU')

    with pytest.raises(exceptions.PrecisionError) as excinfo:
        numbers.spell_number(.4326752, locale='hu_HU', precision=7)

    with pytest.raises(exceptions.PrecisionError) as excinfo:
        numbers.spell_number(.4326752, locale='hu_HU')

    with pytest.raises(exceptions.NoFractionOrdinalsAllowed) as excinfo:
        numbers.spell_number('1999.23862', ordinal=True, locale='hu_HU')
