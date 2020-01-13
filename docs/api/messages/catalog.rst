Messages and Catalogs
=====================

.. module:: babel.messages.catalog

This module provides a basic interface to hold catalog and message
information.  It's generally used to modify a gettext catalog but it is
not being used to actually use the translations.

Catalogs
--------

.. autoclass:: Catalog
   :members:
   :special-members: __iter__

Messages
--------

.. autoclass:: Message
   :members:

Exceptions
----------

.. autoexception:: TranslationError
