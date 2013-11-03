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
