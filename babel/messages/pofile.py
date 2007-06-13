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

from datetime import date, datetime
import re
try:
    set
except NameError:
    from sets import Set as set
from textwrap import wrap

from babel import __version__ as VERSION
from babel.messages.catalog import Catalog
from babel.util import LOCALTZ

__all__ = ['escape', 'normalize', 'read_po', 'write_po']

def read_po(fileobj):
    """Read messages from a ``gettext`` PO (portable object) file from the given
    file-like object and return a `Catalog`.
    
    >>> from StringIO import StringIO
    >>> buf = StringIO('''# Translations template for PROJECT.
    ... # Copyright (C) YEAR COPYRIGHT HOLDER
    ... # This file is distributed under the same license as the PROJECT project.
    ... # FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
    ... #
    ... 
    ... #: main.py:1
    ... #, fuzzy, python-format
    ... msgid "foo %(name)s"
    ... msgstr ""
    ...
    ... # A user comment
    ... #. An auto comment
    ... #: main.py:3
    ... msgid "bar"
    ... msgid_plural "baz"
    ... msgstr[0] ""
    ... msgstr[1] ""
    ... ''')
    >>> catalog = read_po(buf)
    >>> catalog.revision_date = datetime(2007, 04, 01)
    
    >>> print catalog.header_comment
    # Translations template for PROJECT.
    # Copyright (C) 2007 ORGANIZATION
    # This file is distributed under the same license as the PROJECT project.
    # FIRST AUTHOR <EMAIL@ADDRESS>, 2007.
    
    >>> for message in catalog:
    ...     if message.id:
    ...         print (message.id, message.string)
    ...         print ' ', (message.locations, message.flags, message.comments)
    ('foo %(name)s', '')
      ([('main.py', 1)], set(['fuzzy', 'python-format']), [])
    (('bar', 'baz'), ('', ''))
      ([('main.py', 3)], set([]), ['A user comment', 'An auto comment'])
    
    :param fileobj: the file-like object to read the PO file from
    :return: an iterator over ``(message, translation, location)`` tuples
    :rtype: ``iterator``
    """
    catalog = Catalog()

    messages = []
    translations = []
    locations = []
    flags = []
    comments = []
    in_msgid = in_msgstr = False
    in_header = True
    header_lines = []

    def _add_message():
        translations.sort()
        if len(messages) > 1:
            msgid = tuple(messages)
        else:
            msgid = messages[0]
        if len(translations) > 1:
            string = tuple([t[1] for t in translations])
        else:
            string = translations[0][1]
        catalog.add(msgid, string, list(locations), set(flags), list(comments))
        del messages[:]; del translations[:]; del locations[:];
        del flags[:]; del comments[:]

    for line in fileobj.readlines():
        line = line.strip()
        if line.startswith('#'):
            if in_header and line[1:].startswith(' '):
                header_lines.append(line)
            else:
                in_header = in_msgid = in_msgstr = False
                if messages:
                    _add_message()
                if line[1:].startswith(':'):
                    for location in line[2:].lstrip().split():
                        filename, lineno = location.split(':', 1)
                        locations.append((filename, int(lineno)))
                elif line[1:].startswith(','):
                    for flag in line[2:].lstrip().split(','):
                        flags.append(flag.strip())
                elif line[1:].startswith('.'):
                    # These are called auto-comments
                    comment = line[2:].strip()
                    if comment:
                        # Just check that we're not adding empty comments
                        comments.append(comment)
                elif line[1:].startswith(' '):
                    # These are called user comments
                    comment = line[1:].strip()
                    if comment:
                        # Just check that we're not adding empty comments
                        comments.append(comment)
        else:
            in_header = False
            if line.startswith('msgid_plural'):
                in_msgid = True
                msg = line[12:].lstrip()
                messages.append(msg[1:-1])
            elif line.startswith('msgid'):
                in_msgid = True
                if messages:
                    _add_message()
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

    catalog.header_comment = '\n'.join(header_lines)
    if messages:
        _add_message()
    return catalog

WORD_SEP = re.compile('('
    r'\s+|'                                 # any whitespace
    r'[^\s\w]*\w+[a-zA-Z]-(?=\w+[a-zA-Z])|' # hyphenated words
    r'(?<=[\w\!\"\'\&\.\,\?])-{2,}(?=\w)'   # em-dash
')')

def escape(string):
    r"""Escape the given string so that it can be included in double-quoted
    strings in ``PO`` files.
    
    >>> escape('''Say:
    ...   "hello, world!"
    ... ''')
    '"Say:\\n  \\"hello, world!\\"\\n"'
    
    :param string: the string to escape
    :return: the escaped string
    :rtype: `str` or `unicode`
    """
    return '"%s"' % string.replace('\\', '\\\\') \
                          .replace('\t', '\\t') \
                          .replace('\r', '\\r') \
                          .replace('\n', '\\n') \
                          .replace('\"', '\\"')

def normalize(string, width=76):
    r"""This converts a string into a format that is appropriate for .po files.
    
    >>> print normalize('''Say:
    ...   "hello, world!"
    ... ''', width=None)
    ""
    "Say:\n"
    "  \"hello, world!\"\n"
    
    >>> print normalize('''Say:
    ...   "Lorem ipsum dolor sit amet, consectetur adipisicing elit, "
    ... ''', width=32)
    ""
    "Say:\n"
    "  \"Lorem ipsum dolor sit "
    "amet, consectetur adipisicing"
    " elit, \"\n"
    
    :param string: the string to normalize
    :param width: the maximum line width; use `None`, 0, or a negative number
                  to completely disable line wrapping
    :return: the normalized string
    :rtype: `unicode`
    """
    if width and width > 0:
        lines = []
        for idx, line in enumerate(string.splitlines(True)):
            if len(escape(line)) > width:
                chunks = WORD_SEP.split(line)
                chunks.reverse()
                while chunks:
                    buf = []
                    size = 2
                    while chunks:
                        l = len(escape(chunks[-1])) - 2
                        if size + l < width:
                            buf.append(chunks.pop())
                            size += l
                        else:
                            if not buf:
                                # handle long chunks by putting them on a
                                # separate line
                                buf.append(chunks.pop())
                            break
                    lines.append(u''.join(buf))
            else:
                lines.append(line)
    else:
        lines = string.splitlines(True)

    if len(lines) <= 1:
        return escape(string)

    # Remove empty trailing line
    if lines and not lines[-1]:
        del lines[-1]
        lines[-1] += '\n'
    return u'""\n' + u'\n'.join([escape(l) for l in lines])

def write_po(fileobj, catalog, width=76, no_location=False, omit_header=False,
             sort_output=False, sort_by_file=False):
    r"""Write a ``gettext`` PO (portable object) template file for a given
    message catalog to the provided file-like object.
    
    >>> catalog = Catalog()
    >>> catalog.add(u'foo %(name)s', locations=[('main.py', 1)],
    ...             flags=('fuzzy',))
    >>> catalog.add((u'bar', u'baz'), locations=[('main.py', 3)])
    >>> from StringIO import StringIO
    >>> buf = StringIO()
    >>> write_po(buf, catalog, omit_header=True)
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
    :param catalog: the `Catalog` instance
    :param width: the maximum line width for the generated output; use `None`,
                  0, or a negative number to completely disable line wrapping
    :param no_location: do not emit a location comment for every message
    :param omit_header: do not include the ``msgid ""`` entry at the top of the
                        output
    """
    def _normalize(key):
        return normalize(key, width=width).encode(catalog.charset,
                                                  'backslashreplace')

    def _write(text):
        if isinstance(text, unicode):
            text = text.encode(catalog.charset)
        fileobj.write(text)

    messages = list(catalog)
    if sort_output:
        messages.sort(lambda x,y: cmp(x.id, y.id))
    elif sort_by_file:
        messages.sort(lambda x,y: cmp(x.locations, y.locations))

    for message in messages:
        if not message.id: # This is the header "message"
            if omit_header:
                continue
            comment_header = catalog.header_comment
            if width and width > 0:
                lines = []
                for line in comment_header.splitlines():
                    lines += wrap(line, width=width, subsequent_indent='# ',
                                  break_long_words=False)
                comment_header = u'\n'.join(lines) + u'\n'
            _write(comment_header)

        if message.comments:
            for comment in message.comments:
                for line in wrap(comment, width, break_long_words=False):
                    _write('#. %s\n' % line.strip())

        if not no_location:
            locs = u' '.join([u'%s:%d' % item for item in message.locations])
            if width and width > 0:
                locs = wrap(locs, width, break_long_words=False)
            for line in locs:
                _write('#: %s\n' % line.strip())
        if message.flags:
            _write('#%s\n' % ', '.join([''] + list(message.flags)))

        if isinstance(message.id, (list, tuple)):
            _write('msgid %s\n' % _normalize(message.id[0]))
            _write('msgid_plural %s\n' % _normalize(message.id[1]))
            for i, string in enumerate(message.string):
                _write('msgstr[%d] %s\n' % (i, _normalize(message.string[i])))
        else:
            _write('msgid %s\n' % _normalize(message.id))
            _write('msgstr %s\n' % _normalize(message.string or ''))
        _write('\n')
