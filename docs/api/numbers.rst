Numbers and Currencies
======================

.. module:: babel.numbers

The number module provides functionality to format numbers for different
locales.  This includes arbitrary numbers as well as currency.

Number Formatting
-----------------

.. autofunction:: format_number

.. autofunction:: format_decimal

.. autofunction:: format_compact_decimal

.. autofunction:: format_currency

.. autofunction:: format_compact_currency

.. autofunction:: format_percent

.. autofunction:: format_scientific

Number Parsing
--------------

.. autofunction:: parse_number

.. autofunction:: parse_decimal

Exceptions
----------

.. autoexception:: NumberFormatError
    :members:

.. autoexception:: UnknownCurrencyError
    :members:

.. autoexception:: UnknownCurrencyFormatError
    :members:

.. autoexception:: UnsupportedNumberingSystemError
    :members:

Data Access
-----------

.. autofunction:: get_decimal_symbol

.. autofunction:: get_exponential_symbol

.. autofunction:: get_group_symbol

.. autofunction:: get_infinity_symbol

.. autofunction:: get_minus_sign_symbol

.. autofunction:: get_plus_sign_symbol

Currency Utilities
------------------

.. autofunction:: get_currency_name

.. autofunction:: get_currency_precision

.. autofunction:: get_currency_symbol

.. autofunction:: get_currency_unit_pattern

.. autofunction:: get_territory_currencies

.. autofunction:: is_currency

.. autofunction:: list_currencies

.. autofunction:: normalize_currency

.. autofunction:: validate_currency
