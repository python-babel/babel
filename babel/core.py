# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

"""Core locale representation and locale data access gateway."""

from babel import localedata

__all__ = ['UnknownLocaleError', 'Locale', 'negotiate', 'parse']
__docformat__ = 'restructuredtext en'


class UnknownLocaleError(Exception):
    """Exception thrown when a locale is requested for which no locale data
    is available.
    """

    def __init__(self, identifier):
        """Create the exception.
        
        :param identifier: the identifier string of the unsupported locale
        """
        Exception.__init__(self, 'unknown locale %r' % identifier)
        self.identifier = identifier


class Locale(object):
    """Representation of a specific locale.
    
    >>> locale = Locale('en', territory='US')
    >>> repr(locale)
    '<Locale "en_US">'
    >>> locale.display_name
    u'English (United States)'
    
    A `Locale` object can also be instantiated from a raw locale string:
    
    >>> locale = Locale.parse('en-US', sep='-')
    >>> repr(locale)
    '<Locale "en_US">'
    
    `Locale` objects provide access to a collection of locale data, such as
    territory and language names, number and date format patterns, and more:
    
    >>> locale.number_symbols['decimal']
    u'.'

    If a locale is requested for which no locale data is available, an
    `UnknownLocaleError` is raised:
    
    >>> Locale.parse('en_DE')
    Traceback (most recent call last):
        ...
    UnknownLocaleError: unknown locale 'en_DE'
    
    :see: `IETF RFC 3066 <http://www.ietf.org/rfc/rfc3066.txt>`_
    """

    def __init__(self, language, territory=None, variant=None):
        """Initialize the locale object from the given identifier components.
        
        >>> locale = Locale('en', 'US')
        >>> locale.language
        'en'
        >>> locale.territory
        'US'
        
        :param language: the language code
        :param territory: the territory (country or region) code
        :param variant: the variant code
        :raise `UnknownLocaleError`: if no locale data is available for the
                                     requested locale
        """
        self.language = language
        self.territory = territory
        self.variant = variant
        identifier = str(self)
        try:
            self._data = localedata.load(identifier)
        except IOError:
            raise UnknownLocaleError(identifier)

    def parse(cls, identifier, sep='_'):
        """Create a `Locale` instance for the given locale identifier.
        
        >>> l = Locale.parse('de-DE', sep='-')
        >>> l.display_name
        u'Deutsch (Deutschland)'
        
        If the `identifier` parameter is not a string, but actually a `Locale`
        object, that object is returned:
        
        >>> Locale.parse(l)
        <Locale "de_DE">
        
        :param identifier: the locale identifier string
        :param sep: optional component separator
        :return: a corresponding `Locale` instance
        :rtype: `Locale`
        :raise `ValueError`: if the string does not appear to be a valid locale
                             identifier
        :raise `UnknownLocaleError`: if no locale data is available for the
                                     requested locale
        """
        if type(identifier) is cls:
            return identifier
        return cls(*parse(identifier, sep=sep))
    parse = classmethod(parse)

    def __repr__(self):
        return '<Locale "%s">' % str(self)

    def __str__(self):
        return '_'.join(filter(None, [self.language, self.territory,
                                      self.variant]))

    def display_name(self):
        retval = self.languages.get(self.language)
        if self.territory:
            variant = ''
            if self.variant:
                variant = ', %s' % self.variants.get(self.variant)
            retval += ' (%s%s)' % (self.territories.get(self.territory), variant)
        return retval
    display_name = property(display_name, doc="""\
        The localized display name of the locale.
        
        >>> Locale('en').display_name
        u'English'
        >>> Locale('en', 'US').display_name
        u'English (United States)'
        
        :type: `unicode`
        """)

    #{ General Locale Display Names

    def languages(self):
        return self._data['languages']
    languages = property(languages, doc="""\
        Mapping of language codes to translated language names.
        
        >>> Locale('de', 'DE').languages['ja']
        u'Japanisch'
        
        :type: `dict`
        :see: `ISO 639 <http://www.loc.gov/standards/iso639-2/>`_
        """)

    def scripts(self):
        return self._data['scripts']
    scripts = property(scripts, doc="""\
        Mapping of script codes to translated script names.
        
        >>> Locale('en', 'US').scripts['Hira']
        u'Hiragana'
        
        :type: `dict`
        :see: `ISO 15924 <http://www.evertype.com/standards/iso15924/>`_
        """)

    def territories(self):
        return self._data['territories']
    territories = property(territories, doc="""\
        Mapping of script codes to translated script names.
        
        >>> Locale('es', 'CO').territories['DE']
        u'Alemania'
        
        :type: `dict`
        :see: `ISO 3166 <http://www.iso.org/iso/en/prods-services/iso3166ma/>`_
        """)

    def variants(self):
        return self._data['variants']
    variants = property(variants, doc="""\
        Mapping of script codes to translated script names.
        
        >>> Locale('de', 'DE').variants['1901']
        u'alte deutsche Rechtschreibung'
        
        :type: `dict`
        """)

    #{ Number Formatting

    def currencies(self):
        return self._data['currency_names']
    currencies = property(currencies, doc="""\
        Mapping of currency codes to translated currency names.
        
        >>> Locale('en').currencies['COP']
        u'Colombian Peso'
        >>> Locale('de', 'DE').currencies['COP']
        u'Kolumbianischer Peso'
        
        :type: `dict`
        """)

    def currency_symbols(self):
        return self._data['currency_symbols']
    currency_symbols = property(currency_symbols, doc="""\
        Mapping of currency codes to symbols.
        
        >>> Locale('en').currency_symbols['USD']
        u'US$'
        >>> Locale('en', 'US').currency_symbols['USD']
        u'$'
        
        :type: `dict`
        """)

    def number_symbols(self):
        return self._data['number_symbols']
    number_symbols = property(number_symbols, doc="""\
        Symbols used in number formatting.
        
        >>> Locale('fr', 'FR').number_symbols['decimal']
        u','
        
        :type: `dict`
        """)

    def decimal_formats(self):
        return self._data['decimal_formats']
    decimal_formats = property(decimal_formats, doc="""\
        Locale patterns for decimal number formatting.
        
        >>> Locale('en', 'US').decimal_formats[None]
        <NumberPattern u'#,##0.###'>
        
        :type: `dict`
        """)

    def percent_formats(self):
        return self._data['percent_formats']
    percent_formats = property(percent_formats, doc="""\
        Locale patterns for percent number formatting.
        
        >>> Locale('en', 'US').percent_formats[None]
        <NumberPattern u'#,##0%'>
        
        :type: `dict`
        """)

    #{ Calendar Information and Date Formatting

    def periods(self):
        return self._data['periods']
    periods = property(periods, doc="""\
        Locale display names for day periods (AM/PM).
        
        >>> Locale('en', 'US').periods['am']
        u'AM'
        
        :type: `dict`
        """)

    def days(self):
        return self._data['days']
    days = property(days, doc="""\
        Locale display names for weekdays.
        
        >>> Locale('de', 'DE').days['format']['wide'][3]
        u'Donnerstag'
        
        :type: `dict`
        """)

    def months(self):
        return self._data['months']
    months = property(months, doc="""\
        Locale display names for months.
        
        >>> Locale('de', 'DE').months['format']['wide'][10]
        u'Oktober'
        
        :type: `dict`
        """)

    def quarters(self):
        return self._data['quarters']
    quarters = property(quarters, doc="""\
        Locale display names for quarters.
        
        >>> Locale('de', 'DE').quarters['format']['wide'][1]
        u'1. Quartal'
        
        :type: `dict`
        """)

    def eras(self):
        return self._data['eras']
    eras = property(eras, doc="""\
        Locale display names for eras.
        
        >>> Locale('en', 'US').eras['wide'][1]
        u'Anno Domini'
        >>> Locale('en', 'US').eras['abbreviated'][0]
        u'BC'
        
        :type: `dict`
        """)

    def time_zones(self):
        return self._data['time_zones']
    time_zones = property(time_zones, doc="""\
        Locale display names for time zones.
        
        >>> Locale('en', 'US').time_zones['America/Los_Angeles']['long']['standard']
        u'Pacific Standard Time'
        >>> Locale('en', 'US').time_zones['Europe/Dublin']['city']
        u'Dublin'
        
        :type: `dict`
        """)

    def first_week_day(self):
        return self._data['week_data']['first_day']
    first_week_day = property(first_week_day, doc="""\
        The first day of a week.
        
        >>> Locale('de', 'DE').first_week_day
        0
        >>> Locale('en', 'US').first_week_day
        6
        
        :type: `int`
        """)

    def weekend_start(self):
        return self._data['week_data']['weekend_start']
    weekend_start = property(weekend_start, doc="""\
        The day the weekend starts.
        
        >>> Locale('de', 'DE').weekend_start
        5
        
        :type: `int`
        """)

    def weekend_end(self):
        return self._data['week_data']['weekend_end']
    weekend_end = property(weekend_end, doc="""\
        The day the weekend ends.
        
        >>> Locale('de', 'DE').weekend_end
        6
        
        :type: `int`
        """)

    def min_week_days(self):
        return self._data['week_data']['min_days']
    min_week_days = property(min_week_days, doc="""\
        The minimum number of days in a week so that the week is counted as the
        first week of a year or month.
        
        >>> Locale('de', 'DE').min_week_days
        4
        
        :type: `int`
        """)

    def date_formats(self):
        return self._data['date_formats']
    date_formats = property(date_formats, doc="""\
        Locale patterns for date formatting.
        
        >>> Locale('en', 'US').date_formats['short']
        <DateTimePattern u'M/d/yy'>
        >>> Locale('fr', 'FR').date_formats['long']
        <DateTimePattern u'd MMMM yyyy'>
        
        :type: `dict`
        """)

    def time_formats(self):
        return self._data['time_formats']
    time_formats = property(time_formats, doc="""\
        Locale patterns for time formatting.
        
        >>> Locale('en', 'US').time_formats['short']
        <DateTimePattern u'h:mm a'>
        >>> Locale('fr', 'FR').time_formats['long']
        <DateTimePattern u'HH:mm:ss z'>
        
        :type: `dict`
        """)

    def datetime_formats(self):
        return self._data['datetime_formats']
    datetime_formats = property(datetime_formats, doc="""\
        Locale patterns for datetime formatting.
        
        >>> Locale('en').datetime_formats[None]
        u'{1} {0}'
        >>> Locale('th').datetime_formats[None]
        u'{1}, {0}'
        
        :type: `dict`
        """)


def negotiate(preferred, available):
    """Find the best match between available and requested locale strings.
    
    >>> negotiate(['de_DE', 'en_US'], ['de_DE', 'de_AT'])
    'de_DE'
    >>> negotiate(['de_DE', 'en_US'], ['en', 'de'])
    'de'
    
    :param preferred: the list of locale strings preferred by the user
    :param available: the list of locale strings available
    :return: the locale identifier for the best match, or `None` if no match
             was found
    :rtype: `str`
    """
    for locale in preferred:
        if locale in available:
            return locale
        parts = locale.split('_')
        if len(parts) > 1 and parts[0] in available:
            return parts[0]
    return None

def parse(identifier, sep='_'):
    """Parse a locale identifier into a ``(language, territory, variant)``
    tuple.
    
    >>> parse('zh_CN')
    ('zh', 'CN', None)
    
    The default component separator is "_", but a different separator can be
    specified using the `sep` parameter:
    
    >>> parse('zh-CN', sep='-')
    ('zh', 'CN', None)
    
    :param identifier: the locale identifier string
    :param sep: character that separates the different parts of the locale
                string
    :return: the ``(language, territory, variant)`` tuple
    :rtype: `tuple`
    :raise `ValueError`: if the string does not appear to be a valid locale
                         identifier
    
    :see: `IETF RFC 3066 <http://www.ietf.org/rfc/rfc3066.txt>`_
    """
    parts = identifier.split(sep)
    lang, territory, variant = parts[0].lower(), None, None
    if not lang.isalpha():
        raise ValueError('expected only letters, got %r' % lang)
    if len(parts) > 1:
        territory = parts[1].upper().split('.', 1)[0]
        if not territory.isalpha():
            raise ValueError('expected only letters, got %r' % territory)
        if len(parts) > 2:
            variant = parts[2].upper().split('.', 1)[0]
    return lang, territory, variant
