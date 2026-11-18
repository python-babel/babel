.. -*- mode: rst; encoding: utf-8 -*-

============
Introduction
============

The functionality Babel provides for internationalization (I18n) and
localization (L10N) can be separated into two different aspects:

 * tools to build and work with ``gettext`` message catalogs, and
 * a Python interface to the CLDR (Common Locale Data Repository), providing
   access to various locale display names, localized number and date
   formatting, etc.


Message Catalogs
================

While the Python standard library includes a :mod:`gettext` module that
enables applications to use message catalogs, it requires developers to
build these catalogs using GNU tools such as ``xgettext``, ``msgmerge``,
and ``msgfmt``.  And while ``xgettext`` does have support for extracting
messages from Python files, it does not know how to deal with other kinds
of files commonly found in Python web-applications, such as templates, nor
does it provide an easy extensibility mechanism to add such support.

Babel addresses this by providing a framework where various extraction
methods can be plugged in to a larger message extraction framework, and
also removes the dependency on the GNU ``gettext`` tools for common tasks,
as these aren't necessarily available on all platforms. See
:ref:`messages` for details on this aspect of Babel.


Locale Data
===========

Furthermore, while the Python standard library does include support for
basic localization with respect to the formatting of numbers and dates
(the :mod:`locale` module, among others), this support is based on the
assumption that there will be only one specific locale used per process
(at least simultaneously.) Also, it doesn't provide access to other kinds
of locale data, such as the localized names of countries, languages, or
time-zones, which are frequently needed in web-based applications.

For these requirements, Babel includes data extracted from the `Common
Locale Data Repository (CLDR) <https://unicode.org/cldr/>`_, and provides a
number of convenient methods for accessing and using this data. See
:ref:`locale-data`, :ref:`date-and-time`, and :ref:`numbers` for more
information on this aspect of Babel.

CLDR features in Babel
----------------------

Babel exposes a subset of CLDR through its Python APIs. Use this table to
find the API for the locale data you need.

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - CLDR data
     - Where to use it in Babel
   * - Language, script, and territory names
     - :class:`babel.core.Locale` exposes localized names through its
       ``languages``, ``scripts``, and ``territories`` properties.
   * - Dates, times, and time zones
     - :mod:`babel.dates` formats dates, times, intervals, and localized
       time zone names.
   * - Numbers and currencies
     - :mod:`babel.numbers` formats decimals, percentages, and
       currencies, and provides localized currency names and symbols.
   * - Measurement units
     - :mod:`babel.units` formats quantities with localized unit names.
   * - Lists
     - :mod:`babel.lists` joins items using locale-specific separators
       and conjunctions.
   * - Cardinal and ordinal plurals
     - :class:`babel.core.Locale` provides ``plural_form`` and
       ``ordinal_form`` to select the locale's plural category.
   * - Languages spoken in a territory
     - :mod:`babel.languages` exposes language population estimates
       and official status by territory.

Babel does not provide locale-aware string sorting (CLDR collation) or
transliteration (CLDR transforms).
