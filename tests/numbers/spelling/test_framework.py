# -*- coding: utf-8 -*-
"""Testing the spelling of numbers

:copyright: (c) 2013 by Szabolcs Blága
:license: BSD, see LICENSE in babel for more details.
"""
from __future__ import unicode_literals

import pytest

from babel import numbers
from babel.numbers import _spelling as numspell
from babel.numbers._spelling import exceptions


def test_context_framework():
    pp = numspell.DefaultPreprocessor(maximum_precision=6)
    context, extra_kwargs = pp(2222.22222, {'precision':5, 'extra':23})

    assert extra_kwargs == {'extra':23}

    for side in context:
        assert isinstance(side, numspell.SideContext)
        for group in side:
            assert isinstance(group, numspell.GroupContext)
            for digit in group:
                assert isinstance(digit, numspell.DigitContext)
                assert digit.value == 2


def test_errors():
    with pytest.raises(exceptions.SpellerNotFound) as excinfo:
        numbers.spell_number(23, locale='zz_QQ')

    with pytest.raises(exceptions.PreprocessorClassError) as excinfo:
        @numspell.spell('hu_HU', preprocessor=object)
        def anon():
            pass

    with pytest.raises(ValueError) as excinfo:
        numbers.spell_number('kisnyúl', locale='hu_HU')
