# -*- coding: utf-8 -*-
"""
Spelling for locale: en_*
"""
from __future__ import division, print_function, unicode_literals

from . import spell
from .utils import prod

@spell('en',
    integer_grouping=3, fraction_grouping=3,
    maximum_precision=3, maximum_digits=24,
    allow_fraction_ordinals=False,
    )
def en_GB(number, state_rounded=False):
    """
    Draft English speller based on: http://en.wikipedia.org/wiki/English_numerals

    :copyright: (c) 2014 by Szabolcs Blága
    :license: BSD, see LICENSE in babel for more details.
    """
    # name-parts for the short scale
    scale_base = 'm b tr quad quint sext'
    scale = ['', 'thousand'] + prod(scale_base, 'illion')

    if len(number.integer) < 2 and number.integer.value == 0:
        number.integer.string = 'zero'

    # initialization running once
    if number.fraction:
        number.separator = ' point '

    if number.rounded and state_rounded:
        number.prefix = 'approximately '

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
    if number.ordinal:
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
                if number.ordinal and side == number.integer and digit == number.last_nonzero:

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
