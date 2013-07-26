Core Functionality
==================

.. module:: babel.core

The core API provides the basic core functionality.  Primarily it provides
the :class:`Locale` object and ways to create it.  This object
encapsulates a locale and exposes all the data it contains.

All the core functionality is also directly importable from the `babel`
module for convenience.

Basic Interface
---------------

.. autoclass:: Locale
   :members:

.. autofunction:: default_locale

.. autofunction:: negotiate_locale


Exceptions
----------

.. autoexception:: UnknownLocaleError
   :members:


Utility Functions
-----------------

.. autofunction:: get_global

.. autofunction:: parse_locale

.. autofunction:: get_locale_identifier
