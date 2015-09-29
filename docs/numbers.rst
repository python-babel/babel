.. -*- mode: rst; encoding: utf-8 -*-

.. _numbers:

=================
Number Formatting
=================


Support for locale-specific formatting and parsing of numbers is provided by
the ``babel.numbers`` module:

.. code-block:: pycon

    >>> from babel.numbers import format_number, format_decimal, format_percent

Examples:

.. code-block:: pycon

    >>> format_decimal(1.2345, locale='en_US')
    u'1.234'
    >>> format_decimal(1.2345, locale='sv_SE')
    u'1,234'
    >>> format_decimal(12345, locale='de_DE')
    u'12.345'


Pattern Syntax
==============

While Babel makes it simple to use the appropriate number format for a given
locale, you can also force it to use custom patterns. As with date/time
formatting patterns, the patterns Babel supports for number formatting are
based on the `Locale Data Markup Language specification`_ (LDML).

Examples:

.. code-block:: pycon

    >>> format_decimal(-1.2345, format='#,##0.##;-#', locale='en')
    u'-1.23'
    >>> format_decimal(-1.2345, format='#,##0.##;(#)', locale='en')
    u'(1.23)'

The syntax for custom number format patterns is described in detail in the
the specification. The following table is just a relatively brief overview.

 .. _`Locale Data Markup Language specification`: http://unicode.org/reports/tr35/#Number_Format_Patterns

  +----------+-----------------------------------------------------------------+
  | Symbol   | Description                                                     |
  +==========+=================================================================+
  | ``0``    | Digit                                                           |
  +----------+-----------------------------------------------------------------+
  | ``1-9``  | '1' through '9' indicate rounding.                              |
  +----------+-----------------------------------------------------------------+
  | ``@``    | Significant digit                                               |
  +----------+-----------------------------------------------------------------+
  | ``#``    | Digit, zero shows as absent                                     |
  +----------+-----------------------------------------------------------------+
  | ``.``    | Decimal separator or monetary decimal separator                 |
  +----------+-----------------------------------------------------------------+
  | ``-``    | Minus sign                                                      |
  +----------+-----------------------------------------------------------------+
  | ``,``    | Grouping separator                                              |
  +----------+-----------------------------------------------------------------+
  | ``E``    | Separates mantissa and exponent in scientific notation          |
  +----------+-----------------------------------------------------------------+
  | ``+``    | Prefix positive exponents with localized plus sign              |
  +----------+-----------------------------------------------------------------+
  | ``;``    | Separates positive and negative subpatterns                     |
  +----------+-----------------------------------------------------------------+
  | ``%``    | Multiply by 100 and show as percentage                          |
  +----------+-----------------------------------------------------------------+
  | ``‰``    | Multiply by 1000 and show as per mille                          |
  +----------+-----------------------------------------------------------------+
  | ``¤``    | Currency sign, replaced by currency symbol. If doubled,         |
  |          | replaced by international currency symbol. If tripled, uses the |
  |          | long form of the decimal symbol.                                |
  +----------+-----------------------------------------------------------------+
  | ``'``    | Used to quote special characters in a prefix or suffix          |
  +----------+-----------------------------------------------------------------+
  | ``*``    | Pad escape, precedes pad character                              |
  +----------+-----------------------------------------------------------------+


Parsing Numbers
===============

Babel can also parse numeric data in a locale-sensitive manner:

.. code-block:: pycon

    >>> from babel.numbers import parse_decimal, parse_number

Examples:

.. code-block:: pycon

    >>> parse_decimal('1,099.98', locale='en_US')
    1099.98
    >>> parse_decimal('1.099,98', locale='de')
    1099.98
    >>> parse_decimal('2,109,998', locale='de')
    Traceback (most recent call last):
      ...
    NumberFormatError: '2,109,998' is not a valid decimal number

.. note:: Number parsing is not properly implemented yet


===============
Number Spelling
===============

Babel is able to spell cardinal and ordinal numbers locale-sensitively

.. code-block:: pycon

    >>> from babel.numbers import spell_number

.. note::
    Currently only en_GB and hu_HU are implemented.
    Any contribution is welcome!

Examples:

.. code-block:: pycon

    >>> spell_number(23, locale='en_GB')
    u'twenty-three'

    >>> spell_number(.23, locale='en')
    u'zero point twenty-three hundredths'

    >>> spell_number(2015, locale='hu_HU)
    u'kétezer-tizenöt'


Additional parameters allow the spelling for ordinal numbers
and control the rounding precision for fractional numbers.

.. code-block:: pycon

    >>> spell_number(23, locale='en_GB', ordinal=True)
    u'twenty-third'

    >>> spell_number(.23, locale='en', precision=1)
    u'zero point two tenths'

    >>> spell_number(2015, locale='hu_HU', ordinal=True)
    u'kétezer-tizenötödik'

If no speller function exists for the given locale
(after negotiation) a ``SpellerNotFound`` error is thrown.

It is also possible to implement locale specific parameters
if it is required by the given language.
