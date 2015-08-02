# -*- coding: utf-8 -*-
"""
Spelling for locale: hu_*
"""
from __future__ import division, print_function, unicode_literals

from . import spell
from .utils import prod

@spell('hu_HU',
    integer_grouping=3, fraction_grouping=3,
    maximum_precision=6, maximum_digits=66,
    allow_fraction_ordinals=False,
    )
def hu_HU(number, state_rounded=False):
    """
    Based on the official language guideline of Hungary:
    http://hu.wikisource.org/wiki/A_magyar_helyes%C3%ADr%C3%A1s_szab%C3%A1lyai/Egy%C3%A9b_tudnival%C3%B3k#288.
    http://hu.wikipedia.org/wiki/Wikip%C3%A9dia:Helyes%C3%ADr%C3%A1s/A_sz%C3%A1mok_%C3%ADr%C3%A1sa

    Names of the powers of ten: http://hu.wikipedia.org/wiki/T%C3%ADz_hatv%C3%A1nyai

    For doublechecking: http://helyesiras.mta.hu

    Currently supports: +/- 10^-6 -- 10^66-1
    Maximum could easily be extended, currently
    999999999999999999999999999999999999999999999999999999999999999999
    (66 pieces of the digit 9)
    Minimum is the same in negative.
    The smallest number 0.000001

    :copyright: (c) 2013 by Szabolcs Blága
    :license: BSD, see LICENSE in babel for more details.
    """

    # name-parts for the Hungarian long scale (every 10^6 has an unique name)
    scale_base = 'm b tr kvadr kvint szext szept okt non dec'
    scale = ['', 'ezer'] + prod(scale_base, 'illió illiárd')
    scale_ord = ['', 'ezre'] + prod(scale_base, 'illiomo illiárdo')
    # alternate spelling (millió, ezermillió, billió, ezerbillió, stb.)

    # maximum acceptable number should be defined in the decorator parameters

    if len(number.integer) < 2 and number.integer.value == 0:
        number.integer.string = 'nulla'

    # initialization running once
    if number.fraction:
        number.separator = ' egész '

    if number.rounded and state_rounded:
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
    if number.ordinal:
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
                if number.ordinal and side == number.integer and digit == number.last_nonzero:

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
    # needed for fractional ordinals only (curretly not supported by the preprocessor)
    frac_end_ord = ' e o e e e o'.split(' ')

    # add suffix on fraction side
    if number.fraction.value > 0:
        number.fraction.suffix = ' ' + frac_end[len(number.fraction)]

        # add extra stuffing to fit general ordinal number suffix for fractions
        if number.ordinal:
            number.fraction.suffix += frac_end_ord[len(number.fraction)]
