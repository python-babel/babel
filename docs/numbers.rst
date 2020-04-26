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

 .. _`Locale Data Markup Language specification`:
    https://unicode.org/reports/tr35/#Number_Format_Patterns

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


Rounding Modes
==============

Since Babel makes full use of Python's `Decimal`_ type to perform number
rounding before formatting, users have the chance to control the rounding mode
and other configurable parameters through the active `Context`_ instance.

By default, Python rounding mode is ``ROUND_HALF_EVEN`` which complies with
`UTS #35 section 3.3`_.  Yet, the caller has the opportunity to tweak the
current context before formatting a number or currency:

.. code-block:: pycon

    >>> from babel.numbers import decimal, format_decimal
    >>> with decimal.localcontext(decimal.Context(rounding=decimal.ROUND_DOWN)):
    >>>    txt = format_decimal(123.99, format='#', locale='en_US')
    >>> txt
    u'123'

It is also possible to use ``decimal.setcontext`` or directly modifying the
instance returned by ``decimal.getcontext``.  However, using a context manager
is always more convenient due to the automatic restoration and the ability to
nest them.

Whatever mechanism is chosen, always make use of the ``decimal`` module imported
from ``babel.numbers``.  For efficiency reasons, Babel uses the fastest decimal
implementation available, such as `cdecimal`_.  These various implementation
offer an identical API, but their types and instances do **not** interoperate
with each other.

For example, the previous example can be slightly modified to generate
unexpected results on Python 2.7, with the `cdecimal`_ module installed:

.. code-block:: pycon

    >>> from decimal import localcontext, Context, ROUND_DOWN
    >>> from babel.numbers import format_decimal
    >>> with localcontext(Context(rounding=ROUND_DOWN)):
    >>>    txt = format_decimal(123.99, format='#', locale='en_US')
    >>> txt
    u'124'

Changing other parameters such as the precision may also alter the results of
the number formatting functions.  Remember to test your code to make sure it
behaves as desired.

.. _Decimal: https://docs.python.org/3/library/decimal.html#decimal-objects
.. _Context: https://docs.python.org/3/library/decimal.html#context-objects
.. _`UTS #35 section 3.3`: https://www.unicode.org/reports/tr35/tr35-numbers.html#Formatting
.. _cdecimal: https://pypi.org/project/cdecimal/


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

Note: as of version 2.8.0, the ``parse_number`` function has limited
functionality. It can remove group symbols of certain locales from numeric
strings, but may behave unexpectedly until its logic handles more encoding
issues and other special cases.

Examples:

.. code-block:: pycon

    >>> parse_number('1,099', locale='en_US')
    1099
    >>> parse_number('1.099.024', locale='de')
    1099024
    >>> parse_number('123' + u'\xa0' + '4567', locale='ru')
    1234567
    >>> parse_number('123 4567', locale='ru')
      ...
    NumberFormatError: '123 4567' is not a valid number
