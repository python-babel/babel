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

"""Reading and writing of files in the ``gettext`` PO (portable object)
format.

:see: `The Format of PO Files
       <http://www.gnu.org/software/gettext/manual/gettext.html#PO-Files>`_
"""

# TODO: line wrapping
from textwrap import wrap
from datetime import date, datetime
import re
try:
    set
except NameError:
    from sets import Set as set
import time

from babel import __version__ as VERSION

__all__ = ['escape', 'normalize', 'read_po', 'write_po']

POT_HEADER = """\
# Translations Template for %%(project)s.
# Copyright (C) YEAR ORGANIZATION
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
msgid ""
msgstr ""
"Project-Id-Version: %%(project)s %%(version)s\\n"
"POT-Creation-Date: %%(creation_date)s\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=%%(charset)s\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Generated-By: Babel %s\\n"

""" % VERSION

PYTHON_FORMAT = re.compile(r'\%(\([\w]+\))?[diouxXeEfFgGcrs]').search

def escape(string):
    r"""Escape the given string so that it can be included in double-quoted
    strings in ``PO`` files.
    
    >>> escape('''Say:
    ...   "hello, world!"
    ... ''')
    'Say:\\n  \\"hello, world!\\"\\n'
    
    :param string: the string to escape
    :return: the escaped string
    :rtype: `str` or `unicode`
    """
    return string.replace('\\', '\\\\') \
                 .replace('\t', '\\t') \
                 .replace('\r', '\\r') \
                 .replace('\n', '\\n') \
                 .replace('\"', '\\"')

def normalize(string, charset='utf-8'):
    """This converts a string into a format that is appropriate for .po files,
    namely much closer to C style.
    
    :param string: the string to normalize
    :param charset: the encoding to use for `unicode` strings
    :return: the normalized string
    :rtype: `str`
    """
    string = string.encode(charset, 'backslashreplace')
    lines = string.split('\n')
    if len(lines) == 1:
        string = '"' + escape(string) + '"'
    else:
        if not lines[-1]:
            del lines[-1]
            lines[-1] = lines[-1] + '\n'
        for i in range(len(lines)):
            lines[i] = escape(lines[i])
        lineterm = '\\n"\n"'
        string = '""\n"' + lineterm.join(lines) + '"'
    return string

def read_po(fileobj):
    """Read messages from a ``gettext`` PO (portable object) file from the given
    file-like object.
    
    This function yields tuples of the form:
    
        ``(message, translation, locations, flags)``
    
    where:
    
     * ``message`` is the original (untranslated) message, or a
       ``(singular, plural)`` tuple for pluralizable messages
     * ``translation`` is the translation of the message, or a tuple of
       translations for pluralizable messages
     * ``locations`` is a sequence of ``(filename, lineno)`` tuples
     * ``flags`` is a set of strings (for exampe, "fuzzy")
    
    >>> from StringIO import StringIO
    >>> buf = StringIO('''
    ... #: main.py:1
    ... #, fuzzy, python-format
    ... msgid "foo %(name)s"
    ... msgstr ""
    ...
    ... #: main.py:3
    ... msgid "bar"
    ... msgid_plural "baz"
    ... msgstr[0] ""
    ... msgstr[1] ""
    ... ''')
    >>> for message, translation, locations, flags in read_po(buf):
    ...     print (message, translation)
    ...     print ' ', (locations, flags)
    (('foo %(name)s',), ('',))
      ((('main.py', 1),), set(['fuzzy', 'python-format']))
    (('bar', 'baz'), ('', ''))
      ((('main.py', 3),), set([]))
    
    :param fileobj: the file-like object to read the PO file from
    :return: an iterator over ``(message, translation, location)`` tuples
    :rtype: ``iterator``
    """
    messages = []
    translations = []
    locations = []
    flags = []
    in_msgid = in_msgstr = False

    def pack():
        translations.sort()
        retval = (tuple(messages), tuple([t[1] for t in translations]),
                  tuple(locations), set(flags))
        del messages[:]
        del translations[:]
        del locations[:]
        del flags[:]
        return retval

    for line in fileobj.readlines():
        line = line.strip()
        if line.startswith('#'):
            in_msgid = in_msgstr = False
            if messages:
                yield pack()
            if line[1:].startswith(':'):
                for location in line[2:].lstrip().split():
                    filename, lineno = location.split(':', 1)
                    locations.append((filename, int(lineno)))
            elif line[1:].startswith(','):
                for flag in line[2:].lstrip().split(','):
                    flags.append(flag.strip())
        elif line:
            if line.startswith('msgid_plural'):
                in_msgid = True
                msg = line[12:].lstrip()
                messages.append(msg[1:-1])
            elif line.startswith('msgid'):
                in_msgid = True
                if messages:
                    yield pack()
                msg = line[5:].lstrip()
                messages.append(msg[1:-1])
            elif line.startswith('msgstr'):
                in_msgid = False
                in_msgstr = True
                msg = line[6:].lstrip()
                if msg.startswith('['):
                    idx, msg = msg[1:].split(']')
                    translations.append([int(idx), msg.lstrip()[1:-1]])
                else:
                    translations.append([0, msg[1:-1]])
            elif line.startswith('"'):
                if in_msgid:
                    messages[-1] += line.rstrip()[1:-1]
                elif in_msgstr:
                    translations[-1][1] += line.rstrip()[1:-1]

    if messages:
        yield pack()

def write_po(fileobj, messages, project='PROJECT', version='VERSION', width=76,
             charset='utf-8', no_location=False, omit_header=False):
    r"""Write a ``gettext`` PO (portable object) file to the given file-like
    object.
    
    The `messages` parameter is expected to be an iterable object producing
    tuples of the form:
    
        ``(filename, lineno, funcname, message, flags)``
    
    >>> from StringIO import StringIO
    >>> buf = StringIO()
    >>> write_po(buf, [
    ...     ('main.py', 1, None, u'foo %(name)s', ('fuzzy',)),
    ...     ('main.py', 3, 'ngettext', (u'bar', u'baz'), None)
    ... ], omit_header=True)
    
    >>> print buf.getvalue()
    #: main.py:1
    #, fuzzy, python-format
    msgid "foo %(name)s"
    msgstr ""
    <BLANKLINE>
    #: main.py:3
    msgid "bar"
    msgid_plural "baz"
    msgstr[0] ""
    msgstr[1] ""
    <BLANKLINE>
    <BLANKLINE>
    
    :param fileobj: the file-like object to write to
    :param messages: an iterable over the messages
    :param project: the project name
    :param version: the project version
    :param charset: the encoding
    :param no_location: do not emit a location comment for every message
    :param omit_header: do not include the ``msgid ""`` entry at the top of the
                        output
    """
    def _normalize(key):
        return normalize(key, charset=charset)

    if not omit_header:
        fileobj.write(POT_HEADER % {
            'project': project,
            'version': version,
            'creation_date': time.strftime('%Y-%m-%d %H:%M%z'),
            'charset': charset,
        })

    locations = {}
    msgflags = {}
    msgids = []

    for filename, lineno, funcname, key, flags in messages:
        flags = set(flags or [])
        if key in msgids:
            locations[key].append((filename, lineno))
            msgflags[key] |= flags
        else:
            if (isinstance(key, (list, tuple)) and
                    filter(None, [PYTHON_FORMAT(k) for k in key])) or \
                    (isinstance(key, basestring) and PYTHON_FORMAT(key)):
                flags.add('python-format')
            else:
                flags.discard('python-format')
            locations[key] = [(filename, lineno)]
            msgflags[key] = flags
            msgids.append(key)

    for msgid in msgids:
        if not no_location:
            locs = [
                u' %s:%s' % (fname, lineno) for
                fname, lineno in locations[msgid]
            ]
            if width > 0:
                wrapped = wrap(u''.join(locs), width, break_long_words=False)
            else:
                wrapped = locs
            for line in wrapped:
                fileobj.write(u'#: %s\n' % line.strip())
        flags = msgflags[msgid]
        if flags:
            fileobj.write('#%s\n' % ', '.join([''] + list(flags)))
        if type(msgid) is tuple:
            assert len(msgid) == 2
            if width > 0:
                wrapped = wrap(msgid[0], width, break_long_words=False)
            else:
                wrapped = [msgid[0]]
            if len(wrapped) == 1:
                fileobj.write('msgid ')
            else:
                fileobj.write('msgid ""\n')
            for line in wrapped:
                fileobj.write('%s\n' % normalize(line, charset))
            if width > 0:
                wrapped = wrap(msgid[1], width, break_long_words=False)
            else:
                wrapped = [msgid[1]]
            if len(wrapped) == 1:
                fileobj.write('msgid_plural ')
            else:
                fileobj.write('msgid_plural ""\n')
            for line in wrapped:
                fileobj.write('%s\n' % normalize(line, charset))
            fileobj.write('msgstr[0] ""\n')
            fileobj.write('msgstr[1] ""\n')
        else:
            if width > 0:
                wrapped = wrap(msgid, width, break_long_words=False)
            else:
                wrapped = [msgid]
            if len(wrapped) == 1:
                fileobj.write('msgid ')
            else:
                fileobj.write('msgid ""\n')
            for line in wrapped:
                fileobj.write('%s\n' % normalize(line, charset))
            fileobj.write('msgstr ""\n')
        fileobj.write('\n')
