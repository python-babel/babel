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

"""Various utility classes and functions."""

from datetime import timedelta, tzinfo
import os
import re

__all__ = ['pathmatch', 'relpath', 'LazyProxy', 'UTC']
__docformat__ = 'restructuredtext en'

def pathmatch(pattern, filename):
    """Extended pathname pattern matching.
    
    This function is similar to what is provided by the ``fnmatch`` module in
    the Python standard library, but:
    
     * can match complete (relative or absolute) path names, and not just file
       names, and
     * also supports a convenience pattern ("**") to match files at any
       directory level.
    
    Examples:
    
    >>> pathmatch('**.py', 'bar.py')
    True
    >>> pathmatch('**.py', 'foo/bar/baz.py')
    True
    >>> pathmatch('**.py', 'templates/index.html')
    False
    
    >>> pathmatch('**/templates/*.html', 'templates/index.html')
    True
    >>> pathmatch('**/templates/*.html', 'templates/foo/bar.html')
    False
    
    :param pattern: the glob pattern
    :param filename: the path name of the file to match against
    :return: `True` if the path name matches the pattern, `False` otherwise
    :rtype: `bool`
    """
    symbols = {
        '?':   '[^/]',
        '?/':  '[^/]/',
        '*':   '[^/]+',
        '*/':  '[^/]+/',
        '**/': '(?:.+/)*?',
        '**':  '(?:.+/)*?[^/]+',
    }
    buf = []
    for idx, part in enumerate(re.split('([?*]+/?)', pattern)):
        if idx % 2:
            buf.append(symbols[part])
        elif part:
            buf.append(re.escape(part))
    return re.match(''.join(buf) + '$', filename) is not None


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

    def __setattr__(self, key, value):
        setattr(self.value, name, value)

    def __delitem__(self, key):
        del self.value[key]

    def __getitem__(self, key):
        return self.value[key]

    def __setitem__(self, key, value):
        self.value[name] = value


try:
    relpath = os.path.relpath
except AttributeError:
    def relpath(path, start='.'):
        """Compute the relative path to one path from another.
        
        >>> relpath('foo/bar.txt', '')
        'foo/bar.txt'
        >>> relpath('foo/bar.txt', 'foo')
        'bar.txt'
        >>> relpath('foo/bar.txt', 'baz')
        '../foo/bar.txt'
        
        :return: the relative path
        :rtype: `basestring`
        """
        start_list = os.path.abspath(start).split(os.sep)
        path_list = os.path.abspath(path).split(os.sep)

        # Work out how much of the filepath is shared by start and path.
        i = len(os.path.commonprefix([start_list, path_list]))

        rel_list = [os.path.pardir] * (len(start_list) - i) + path_list[i:]
        return os.path.join(*rel_list)

try:
    from pytz import UTC
except ImportError:
    ZERO = timedelta(0)

    class UTC(tzinfo):
        """Simple `tzinfo` implementation for UTC."""

        def __repr__(self):
            return '<UTC>'

        def __str__(self):
            return 'UTC'

        def utcoffset(self, dt):
            return ZERO

        def tzname(self, dt):
            return 'UTC'

        def dst(self, dt):
            return ZERO

    UTC = UTC()
    """`tzinfo` object for UTC (Universal Time).
    
    :type: `tzinfo`
    """
