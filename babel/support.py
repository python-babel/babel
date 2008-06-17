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

"""Several classes and functions that help with integrating and using Babel
in applications.

.. note: the code in this module is not used by Babel itself
"""

from datetime import date, datetime, time
import gettext

try:
    set
except NameError:
    from sets import set

from babel.core import Locale
from babel.dates import format_date, format_datetime, format_time, LC_TIME
from babel.numbers import format_number, format_decimal, format_currency, \
                          format_percent, format_scientific, LC_NUMERIC
from babel.util import UTC, PYTHON_FORMAT

__all__ = ['Format', 'LazyProxy', 'Translations', 'validate_format']
__docformat__ = 'restructuredtext en'


class Format(object):
    """Wrapper class providing the various date and number formatting functions
    bound to a specific locale and time-zone.
    
    >>> fmt = Format('en_US', UTC)
    >>> fmt.date(date(2007, 4, 1))
    u'Apr 1, 2007'
    >>> fmt.decimal(1.2345)
    u'1.234'
    """

    def __init__(self, locale, tzinfo=None):
        """Initialize the formatter.
        
        :param locale: the locale identifier or `Locale` instance
        :param tzinfo: the time-zone info (a `tzinfo` instance or `None`)
        """
        self.locale = Locale.parse(locale)
        self.tzinfo = tzinfo

    def date(self, date=None, format='medium'):
        """Return a date formatted according to the given pattern.
        
        >>> fmt = Format('en_US')
        >>> fmt.date(date(2007, 4, 1))
        u'Apr 1, 2007'
        
        :see: `babel.dates.format_date`
        """
        return format_date(date, format, locale=self.locale)

    def datetime(self, datetime=None, format='medium'):
        """Return a date and time formatted according to the given pattern.
        
        >>> from pytz import timezone
        >>> fmt = Format('en_US', tzinfo=timezone('US/Eastern'))
        >>> fmt.datetime(datetime(2007, 4, 1, 15, 30))
        u'Apr 1, 2007 11:30:00 AM'
        
        :see: `babel.dates.format_datetime`
        """
        return format_datetime(datetime, format, tzinfo=self.tzinfo,
                               locale=self.locale)

    def time(self, time=None, format='medium'):
        """Return a time formatted according to the given pattern.
        
        >>> from pytz import timezone
        >>> fmt = Format('en_US', tzinfo=timezone('US/Eastern'))
        >>> fmt.time(datetime(2007, 4, 1, 15, 30))
        u'11:30:00 AM'
        
        :see: `babel.dates.format_time`
        """
        return format_time(time, format, tzinfo=self.tzinfo, locale=self.locale)

    def number(self, number):
        """Return an integer number formatted for the locale.
        
        >>> fmt = Format('en_US')
        >>> fmt.number(1099)
        u'1,099'
        
        :see: `babel.numbers.format_number`
        """
        return format_number(number, locale=self.locale)

    def decimal(self, number, format=None):
        """Return a decimal number formatted for the locale.
        
        >>> fmt = Format('en_US')
        >>> fmt.decimal(1.2345)
        u'1.234'
        
        :see: `babel.numbers.format_decimal`
        """
        return format_decimal(number, format, locale=self.locale)

    def currency(self, number, currency):
        """Return a number in the given currency formatted for the locale.
        
        :see: `babel.numbers.format_currency`
        """
        return format_currency(number, currency, locale=self.locale)

    def percent(self, number, format=None):
        """Return a number formatted as percentage for the locale.
        
        >>> fmt = Format('en_US')
        >>> fmt.percent(0.34)
        u'34%'
        
        :see: `babel.numbers.format_percent`
        """
        return format_percent(number, format, locale=self.locale)

    def scientific(self, number):
        """Return a number formatted using scientific notation for the locale.
        
        :see: `babel.numbers.format_scientific`
        """
        return format_scientific(number, locale=self.locale)


class LazyProxy(object):
    """Class for proxy objects that delegate to a specified function to evaluate
    the actual object.
    
    >>> def greeting(name='world'):
    ...     return 'Hello, %s!' % name
    >>> lazy_greeting = LazyProxy(greeting, name='Joe')
    >>> print lazy_greeting
    Hello, Joe!
    >>> u'  ' + lazy_greeting
    u'  Hello, Joe!'
    >>> u'(%s)' % lazy_greeting
    u'(Hello, Joe!)'
    
    This can be used, for example, to implement lazy translation functions that
    delay the actual translation until the string is actually used. The
    rationale for such behavior is that the locale of the user may not always
    be available. In web applications, you only know the locale when processing
    a request.
    
    The proxy implementation attempts to be as complete as possible, so that
    the lazy objects should mostly work as expected, for example for sorting:
    
    >>> greetings = [
    ...     LazyProxy(greeting, 'world'),
    ...     LazyProxy(greeting, 'Joe'),
    ...     LazyProxy(greeting, 'universe'),
    ... ]
    >>> greetings.sort()
    >>> for greeting in greetings:
    ...     print greeting
    Hello, Joe!
    Hello, universe!
    Hello, world!
    """
    __slots__ = ['_func', '_args', '_kwargs', '_value']

    def __init__(self, func, *args, **kwargs):
        # Avoid triggering our own __setattr__ implementation
        object.__setattr__(self, '_func', func)
        object.__setattr__(self, '_args', args)
        object.__setattr__(self, '_kwargs', kwargs)
        object.__setattr__(self, '_value', None)

    def value(self):
        if self._value is None:
            value = self._func(*self._args, **self._kwargs)
            object.__setattr__(self, '_value', value)
        return self._value
    value = property(value)

    def __contains__(self, key):
        return key in self.value

    def __nonzero__(self):
        return bool(self.value)

    def __dir__(self):
        return dir(self.value)

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def __str__(self):
        return str(self.value)

    def __unicode__(self):
        return unicode(self.value)

    def __add__(self, other):
        return self.value + other

    def __radd__(self, other):
        return other + self.value

    def __mod__(self, other):
        return self.value % other

    def __rmod__(self, other):
        return other % self.value

    def __mul__(self, other):
        return self.value * other

    def __rmul__(self, other):
        return other * self.value

    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)

    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    def __delattr__(self, name):
        delattr(self.value, name)

    def __getattr__(self, name):
        return getattr(self.value, name)

    def __setattr__(self, name, value):
        setattr(self.value, name, value)

    def __delitem__(self, key):
        del self.value[key]

    def __getitem__(self, key):
        return self.value[key]

    def __setitem__(self, key, value):
        self.value[key] = value


class Translations(gettext.GNUTranslations):
    """An extended translation catalog class."""

    DEFAULT_DOMAIN = 'messages'

    def __init__(self, fileobj=None):
        """Initialize the translations catalog.
        
        :param fileobj: the file-like object the translation should be read
                        from
        """
        gettext.GNUTranslations.__init__(self, fp=fileobj)
        self.files = filter(None, [getattr(fileobj, 'name', None)])

    def load(cls, dirname=None, locales=None, domain=DEFAULT_DOMAIN):
        """Load translations from the given directory.
        
        :param dirname: the directory containing the ``MO`` files
        :param locales: the list of locales in order of preference (items in
                        this list can be either `Locale` objects or locale
                        strings)
        :param domain: the message domain
        :return: the loaded catalog, or a ``NullTranslations`` instance if no
                 matching translations were found
        :rtype: `Translations`
        """
        if locales is not None:
            if not isinstance(locales, (list, tuple)):
                locales = [locales]
            locales = [str(locale) for locale in locales]
        filename = gettext.find(domain or cls.DEFAULT_DOMAIN, dirname, locales)
        if not filename:
            return gettext.NullTranslations()
        return cls(fileobj=open(filename, 'rb'))
    load = classmethod(load)

    def merge(self, translations):
        """Merge the given translations into the catalog.
        
        Message translations in the specfied catalog override any messages with
        the same identifier in the existing catalog.
        
        :param translations: the `Translations` instance with the messages to
                             merge
        :return: the `Translations` instance (``self``) so that `merge` calls
                 can be easily chained
        :rtype: `Translations`
        """
        if isinstance(translations, Translations):
            self._catalog.update(translations._catalog)
            self.files.extend(translations.files)
        return self

    def __repr__(self):
        return "<%s>" % (type(self).__name__)


#: list of format chars that are compatible to each other
_string_format_compatibilities = [
    set(['i', 'd', 'u']),
    set(['x', 'X']),
    set(['f', 'F', 'g', 'G'])
]


def validate_format(format, alternative):
    """Test format string `alternative` against `format`.  `format` can be the
    msgid of a message and `alternative` one of the `msgstr`\s.  The two
    arguments are not interchangeable as `alternative` may contain less
    placeholders if `format` uses named placeholders.

    If `format` does not use string formatting a `TypeError` is raised.

    If the string formatting of `alternative` is compatible to `format` the
    function returns `None`, otherwise a `ValueError` is raised.

    Examples for compatible format strings:

    >>> validate_format('Hello %s!', 'Hallo %s!')
    >>> validate_format('Hello %i!', 'Hallo %d!')

    Example for an incompatible format strings:

    >>> validate_format('Hello %(name)s!', 'Hallo %s!')
    Traceback (most recent call last):
      ...
    TypeError: the format strings are of different kinds

    :param format: The original format string
    :param alternative: The alternative format string that should be checked
                        against format
    :return: None on success
    :raises ValueError: on an formatting error
    """

    def _parse(string):
        result = []
        for match in PYTHON_FORMAT.finditer(string):
            name, format, typechar = match.groups()
            if typechar == '%' and name is not None:
                continue
            result.append((name, typechar))
        return result

    def _compatible(a, b):
        if a == b:
            return True
        for set in _string_format_compatibilities:
            if a in set and b in set:
                return True
        return False

    def _check_positional(results):
        positional = None
        for name, char in results:
            if positional is None:
                positional = name is None
            else:
                if (name is None) != positional:
                    raise ValueError('format string mixes positional '
                                     'and named placeholders')
        return bool(positional)

    a, b = map(_parse, (format, alternative))

    # if a does not use string formattings, we are dealing with invalid
    # input data.  This function only works if the first string provided
    # does contain string format chars
    if not a:
        raise TypeError('original string provided does not use string '
                        'formatting.')

    # now check if both strings are positional or named
    a_positional, b_positional = map(_check_positional, (a, b))
    if a_positional and not b_positional and not b:
        raise ValueError('placeholders are incompatible')
    elif a_positional != b_positional:
        raise TypeError('the format strings are of different kinds')

    # if we are operating on positional strings both must have the
    # same number of format chars and those must be compatible
    if a_positional:
        if len(a) != len(b):
            raise ValueError('positional format placeholders unbalanced')
        for idx, ((_, first), (_, second)) in enumerate(zip(a, b)):
            if not _compatible(first, second):
                raise ValueError('incompatible format for placeholder %d: '
                                 '%r and %r are not compatible' %
                                 (idx + 1, first, second))

    # otherwise the second string must not have names the first one
    # doesn't have and the types of those included must be compatible
    else:
        type_map = dict(a)
        for name, typechar in b:
            if name not in type_map:
                raise ValueError('unknown named placeholder %r' % name)
            elif not _compatible(typechar, type_map[name]):
                raise ValueError('incompatible format for placeholder %r: '
                                 '%r and %r are not compatible' %
                                 (name, typechar, type_map[name]))
