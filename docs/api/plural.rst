Pluralization Support
=====================

.. module:: babel.plural

The pluralization support provides functionality around the CLDR
pluralization rules.  It can parse and evaluate pluralization rules, as
well as convert them to other formats such as gettext.

Basic Interface
---------------

.. autoclass:: PluralRule
   :members:

Conversion Functionality
------------------------

.. autofunction:: to_javascript

.. autofunction:: to_python

.. autofunction:: to_gettext
