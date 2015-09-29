# -*- coding: utf-8 -*-
"""Number spelling - exceptions

:copyright: (c) 2013 by Szabolcs Blága
:license: BSD, see LICENSE in babel for more details.
"""


class SpellerNotFound(Exception):
    """There is no speller for the given locale"""


class PreprocessorClassError(Exception):
    """Preprocessors should inherit from PreprocessorBase"""


class TooBigToSpell(Exception):
    """Overflow for the speller"""


class PrecisionError(Exception):
    """Errors regarding precision and rounding"""


class NoFractionOrdinalsAllowed(Exception):
    """
    Raised if the user tries to spell a fractional
    number as ordinal
    """
