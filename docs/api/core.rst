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

.. autofunction:: get_cldr_version


.. _territory-containment:

Territory Containment
---------------------

The global data includes CLDR's primary geographic hierarchy of territories,
subregions, continents, and the world. Use ``territory_parents`` to find the
immediate parent of a territory or region. For example, Argentina belongs to
South America, which belongs to the Americas, which belongs to the world::

    >>> from babel.core import Locale, get_global
    >>> parents = get_global('territory_parents')
    >>> parents['AR'], parents['005'], parents['019']
    ('005', '019', '001')
    >>> '001' in parents
    False

Use ``territory_containment`` for the reverse direction. Each value is a tuple
of direct child codes; descendants are not included recursively. Territories
without children do not appear as keys::

    >>> children = get_global('territory_containment')
    >>> 'AR' in children['005']
    True
    >>> 'AR' in children['019']
    False
    >>> 'AR' in children
    False

Codes are strings, including numeric region codes with leading zeros. Their
localized names are available through :attr:`Locale.territories`::

    >>> names = Locale('en').territories
    >>> [names[code] for code in ('AR', '005', '019', '001')]
    ['Argentina', 'South America', 'Americas', 'world']

These mappings exclude deprecated containment entries and auxiliary groupings,
including the European Union, the Eurozone, the United Nations, and overlapping
geographic groupings such as Latin America. This keeps every child in a single
primary geographic hierarchy. The data follows CLDR and is not a list of
officially assigned ISO country codes. It is independent of locale inheritance
and timezone mappings.
