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

"""Low-level locale data access.

:note: The `Locale` class, which uses this module under the hood, provides a
       more convenient interface for accessing the locale data.
"""

import os
import pickle
try:
    import threading
except ImportError:
    import dummy_threading as threading

__all__ = ['exists', 'load']
__docformat__ = 'restructuredtext en'

_cache = {}
_cache_lock = threading.RLock()
_dirname = os.path.join(os.path.dirname(__file__), 'localedata')

def exists(name):
    """Check whether locale data is available for the given locale.
    
    :param name: the locale identifier string
    :return: `True` if the locale data exists, `False` otherwise
    :rtype: `bool`
    """
    if name in _cache:
        return True
    return os.path.exists(os.path.join(_dirname, '%s.dat' % name))

def list():
    """Return a list of all locale identifiers for which locale data is
    available.
    
    :return: a list of locale identifiers (strings)
    :rtype: `list`
    :since: version 0.8.1
    """
    return [stem for stem, extension in [
        os.path.splitext(filename) for filename in os.listdir(_dirname)
    ] if extension == '.dat' and stem != 'root']

def load(name):
    """Load the locale data for the given locale.
    
    The locale data is a dictionary that contains much of the data defined by
    the Common Locale Data Repository (CLDR). This data is stored as a
    collection of pickle files inside the ``babel`` package.
    
    >>> d = load('en_US')
    >>> d['languages']['sv']
    u'Swedish'
    
    Note that the results are cached, and subsequent requests for the same
    locale return the same dictionary:
    
    >>> d1 = load('en_US')
    >>> d2 = load('en_US')
    >>> d1 is d2
    True
    
    :param name: the locale identifier string (or "root")
    :return: the locale data
    :rtype: `dict`
    :raise `IOError`: if no locale data file is found for the given locale
                      identifer, or one of the locales it inherits from
    """
    _cache_lock.acquire()
    try:
        data = _cache.get(name)
        if not data:
            # Load inherited data
            if name == 'root':
                data = {}
            else:
                parts = name.split('_')
                if len(parts) == 1:
                    parent = 'root'
                else:
                    parent = '_'.join(parts[:-1])
                data = load(parent).copy()
            filename = os.path.join(_dirname, '%s.dat' % name)
            fileobj = open(filename, 'rb')
            try:
                if name != 'root':
                    merge(data, pickle.load(fileobj))
                else:
                    data = pickle.load(fileobj)
                _cache[name] = data
            finally:
                fileobj.close()
        return data
    finally:
        _cache_lock.release()

def merge(dict1, dict2):
    """Merge the data from `dict2` into the `dict1` dictionary, making copies
    of nested dictionaries.
    
    :param dict1: the dictionary to merge into
    :param dict2: the dictionary containing the data that should be merged
    """
    for key, value in dict2.items():
        if value is not None:
            if type(value) is dict:
                dict1[key] = dict1.get(key, {}).copy()
                merge(dict1[key], value)
            else:
                dict1[key] = value
