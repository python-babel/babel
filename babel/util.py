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

import os
import re

__all__ = ['default_locale', 'extended_glob', 'lazy']
__docformat__ = 'restructuredtext en'

def default_locale(kind):
    """Returns the default locale for a given category, based on environment
    variables.
    
    :param kind: one of the ``LC_XXX`` environment variable names
    :return: the value of the variable, or any of the fallbacks (``LC_ALL`` and
             ``LANG``)
    :rtype: `str`
    """
    for name in (kind, 'LC_ALL', 'LANG'):
        locale = os.getenv(name)
        if locale is not None:
            return locale

def extended_glob(pattern, dirname=''):
    """Extended pathname pattern expansion.
    
    This function is similar to what is provided by the ``glob`` module in the
    Python standard library, but also supports a convenience pattern ("**") to
    match files at any directory level.
    
    :param pattern: the glob pattern
    :param dirname: the path to the directory in which to search for files
                     matching the given pattern
    :return: an iterator over the absolute filenames of any matching files
    :rtype: ``iterator``
    """
    symbols = {
        '?':   '[^/]',
        '?/':  '[^/]/',
        '*':   '[^/]+',
        '*/':  '[^/]+/',
        '**':  '(?:.+/)*?',
        '**/': '(?:.+/)*?',
    }
    buf = []
    for idx, part in enumerate(re.split('([?*]+/?)', pattern)):
        if idx % 2:
            buf.append(symbols[part])
        elif part:
            buf.append(re.escape(part))
    regex = re.compile(''.join(buf) + '$')

    absname = os.path.abspath(dirname)
    for root, dirnames, filenames in os.walk(absname):
        for subdir in dirnames:
            if subdir.startswith('.') or subdir.startswith('_'):
                dirnames.remove(subdir)
        for filename in filenames:
            filepath = relpath(
                os.path.join(root, filename).replace(os.sep, '/'),
                dirname
            )
            if regex.match(filepath):
                yield filepath

def lazy(func):
    """Return a new function that lazily evaluates another function.
    
    >>> lazystr = lazy(str)
    >>> ls = lazystr('foo')
    >>> print ls
    foo
    
    :param func: the function to wrap
    :return: a lazily-evaluated version of the function
    :rtype: ``function``
    """
    def newfunc(*args, **kwargs):
        return LazyProxy(func, *args, **kwargs)
    return newfunc


class LazyProxy(object):
    """
    
    >>> lazystr = LazyProxy(str, 'bar')
    >>> print lazystr
    bar
    >>> u'foo' + lazystr
    u'foobar'
    """

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._value = None

    def value(self):
        if self._value is None:
            self._value = self.func(*self.args, **self.kwargs)
        return self._value
    value = property(value)

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

    def __cmp__(self, other):
        return cmp(self.value, other)

    def __rcmp__(self, other):
        return other + self.value

    def __eq__(self, other):
        return self.value == other

#    def __delattr__(self, name):
#        delattr(self.value, name)
#
#    def __getattr__(self, name):
#        return getattr(self.value, name)
#
#    def __setattr__(self, name, value):
#        setattr(self.value, name, value)

    def __delitem__(self, key):
        del self.value[name]

    def __getitem__(self, key):
        return self.value[name]

    def __setitem__(self, key, value):
        self.value[name] = value


try:
    relpath = os.path.relpath
except AttributeError:
    def relpath(path, start='.'):
        start_list = os.path.abspath(start).split(os.sep)
        path_list = os.path.abspath(path).split(os.sep)

        # Work out how much of the filepath is shared by start and path.
        i = len(os.path.commonprefix([start_list, path_list]))

        rel_list = [os.path.pardir] * (len(start_list) - i) + path_list[i:]
        return os.path.join(*rel_list)
