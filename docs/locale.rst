.. -*- mode: rst; encoding: utf-8 -*-

.. _locale-data:

===========
Locale Data
===========

While :ref:`message catalogs <messages>` allow you to localize any
messages in your application, there are a number of strings that are used
in many applications for which translations are readily available.

Imagine for example you have a list of countries that users can choose from,
and you'd like to display the names of those countries in the language the
user prefers. Instead of translating all those country names yourself in your
application, you can make use of the translations provided by the locale data
included with Babel, which is based on the `Common Locale Data Repository
(CLDR) <http://unicode.org/cldr/>`_ developed and maintained by the `Unicode
Consortium <http://unicode.org/>`_.


The ``Locale`` Class
====================

You normally access such locale data through the
:class:`~babel.core.Locale` class provided by Babel:

.. code-block:: pycon

    >>> from babel import Locale
    >>> locale = Locale('en', 'US')
    >>> locale.territories['US']
    u'United States'
    >>> locale = Locale('es', 'MX')
    >>> locale.territories['US']
    u'Estados Unidos'

In addition to country/territory names, the locale data also provides access to
names of languages, scripts, variants, time zones, and more. Some of the data
is closely related to number and date formatting.

Most of the corresponding ``Locale`` properties return dictionaries, where the
key is a code such as the ISO country and language codes. Consult the API
documentation for references to the relevant specifications.


Likely Subtags
==============

When dealing with locales you can run into the situation where a locale
tag is not fully descriptive.  For instance people commonly refer to
``zh_TW`` but that identifier does not resolve to a locale that the CLDR
covers.  Babel's locale identifier parser in that case will attempt to
resolve the most likely subtag to end up with the intended locale:

.. code-block:: pycon

    >>> from babel import Locale
    >>> Locale.parse('zh_TW')
    Locale('zh', territory='TW', script='Hant')

This can also be used to find the most appropriate locale for a territory.
In that case the territory code needs to be prefixed with ``und`` (unknown
language identifier):

.. code-block:: pycon

    >>> Locale.parse('und_AZ')
    Locale('az', territory='AZ', script='Latn')
    >>> Locale.parse('und_DE')
    Locale('de', territory='DE')

Babel currently cannot deal with fuzzy locales (a locale not fully backed
by data files) so we only accept locales that are fully backed by CLDR
data.  This will change in the future, but for the time being this
restriction is in place.


Locale Display Names
====================

Locales itself can be used to describe the locale itself or other locales.
This mainly means that given a locale object you can ask it for its
canonical display name, the name of the language and other things.  Since
the locales cross-reference each other you can ask for locale names in any
language supported by the CLDR:

.. code-block:: pycon

    >>> l = Locale.parse('de_DE')
    >>> l.get_display_name('en_US')
    u'German (Germany)'
    >>> l.get_display_name('fr_FR')
    u'allemand (Allemagne)'

Display names include all the information to uniquely identify a locale
(language, territory, script and variant) which is often not what you
want.  You can also ask for the information in parts:

.. code-block:: pycon

    >>> l.get_language_name('de_DE')
    u'Deutsch'
    >>> l.get_language_name('it_IT')
    u'tedesco'
    >>> l.get_territory_name('it_IT')
    u'Germania'
    >>> l.get_territory_name('pt_PT')
    u'Alemanha'


Calendar Display Names
======================

The :class:`~babel.core.Locale` class provides access to many locale
display names related to calendar display, such as the names of weekdays
or months.

These display names are of course used for date formatting, but can also be
used, for example, to show a list of months to the user in their preferred
language:

.. code-block:: pycon

    >>> locale = Locale('es')
    >>> month_names = locale.months['format']['wide'].items()
    >>> for idx, name in sorted(month_names):
    ...     print name
    enero
    febrero
    marzo
    abril
    mayo
    junio
    julio
    agosto
    septiembre
    octubre
    noviembre
    diciembre
