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

from datetime import date, datetime
import re
import time

from babel import __version__ as VERSION

__all__ = ['escape', 'normalize', 'read_po', 'write_po']

POT_HEADER = """\
# SOME DESCRIPTIVE TITLE.
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
"Content-Transfer-Encoding: %%(charset)s\\n"
"Generated-By: Babel %s\\n"

""" % VERSION

PYTHON_FORMAT = re.compile(r'(\%\(([\w]+)\)[diouxXeEfFgGcrs])').search

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
    """Parse a PO file.
    
    This function yields tuples of the form:
    
        ``(message, translation, locations)``
    
    where:
    
     * ``message`` is the original (untranslated) message, or a
       ``(singular, plural)`` tuple for pluralizable messages
     * ``translation`` is the translation of the message, or a tuple of
       translations for pluralizable messages
     * ``locations`` is a sequence of ``(filename, lineno)`` tuples
    
    :param fileobj: the file-like object to read the PO file from
    :return: an iterator over ``(message, translation, location)`` tuples
    :rtype: ``iterator``
    """
    for line in fileobj.readlines():
        line = line.strip()
        if line.startswith('#'):
            continue # TODO: process comments
        else:
            if line.startswith('msgid_plural'):
                msg = line[12:].lstrip()
            elif line.startswith('msgid'):
                msg = line[5:].lstrip()
            elif line.startswith('msgstr'):
                msg = line[6:].lstrip()
                if msg.startswith('['):
                    pass # plural

def write_po(fileobj, messages, project=None, version=None, charset='utf-8',
             no_location=False, omit_header=False):
    r"""Write a ``gettext`` PO (portable object) file to the given file-like
    object.
    
    The `messages` parameter is expected to be an iterable object producing
    tuples of the form:
    
        ``(filename, lineno, funcname, message)``
    
    >>> from StringIO import StringIO
    >>> buf = StringIO()
    >>> write_po(buf, [
    ...     ('main.py', 1, None, u'foo'),
    ...     ('main.py', 3, 'ngettext', (u'bar', u'baz'))
    ... ], omit_header=True)
    
    >>> print buf.getvalue()
    #: main.py:1
    msgid "foo"
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
    msgids = []

    for filename, lineno, funcname, key in messages:
        if key in msgids:
            locations[key].append((filename, lineno))
        else:
            locations[key] = [(filename, lineno)]
            msgids.append(key)

    for msgid in msgids:
        if not no_location:
            for filename, lineno in locations[msgid]:
                fileobj.write('#: %s:%s\n' % (filename, lineno))
        if type(msgid) is tuple:
            assert len(msgid) == 2
            if PYTHON_FORMAT(msgid[0]) or PYTHON_FORMAT(msgid[1]):
                fileobj.write('#, python-format\n')
            fileobj.write('msgid %s\n' % normalize(msgid[0], charset))
            fileobj.write('msgid_plural %s\n' % normalize(msgid[1], charset))
            fileobj.write('msgstr[0] ""\n')
            fileobj.write('msgstr[1] ""\n')
        else:
            if PYTHON_FORMAT(msgid):
                fileobj.write('#, python-format\n')
            fileobj.write('msgid %s\n' % normalize(msgid, charset))
            fileobj.write('msgstr ""\n')
        fileobj.write('\n')
