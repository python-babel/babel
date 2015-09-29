# -*- coding: utf-8 -*-
"""Spell out numbers

CLDR data is not used at the moment, but it could be integrated
later. As far as I know the data from babel/cldr/common/rbnf/
is not used at the moment (by babel) and it would not be sufficient
anyway (at least for Hungarian), see:
http://cldr.unicode.org/

After the CLDR data incorporated into this module the whole
interface could change. However to design a general
spelling-rule-markup and implement a general speller function
for every locale based on the markup is a serious challange.
Any contribution is very welcome!

Using decorators, because this way all relevant locale specific
code displayed together with the logic of the single function
that implements spelling.

All three context object are helper for the locale specific
spellers. They help to write clean code for the spelling
logic. Although they are not efficient in many ways they help
to maintain the readability and therefore the maintainability of
the code.

TODO:
    add support for scientific spelling centrally (CLDR support necessary)
    add support for non-decimal number systems

:copyright: (c) 2013 by Szabolcs Blága
:license: BSD, see LICENSE in babel for more details.

The locale specific copyright messages should be placed in the locale
specific function's docstring.
"""
from __future__ import division, print_function, unicode_literals

import sys, os, re, decimal

from .exceptions import *
from .utils import *

dec = decimal.Decimal

_registry = {}


def load():
    if not _registry:
        curr_dir = os.path.abspath(os.path.dirname(__file__))
        for root, dirs, files in os.walk(curr_dir):
            for f in files:
                if f.startswith('locale') and f.endswith('.py'):
                    # TODO: importlib is better but supported from 2.7 only
                    __import__('babel.numbers._spelling.'+f[:-3])


def decorate_spell_function(locale, **kwargs):
    """
    This is the parameterized decorator for the spellers

    It accepts various parameters to be able to simplify
    the locale specific speller function writing.

    The writer of the locale specific speller function
    could also supply a custom preprocessor that inherits
    from ``PreprocessorBase``. The custom preprocessor
    will receive all keyword argument upon instantiation.
    """
    def decorator(func):
        """
        Add the speller function to registry
        """
        # add preprocessor to function if not empty
        proc_class = kwargs.pop('preprocessor', DefaultPreprocessor)

        # check preprocessor
        if issubclass(proc_class, PreprocessorBase):
            func._preprocessor = proc_class(**kwargs)
        else:
            raise PreprocessorClassError

        # check for override issue warning
        _registry[locale] = func
        # prevent the module functions to be called directly -- return `None`
        return None

    return decorator

# shortcut for cleaner code in the locale specific spell function definitions
spell = decorate_spell_function


def get_spell_function(locale):
    """
    Search ``_registry`` for the spelling function

    Negotiation is called in ``babel.numbers.spell_number``
    """
    if locale in _registry:
        return _registry[locale]
    else:
        raise SpellerNotFound("There is no appropriate number speller function for the given locale")


class NumberSpeller(object):
    """
    This class is somewhat redundant, but it is there
    to comply with the general structure of the
    ``babel.numbers`` module
    """

    def __init__(self, locale):
        """
        Search for digit function in the module based on data
        """
        self._speller = get_spell_function(locale)

    def apply(self, number, **kwargs):
        """
        Apply the speller
        """
        # generate the number if a preprocessor exists
        if hasattr(self._speller, '_preprocessor'):
            # errors only thrown by the preprocessor
            number, kwargs = self._speller._preprocessor(number, kwargs)

        # call transform
        self._speller(number, **kwargs)

        # return the result (construct it recursively)
        return '{0}'.format(number)


class PreprocessorBase(object):
    """
    A skeleton class for all other processors
    """
    def __init__(self, **kwargs):
        """Default function accepting keyword arguments"""

    def process(self, number, kwargs):
        """
        Processes arguments from ``babel.numbers.spell_number``
        and return remaining ones for the actual locale
        specific speller

        Process number based on arguments and internal state
        """
        return number, kwargs

    def __call__(self, number, kwargs):
        """Do processing with the shortcut syntax"""
        return self.process(number, kwargs)


class DefaultPreprocessor(PreprocessorBase):
    """The default preprocessor for spelling numbers

    Various complecated grouping mechanism could be implemented
    with different  preprocessor classes.

    If no preprocessor class is provided for the decorator of a speller
    function then the default preprocessor is used.
    """
    def __init__(self, integer_grouping=3, fraction_grouping=3,
            maximum_precision=3, maximum_digits=15,
            scientific_threshold=None,
            allow_fraction_ordinals=False,
            ):
        """
        Define acceptable parameters

        :param integer_grouping: how to group the integer part
        :param fraction_grouping: how to group the fraction part
        :param maximum_precision: what is the maximum number of
            fractional digits that the speller could handle
        :param maximum_digits: what is the maximum number of
            digits(!) that the speller could handle defaults
            to 999 trillion, etc. as maximum
        :param scientific_threshold: what is the maximum number
            of digits above which the speller use scientific
            notation, e.g. 1.23 x 10^23, not used by default,
            and maximum precision applies here as well.
        :param allow_fraction_ordinals: allow the spelling of
            fractional numbers as ordinals (there is no actual
            use case for that but in some languages it is
            technically possible)
        """
        self.integer_grouping = integer_grouping
        self.fraction_grouping = fraction_grouping
        self.maximum_precision = maximum_precision
        self.maximum_digits = maximum_digits

    def process(self, number, kwargs):
        """
        Processes arguments from ``babel.numbers.spell_number``
        and return remaining ones for the actual locale
        specific speller

        Process number and return context
        """
        # if precision is set by the caller, silently round
        silent_round = True if 'precision' in kwargs else False

        prec = kwargs.pop('precision', self.maximum_precision)

        if prec > self.maximum_precision:
            raise PrecisionError('Maximum allowed precision is %s digits' % self.maximum_precision)

        ordinal = kwargs.pop('ordinal', False)

        def reverse_group_by(digits, group_size):
            """This is a basic implementation of grouping."""
            digits.reverse()
            groups = []
            while len(digits) > 0:
                groups.append(digits[:group_size])
                digits = digits[group_size:]
            return groups

        with decimal.localcontext() as ctx:
            ctx.prec = 99 # it should be minimum the supported digits
            # this is supposed to be the only place for unintensional precision loss
            try:
                number = dec(str(number)) # to support Python 2.6
            except decimal.InvalidOperation:
                raise ValueError('Not a valid number.')
            n = number.quantize(dec(10) ** -prec)
            # get rid of the exponent or trailing zeros in one step
            n = n.quantize(dec(1)) if n == n.to_integral() else n.normalize()

        rounded = True if n != number else False

        if rounded and not silent_round:
            raise PrecisionError('Needed rounding, set precision less or equal %s' % self.maximum_precision)

        # split number parts
        m = re.match(r"(-)?(\d+)\.?(\d+)?", str(n))
        sign, integer, fraction = m.groups()

        # check for maximum
        if len(integer) > self.maximum_digits:
            raise TooBigToSpell('Maximum %s digits allowed' % self.maximum_digits)

        integer = reverse_group_by([int(i) for i in integer], self.integer_grouping)

        if fraction and fraction != '0':
            if ordinal:
                raise NoFractionOrdinalsAllowed
            fraction = reverse_group_by([int(i) for i in fraction], self.fraction_grouping)
        else:
            fraction = []

        return NumberContext(n, integer, fraction, rounded, sign=='-', ordinal), kwargs


class ContextBase(object):
    """
    Basic functionality for context classes
    """
    def __init__(self):
        self.prefix = ""
        self.suffix = ""
        self.separator = ""
        self.string = None
        self.value = None

    def __iter__(self):
        """
        Should be overridden
        """
        return []

    def __unicode__(self):
        """
        Based on the overrode iterators `self.__iter__`
        """
        s = self.string if self.string is not None else self.separator.join(reversed(['{0}'.format(e) for e in self]))

        return self.prefix + s + self.suffix

    def __str__(self):
        """
        This is necessary to support both Python 2 and 3
        """
        if sys.version < '3':
            return unicode(self).encode('utf-8')
        else:
            return self.__unicode__()


class NumberContext(ContextBase):
    """
    Represents a number and its internal structure.

    The number is separated into integer and fraction parts
    and the fraction part is also rounded if necessary.
    """
    def __init__(self, value, integer, fraction, rounded, negative, ordinal):
        super(NumberContext, self).__init__()
        self.value = value
        self.integer = SideContext(integer, self)
        self.fraction = SideContext(fraction, self)
        self.rounded = rounded
        self.negative = negative
        self.ordinal = ordinal

    def __iter__(self):
        yield self.fraction
        yield self.integer

    def __len__(self):
        return len(self.integer) + len(self.fraction)

    @property
    def last_nonzero(self):
        """
        The first non-zero digit from the right
        """
        for side in self:
            for group in side:
                for digit in group:
                    if digit.value != 0:
                        return digit


class SideContext(ContextBase):
    """
    Represent one side of the decimal point
    """
    def __init__(self, groups, number):
        super(SideContext, self).__init__()
        self.number = number
        self.groups = tuple(GroupContext(digits, number, self, i) for i, digits in enumerate(groups))
        # calculate the value of the side the hard way (might use number.value instead)
        e, s = 0, 0
        for g in self.groups:
            s += g.value*10**e
            e += len(g)
        self.value = s

    def __iter__(self):
        for group in self.groups:
            yield group

    def __len__(self):
        return sum(len(g) for g in self)


class GroupContext(ContextBase):
    """
    Represent a group of digits inside a number

    Digits inside the group are indexed from the right.
    """
    def __init__(self, digits, number, side, index):
        super(GroupContext, self).__init__()
        self.digits = tuple(DigitContext(v, number, side, self, i) for i,v in enumerate(digits))
        self.number = number
        self.side = side
        self.index = index
        self.value = sum(d.value*dec(10)**e for e,d in enumerate(self.digits)) # might use int

    def __len__(self):
        return len(self.digits)

    def __iter__(self):
        for digit in self.digits:
            yield digit


class DigitContext(ContextBase):
    """
    Represent one digit of a number and its context
    """
    def __init__(self, value, number, side, group, index):
        super(DigitContext, self).__init__()
        self.value = value
        self.number = number
        self.side = side
        self.group = group
        self.index = index
        self.string = ''

    def __iter__(self):
        """
        Not so nice, but this way it could also inherit from ContextBase
        """
        yield self.string


__all__ = ['spell']  # this is the only public element
