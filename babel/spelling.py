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

import re, decimal


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
        # search for digit function in the module based on data
        cls = self.__class__
        self._speller = cls.get_spell_function(locale)

    def apply(self, number, ordinal=False, **kwargs):
        """Apply the speller for every digit of the number
        
        After the speller is called for every digit the NumberContext objects will
        hold the proper representation of the number

        The speller function is called with every digit. The order is
        integer part first from right to left (!) then fractional part
        also from right to left. Property `digit.first_nonzero` is for the
        integer and property `last_nonzero` is for the fractional part. 
        """
        # generate the number context
        number = self._speller._context_maker(number)
        number.ordinal = ordinal

        # call transform for every digit
        for digit in number.digits:
            self._speller(digit)

        # return the result (construct it recursively)
        return unicode(number)
        
    @classmethod
    def get_spell_function(cls, locale):
        """Search `cls.registry` for the spelling function

        Should find spellers negotiating locale e.g. if there is a general speller
        for all the territories, etc.
        """
        if locale in cls.registry:
            return cls.registry[locale]
        else:
            raise SpellerNotFound("There is no appropriate number speller function for the given locale")


    @classmethod
    def decorate_spell_function(cls, locale, context_maker=None):
        """Explain how the decorator works...

        The actual name of the function that is decorated doesn't really matter
        as it is not used anywhere (might matter although), but than would put
        a constraint on the locales, that cold be used.

        Group_size 0 means the whole main or frac is one big group

        Additional parameters might be:
            reverse_indexing
            
        """
        def decorator(func):
            """Add the speller function to registry

            """
            cm = context_maker if context_maker is not None else ContextMaker()
            # add the parameters as function atributes or as separete entities in the registry?
            func._context_maker = cm
            # check for override issue warning
            cls.registry[locale] = func
            # pervent the module functions to be called directly -- retrun `None`
            return None
        return decorator


# shortcut for cleaner code in the locale specific spell function definitions
spell = NumberSpeller.decorate_spell_function


class ContextBase(object):
    """Basic functionality for context classes"""
    def __init__(self):
        self.prefix = ""
        self.suffix = ""
        self.separator = ""

    def __iter__(self):
        """ """
        return []

    def __unicode__(self):
        """Based on the overrided iterators `self.__iter__`"""
        return '{}{}{}'.format(
            self.prefix,
            self.separator.join(reversed([unicode(e) for e in self])), 
            self.suffix
        )

    def __str__(self):
        return self.__unicode__.encode('utf8')
        

class NumberContext(ContextBase):
    """Represents a number and its internal structure.

    The number is separated into integer and fraction parts
    and the fraction part is also rounded if too detailed.

    Comparison on the NumberContext object should work if it
    was a decimal number.
    """
    def __init__(self, number, integer, fraction, rounded, minus):
        self.value = number
        self.integer = SideContext(integer, self)
        self.fraction = SideContext(fraction, self)
        self.rounded = rounded
        self.minus = minus
        ContextBase.__init__(self)
        
    def __iter__(self):
        yield self.fraction
        yield self.integer

    def __cmp__(self, other):
        if self.value < other: return -1
        if self.value > other: return 1
        return 0

    def __len__(self):
        return sum(1 for _ in self.digits)

    def __abs__(self):
        return abs(self.value)

    def __getitem__(self, key):
        i = 0
        for side in self:
            for group in side:
                for digit in group:
                    if i == key: return digit
                    i += 1

    @property
    def digits(self):
        for side in self:
            for group in side:
                for digit in group:
                    yield digit


class SideContext(ContextBase):
    """ """
    def __init__(self, groups, number):
        self.number = number
        self.groups = tuple(GroupContext(digits, number, self, i) for i, digits in enumerate(groups))

        ContextBase.__init__(self)

    def __iter__(self):
        for group in self.groups:
            yield group

    def __getitem__(self, key):
        return self.groups[key]

    def __len__(self):
        return sum(len(g) for g in self)

    def __cmp__(self, other):
        if int(self) < other: return -1
        if int(self) > other: return 1
        return 0

    def __int__(self):
        exp, s = 0, 0
        for g in self.groups:
            s += int(g)*10**exp
            exp += len(g)
        return s
        
    @property
    def digits(self):
        for group in self:
            for digit in group:
                yield digit


class GroupContext(ContextBase):
    """Represent a group of digits inside a number

    Digits inside the group are indexed from the right.
    
    right, left
    """

    def __init__(self, digits, number, side, index):
        self.digits = tuple(DigitContext(v, number, self, i) for i,v in enumerate(digits))
        self.number = number
        self.side = side
        self.index = index
        ContextBase.__init__(self)

    def __cmp__(self, other):
        if int(self) < other: return -1
        if int(self) > other: return 1
        return 0

    def __int__(self):
        return sum(int(d)*10**e for e,d in enumerate(self.digits))

    def __len__(self):
        return len(self.digits)

    def __iter__(self):
        for digit in self.digits:
            yield digit

    def __getitem__(self, key):
        return self.digits[key]

        
class DigitContext(ContextBase):
    """Represent one digit of a number and its context
    
    string : the representation of the number
    left # None if end of the group
    right # None if end of the group
    is_head : self == self.group[0] || self.left is None
    is_tail : self == self.group[-1] || self.right is None
    is_main : self.number.main == self.group.group
    is_frac : -*-
    """
    def __init__(self, value, number, group, index):
        self.value = value
        self.number = number
        self.group = group
        self.index = index
        self.string = ''

        ContextBase.__init__(self)

    def __iter__(self):
        """Not so nice, but this was it could also inherit from ContextBase"""
        yield self.string

    def __cmp__(self, other):
        if self.value < other: return -1
        if self.value > other: return 1
        return 0

    def __index__(self):
        return self.value

    def __int__(self):
        return self.value # should be int from ContextMaker

    @property
    def first_nonzero(self):
        nonzero = True
        for digit in self.number.digits:
            if digit > 0:
                return (
                    digit.index == self.index and
                    digit.group.index == self.group.index and
                    digit.group.side is self.group.side
                )

    @property
    def integer(self):
        return (self.group.side is self.number.integer)

    @property
    def fraction(self):
        return (self.group.side is self.number.fraction)


class ContextMaker(object):
    def __init__(self, integer_grouping=3, fraction_grouping=3, precision=6):
        """The defaults are based on the Hungarian speller but specified
        there explicitly.

        If no `ContextMaker` is provided for the decorator of a speller
        function, then these defaults are used impicitly. It is strongly
        advised to provide the contextmaker and relevant initialization
        data with every decorated speller function!
        """
        self.integer_grouping = integer_grouping
        self.fraction_grouping = fraction_grouping
        self.precision = precision

    def __call__(self, number):
        """Check number and return context

        Various complecated grouping mechanism could be implemented
        with different `ContextMaker` classes.

        This is a basic implementation of grouping.

        :number:
            Any object that yields a standard Python number format upon
            calling `str` on it.

        return: NumberContext object
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
        number = decimal.Decimal(number)
        # print('raw', number)
        n = number.quantize(decimal.Decimal(10) ** -self.precision)
        # get rid of the exponent or trailing zeros in one step
        n = n.quantize(decimal.Decimal(1)) if n == n.to_integral() else n.normalize()
        rounded = True if n != number else False

        # print('rounded', n)
        # print(str(n))
        m = re.match(r"(-)?(\d+)\.?(\d+)?", str(n))
        
        if m:
            sign, integer, fraction = m.groups()
            # print(integer, fraction)
            integer = reverse_group_by([int(i) for i in integer], self.integer_grouping)
            if fraction and fraction != '0':
                fraction = reverse_group_by([int(i) for i in fraction], self.fraction_grouping)
            else:
                fraction = []
        else:
            raise ValueError('Not a valid number.')

        # print('The number', integer, fraction, rounded)
        return NumberContext(n, integer, fraction, rounded, sign=='-')


#####################################
# locale specific speller functions #
#####################################

@spell('hu_HU', ContextMaker(3, 3, 6))
def hu_HU(digit):
    """
    The Institute for Linguistics of the Hungarian Academy of Sciences will approve
    the code soon (hopefully).

    Based on the official language guideline of Hungary:
    http://hu.wikisource.org/wiki/A_magyar_helyes%C3%ADr%C3%A1s_szab%C3%A1lyai/Egy%C3%A9b_tudnival%C3%B3k#288.
    http://hu.wikipedia.org/wiki/Wikip%C3%A9dia:Helyes%C3%ADr%C3%A1s/A_sz%C3%A1mok_%C3%ADr%C3%A1sa

    Names of the powers of ten: http://hu.wikipedia.org/wiki/T%C3%ADz_hatv%C3%A1nyai

    For doublechecking: http://helyesiras.mta.hu

    Currently supports: +/- 10^66 - 10^-7 

    :copyright: (c) 2013 by Szabolcs Blága
    :license: BSD, see LICENSE in babel for more details.
    """
    # aliases
    number = digit.number
    group = digit.group
    side = digit.group.side
    
    # name-parts for the Hungarian long scale (every 10^6 has an unique name)
    _S = 'm b tr kvadr kvint szext szept okt non dec'.split()
    # putting the scale together up to 10^60 (could be extended further easily)
    scale = ['', 'ezer'] + [n for nn in ((n+'illió', n+'illiárd') for n in _S) for n in nn]
    ord_scale = ['', 'ezre'] + [n for nn in ((n+'illimo', n+'illiárdo') for n in _S) for n in nn]
    # alternate spelling
    # scale = ('', 'ezer') + (n for nn in ((n+'illió', 'ezer'+n+'illió') for n in _S) for n in nn)
    # not so nice sythax but short and almost itertools fast, for performance see:
    # http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python

    if number > 10**(len(scale)*3):
        # return overflow text only once
        if digit.first_nonzero:
            digit.string = 'leírhatatlanul sok'
        return

    # initialization running once
    if digit == number[0]:
        if number.fraction:
            number.separator = ' egész '
        if number.rounded:
            number.prefix = 'kerekítve '
        if number.minus:
            number.prefix += 'mínusz '

    s = '' # short for `digit.string`
    # aliassing groups as abc
    c = (digit.index == 0)
    b = (digit.index == 1)
    a = (digit.index == 2)

    # cardinal spelling
    if digit.integer and abs(number) < 1:
        s = 'nulla'
        
    elif c:
        s = ' egy kettő három négy öt hat hét nyolc kilenc'.split(' ')[digit]
        if group.index > 0:
            # put it into digit.suffix to not interfere with group suffix in ordinals
            digit.suffix = scale[group.index]
            # special: `kettő` would also be good, but `két` is better
            if digit == 2:
                s = 'két' # `kettő` would also be good, but `két` is better
            
        # create `ezer` instead of `egyezer`
        if group.index == 1 and group == 1:
            s = ''
        # the separator is not good because of potential empty groups
        # print('gsuff', abs(number), 'szám', int(number.fraction), 'tört')
        if group > 0 and group.index > 0:
            if digit.integer and abs(number) > 2000:
                group.suffix = '-'
            if digit.fraction and int(number.fraction) > 2000:
                group.suffix = '-'
        
    elif b:
        s = ' tíz húsz harminc negyven ötven hatvan hetven nyolcvan kilencven'.split(' ')[digit]
        if digit.group[0] > 0 and digit < 3:
            s = ' tizen huszon'.split(' ')[digit]
            
    elif a:
        s = '  két három négy öt hat hét nyolc kilenc'.split(' ')[digit]
        if digit > 0:
            s += 'száz' if digit > 0 else ''

    if digit.fraction and group.index == 0 and digit.index == 0:
        group.suffix = ' '+' tized század ezred tízezred százezred milliomod'.split(' ')[len(number.fraction)]


    # ordinal naming (only affects first_nonzero and modifies cardinal)
    if number.ordinal and digit.first_nonzero:
        # general suffix for all ordinal numbers except 1. (including 0!)
        number.suffix = 'dik'
        
        # fraction with some stuffing sounds (not so scientific)
        if digit.fraction:
            group.suffix += ' e o e e e o'.split(' ')[len(number.fraction)]

        # first integer group is special
        elif group.index == 0:
            # zero case is not affected so start with c
            if c:
                s = ' egye kette harma negye ötö hato hete nyolca kilence'.split(' ')[digit]

        
            elif b:
                s = ' tize husza harminca negyvene ötvene hatvana hetvene nyolcvana kilencvene'.split(' ')[digit]
                # no other checks necessary as this is `first_nonzero`, so c is 0!
                    
            elif a:
                s += 'a' # creating `száza`

        # modifying the scale for higher groups
        else:
            digit.suffix = ord_scale[group.index]

    # special cases
    if number.ordinal:
        if number == 0:
            number.suffix = 'dik' # not set above
        if number == 1:
            s = 'első'
            number.suffix = ''
        elif number == 2:
            s = 'máso'

    digit.string = s
