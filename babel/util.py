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

import codecs
from datetime import timedelta, tzinfo
import os
import parser
import re
import time

__all__ = ['pathmatch', 'relpath', 'UTC', 'LOCALTZ']
__docformat__ = 'restructuredtext en'

# Regexp to match python magic encoding line
PYTHON_MAGIC_COMMENT_re = re.compile(
    r'[ \t\f]* \# .* coding[=:][ \t]*([-\w.]+)', re.VERBOSE)
def parse_encoding(fp):
    """Deduce the encoding of a source file from magic comment.

    It does this in the same way as the `Python interpreter`__

    .. __: http://docs.python.org/ref/encodings.html

    The ``fp`` argument should be a seekable file object.

    (From Jeff Dairiki)
    """
    pos = fp.tell()
    fp.seek(0)
    try:
        line1 = fp.readline()
        has_bom = line1.startswith(codecs.BOM_UTF8)
        if has_bom:
            line1 = line1[len(codecs.BOM_UTF8):]

        m = PYTHON_MAGIC_COMMENT_re.match(line1)
        if not m:
            try:
                parser.suite(line1)
            except SyntaxError:
                # Either it's a real syntax error, in which case the source is
                # not valid python source, or line2 is a continuation of line1,
                # in which case we don't want to scan line2 for a magic
                # comment.
                pass
            else:
                line2 = fp.readline()
                m = PYTHON_MAGIC_COMMENT_re.match(line2)

        if has_bom:
            if m:
                raise SyntaxError(
                    "python refuses to compile code with both a UTF8 "
                    "byte-order-mark and a magic encoding comment")
            return 'utf_8'
        elif m:
            return m.group(1)
        else:
            return None
    finally:
        fp.seek(pos)

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
    match = re.match(''.join(buf) + '$', filename.replace(os.sep, '/'))
    return match is not None


class odict(dict):
    """Ordered dict implementation.
    
    :see: `http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/107747`
    """
    def __init__(self, data=None):
        dict.__init__(self, data or {})
        self._keys = dict.keys(self)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        dict.__setitem__(self, key, item)
        if key not in self._keys:
            self._keys.append(key)

    def __iter__(self):
        return iter(self._keys)

    def clear(self):
        dict.clear(self)
        self._keys = []

    def copy(self):
        d = odict()
        d.update(self)
        return d

    def items(self):
        return zip(self._keys, self.values())

    def keys(self):
        return self._keys[:]

    def setdefault(self, key, failobj = None):
        dict.setdefault(self, key, failobj)
        if key not in self._keys:
            self._keys.append(key)

    def update(self, dict):
        for (key, val) in dict.items():
            self[key] = val

    def values(self):
        return map(self.get, self._keys)


try:
    relpath = os.path.relpath
except AttributeError:
    def relpath(path, start='.'):
        """Compute the relative path to one path from another.
        
        >>> relpath('foo/bar.txt', '').replace(os.sep, '/')
        'foo/bar.txt'
        >>> relpath('foo/bar.txt', 'foo').replace(os.sep, '/')
        'bar.txt'
        >>> relpath('foo/bar.txt', 'baz').replace(os.sep, '/')
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

ZERO = timedelta(0)


class FixedOffsetTimezone(tzinfo):
    """Fixed offset in minutes east from UTC."""

    def __init__(self, offset, name=None):
        self._offset = timedelta(minutes=offset)
        if name is None:
            name = 'Etc/GMT+%d' % offset
        self.zone = name

    def __str__(self):
        return self.zone

    def __repr__(self):
        return '<FixedOffset "%s" %s>' % (self.zone, self._offset)

    def utcoffset(self, dt):
        return self._offset

    def tzname(self, dt):
        return self.zone

    def dst(self, dt):
        return ZERO


try:
    from pytz import UTC
except ImportError:
    UTC = FixedOffsetTimezone(0, 'UTC')
    """`tzinfo` object for UTC (Universal Time).
    
    :type: `tzinfo`
    """

STDOFFSET = timedelta(seconds = -time.timezone)
if time.daylight:
    DSTOFFSET = timedelta(seconds = -time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET


class LocalTimezone(tzinfo):

    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt):
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, -1)
        stamp = time.mktime(tt)
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0


LOCALTZ = LocalTimezone()
"""`tzinfo` object for local time-zone.

:type: `tzinfo`
"""
