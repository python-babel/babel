# -*- coding: utf-8 -*-
"""Spell out numbers

This could be added as a submodul to numbers, but I did not
want to interfere with current modul structure.

CLDR data is not used at the moment, but it could be integrated
later. As far as I know the data from babel/cldr/common/rbnf/
is not used at the moment (by babel) and it would not be sufficient
anyway (at least for Hungarian), see:
http://cldr.unicode.org/

Many structures I tried (including a singleton class inheritance
hierarchy) but finally I decided with the solution using decorators
because this way all relevant locale specific code displayed
together with the logic of the single function that implements
spelling.

After the CLDR data incorporated into this module the whole
interface could change. However to design a general
spelling-rule-markup and implement a general speller function
for every locale based on the markup is a serious challange.
Any contribution is very welcome!

All three context object are helper for the locale specific
spellers. They help to write clean code for the spelling
logic. Although they are not efficient in many ways they help
to maintain the readability and therefore the maintainability of
the code.

:copyright: (c) 2013 by Szabolcs Blága
:license: BSD, see LICENSE in babel for more details.

The locale specific copyright messages should be placed in the locale
specific function's docstring.
"""
from __future__ import division, print_function, unicode_literals

import re, decimal, sys

dec = decimal.Decimal


class SpellerNotFound(Exception):
    """There is no speller for the given locale"""

    
class TooBigToSpell(Exception):
    """Overflow for the speller

    Not used at the moment the returned string should
    reflect the fact it is not spelled in a way that it could
    fit into a place of a spelled out number.

    Maybe a module level setting could be used to switch to
    throwing exception on overflow.
    """


class NumberSpeller(object):
    registry = {}

    def __init__(self, locale):
        """
        Search for digit function in the module based on data
        """
        self._speller = self.__class__.get_spell_function(locale)

    def apply(self, number, ordinal=False, **kwargs):
        """
        Apply the speller
        """
        # generate the number if a ContextMaker exists
        if hasattr(self._speller, '_context_maker'):
            number = self._speller._context_maker(number)
    
        # call transform
        self._speller(number, ordinal)

        # return the result (construct it recursively)
        return '{0}'.format(number)
        
    @classmethod
    def get_spell_function(cls, locale):
        """
        Search `cls.registry` for the spelling function

        NEgotiation is called in `babel.numbers.spell_number`
        """
        if locale in cls.registry:
            return cls.registry[locale]
        else:
            raise SpellerNotFound("There is no appropriate number speller function for the given locale")


    @classmethod
    def decorate_spell_function(cls, locale, context_maker=None):
        """
        This is the parameterized decorator for the spellers
        """
        def decorator(func):
            """
            Add the speller function to registry
            """
            # add contextmaker to function if not empty
            if context_maker is not None:
                func._context_maker = context_maker

            # check for override issue warning
            cls.registry[locale] = func
            # pervent the module functions to be called directly -- return `None`
            return None

        return decorator


# shortcut for cleaner code in the locale specific spell function definitions
spell = NumberSpeller.decorate_spell_function


class ContextMaker(object):
    """
    Various complecated grouping mechanism could be implemented
    with different `ContextMaker` classes.

    If no `ContextMaker` is provided for the decorator of a speller
    function then the speller is called with the raw number.
    """
    def __init__(self, integer_grouping=3, fraction_grouping=3, precision=6):
        """
        The defaults are based on the Hungarian speller but specified
        there explicitly.
        """
        self.integer_grouping = integer_grouping
        self.fraction_grouping = fraction_grouping
        self.precision = precision

    def __call__(self, number):
        """
        Process number and return context

        This is a basic implementation of grouping.
        """
        def reverse_group_by(digits, group_size):
            digits.reverse()
            groups = []
            while len(digits) > 0:
                groups.append(digits[:group_size])
                digits = digits[group_size:]
            return groups

        decimal.getcontext().prec = 99 # could be more or less but it should be as many as the supported digits
        # this is supposed to be the only place for unintensional precision loss
        number = dec(str(number)) # to support Python 2.6
        # print('raw', number)
        n = number.quantize(dec(10) ** -self.precision)
        # get rid of the exponent or trailing zeros in one step
        n = n.quantize(dec(1)) if n == n.to_integral() else n.normalize()
        rounded = True if n != number else False

        # split number parts
        m = re.match(r"(-)?(\d+)\.?(\d+)?", str(n))
        
        if m:
            sign, integer, fraction = m.groups()
            integer = reverse_group_by([int(i) for i in integer], self.integer_grouping)
            if fraction and fraction != '0':
                fraction = reverse_group_by([int(i) for i in fraction], self.fraction_grouping)
            else:
                fraction = []
        else:
            raise ValueError('Not a valid number.')

        return NumberContext(n, integer, fraction, rounded, sign=='-')


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
    def __init__(self, value, integer, fraction, rounded, negative):
        ContextBase.__init__(self)
        self.value = value
        self.integer = SideContext(integer, self)
        self.fraction = SideContext(fraction, self)
        self.rounded = rounded
        self.negative = negative
        
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
        ContextBase.__init__(self)
        self.number = number
        self.groups = tuple(GroupContext(digits, number, self, i) for i, digits in enumerate(groups))
        # callculate the value of the side the hard way (might use number.value instead)
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
        ContextBase.__init__(self)
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
        ContextBase.__init__(self)
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


#####################################
# locale specific speller functions #
#####################################

def prod(*strings):
    """generate chartesian products of strings after splitting them"""
    import itertools
    return [''.join(r) for r in itertools.product(*[s.split(' ') for s in strings])]


@spell('en', ContextMaker(3, 3, 3))
def en_GB(number, ordinal):
    """
    Draft English speller based on: http://en.wikipedia.org/wiki/English_numerals

    :copyright: (c) 2014 by Szabolcs Blága
    :license: BSD, see LICENSE in babel for more details.
    """
    # name-parts for the short scale
    scale_base = 'm b tr quad quint sext'
    scale = ['', 'thousand'] + prod(scale_base, 'illion')
    
    if ordinal and number.fraction:
        number.string = "cannot spell fractional numbers as ordinals :("
        return

    # avoid using decimal by comparing number of digits
    if len(number.integer) > len(scale)*3:
        number.string = 'too big to spell :)'
        return

    if len(number.integer) < 2 and number.integer.value == 0:
        number.integer.string = 'zero'

    # initialization running once
    if number.fraction:
        number.separator = ' point '

    if number.rounded:
        number.prefix = 'rounded to '
    
    if number.negative:
        number.prefix += 'minus '

    names_base = ' one two three four five six seven eight nine'.split(' ')
    teens = ' eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen ninteen'.split(' ')
    teens_ord = ' eleventh twelfth thirteenth fourteenth fifteenth sixteenth seventeenth eighteenth ninteenth'.split(' ')

    names = (
        names_base,
        ' ten twenty thirty fourty fifty sixty seventy eighty ninety'.split(' '),
        names_base,
    )
    names_ord = (
        ' first second third fourth fifth sixth seventh eighth ninth'.split(' '),
        ' tenth twentieth thirtieth fourtieth fiftieth sixtieth seventieth eightieth ninetieth '.split(' '),
    )

    # set general ordinal suffix
    if ordinal:
        number.suffix = 'th'

    # spell
    for side in number:

        side.separator = ' '

        for group in side:
            # employ the scale
            if group.index > 0:
                group.suffix = ' ' + scale[group.index]

            for digit in group:
                # get default namings
                digit.string = names[digit.index][digit.value]

                # add teens
                teen = group.value > 10 and group.digits[1].value == 1
                if digit.index == 0:
                    if teen:
                        digit.string = teens[digit.value]

                if digit.index == 1:
                    if teen:
                        digit.string = ''
                    elif digit.value > 0 and group.digits[0].value > 0:
                        digit.suffix = '-'

                # adding hundred suffix
                if digit.index == 2 and digit.value > 0:
                    digit.suffix = ' hundred'
                    if group.digits[0].value > 0 or group.digits[1].value > 0:
                        digit.suffix += ' and '

                # run specialities for ordinals at last non-zero digit
                if ordinal and side == number.integer and digit == number.last_nonzero:

                    # add normal ordinals
                    if digit.index < 2:
                        digit.string = names_ord[digit.index][digit.value]
                        number.suffix = ''

                    if digit.index == 0:
                        if teen:
                            digit.string = teens_ord[digit.value]

    fra_scale = ' ten hundred thousand'.split(' ')
    # add suffix on fraction side
    if number.fraction.value > 0:
        number.fraction.suffix = ' ' + fra_scale[len(number.fraction)] + 'th'

        if number.fraction.value > 1:
            number.fraction.suffix += 's'


@spell('hu_HU', ContextMaker(3, 3, 6))
def hu_HU(number, ordinal):
    """
    Based on the official language guideline of Hungary:
    http://hu.wikisource.org/wiki/A_magyar_helyes%C3%ADr%C3%A1s_szab%C3%A1lyai/Egy%C3%A9b_tudnival%C3%B3k#288.
    http://hu.wikipedia.org/wiki/Wikip%C3%A9dia:Helyes%C3%ADr%C3%A1s/A_sz%C3%A1mok_%C3%ADr%C3%A1sa

    Names of the powers of ten: http://hu.wikipedia.org/wiki/T%C3%ADz_hatv%C3%A1nyai

    For doublechecking: http://helyesiras.mta.hu

    Currently supports: +/- 10^66 - 10^-7 

    :copyright: (c) 2013 by Szabolcs Blága
    :license: BSD, see LICENSE in babel for more details.
    """

    # name-parts for the Hungarian long scale (every 10^6 has an unique name)
    scale_base = 'm b tr kvadr kvint szext szept okt non dec'
    scale = ['', 'ezer'] + prod(scale_base, 'illió illiárd')
    scale_ord = ['', 'ezre'] + prod(scale_base, 'illiomo illiárdo')
    # alternate spelling (millió, ezermillió, billió, ezerbillió, stb.)
    
    # avoid using decimal by comparing number of digits
    if len(number.integer) > len(scale)*3:
        number.string = 'leírhatatlanul ' + ('sokadik' if ordinal else 'sok') + ' :)'
        return

    if len(number.integer) < 2 and number.integer.value == 0:
        number.integer.string = 'nulla'

    # initialization running once
    if number.fraction:
        number.separator = ' egész '

    if number.rounded:
        number.prefix = 'kerekítve '
    
    if number.negative:
        number.prefix += 'mínusz '


    names = (
        ' egy két három négy öt hat hét nyolc kilenc'.split(' '),
        ' tizen huszon harminc negyven ötven hatvan hetven nyolcvan kilencven'.split(' '),
        '  két három négy öt hat hét nyolc kilenc'.split(' '),
    )
    names_ord = (
        ' egye kette harma negye ötö hato hete nyolca kilence'.split(' '),
        ' tize husza harminca negyvene ötvene hatvana hetvene nyolcvana kilencvene'.split(' '),
    )

    # set general ordinal suffix
    if ordinal:
        number.suffix = 'dik'

    # spell
    for side in number:

        for group in side:
            # employ the scale
            group.suffix = scale[group.index]

            for digit in group:
                # get default namings
                digit.string = names[digit.index][digit.value]

                # special: kettő at the end (also on fraction side but there it could be `két` as well)
                if group.index == 0 and digit.index == 0 and digit.value == 2:
                    digit.string = 'kettő'

                # different spelling for 10 and 20
                if digit.index == 1 and group.digits[0].value == 0 and 0 < digit.value < 3:
                    digit.string = ' tíz húsz'.split(' ')[digit.value]

                # adding `száz` suffix
                if digit.index == 2 and digit.value > 0:
                    digit.suffix = 'száz'

                # run specialities for ordinals at last non-zero digit
                if ordinal and side == number.integer and digit == number.last_nonzero:

                    # add extra character for 100
                    if digit.index == 2:
                        digit.suffix += 'a'
                    # ordinal naming lookup for all other cases
                    else:
                        digit.string = names_ord[digit.index][digit.value]

                    # special spelling for first (and suffix cancelled)
                    if number.integer.value == 1:
                        digit.string = 'első'
                        number.suffix = ''

                    # special spelling for second
                    if number.integer.value == 2:
                        number.last_nonzero.string = 'máso'

                    # modifying group scale on integer side
                    if side == number.integer:
                        group.suffix = scale_ord[group.index]

            # above 2000 use '-' separator
            if group.value > 0 and group.index > 0 and side.value > 2000:
                # the separator is not good because of potential empty groups
                group.suffix += '-'

            # create `ezer` instead of `egyezer` if it is the begining
            elif group.index == 1 and group.value == 1:
                group.string = ''
            

    frac_end = ' tized század ezred tízezred százezred milliomod'.split(' ')
    frac_end_ord = ' e o e e e o'.split(' ')

    # add suffix on fraction side
    if number.fraction.value > 0:
        number.fraction.suffix = ' ' + frac_end[len(number.fraction)]

        # add extra stuffing to fit general ordinal number suffix
        if ordinal:
            number.fraction.suffix += frac_end_ord[len(number.fraction)]

    
    
    
