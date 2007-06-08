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
import textwrap
import time

from babel import __version__ as VERSION

__all__ = ['escape', 'normalize', 'read_po', 'write_po', 'write_pot']

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

POT_HEADER = """\
# Translations Template for %%(project)s.
# Copyright (C) %%(year)s ORGANIZATION
# This file is distributed under the same license as the
# %%(project)s project.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
#, fuzzy
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

    if len(lines) == 1:
        return escape(string)

    # Remove empty trailing line
    if not lines[-1]:
        del lines[-1]
        lines[-1] += '\n'
    return u'""\n' + u'\n'.join([escape(l) for l in lines])

def write_pot(fileobj, messages, project='PROJECT', version='VERSION', width=76,
             charset='utf-8', no_location=False, omit_header=False):
    r"""Write a ``gettext`` PO (portable object) template file to the given
    file-like object.
    
    The `messages` parameter is expected to be an iterable object producing
    tuples of the form:
    
        ``(filename, lineno, funcname, message, flags)``
    
    >>> from StringIO import StringIO
    >>> buf = StringIO()
    >>> write_pot(buf, [
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
    :param width: the maximum line width for the generated output; use `None`,
                  0, or a negative number to completely disable line wrapping
    :param charset: the encoding
    :param no_location: do not emit a location comment for every message
    :param omit_header: do not include the ``msgid ""`` entry at the top of the
                        output
    """
    def _normalize(key):
        return normalize(key, width=width).encode(charset, 'backslashreplace')

    def _write(text):
        if isinstance(text, unicode):
            text = text.encode(charset)
        fileobj.write(text)

    if not omit_header:
        _write(POT_HEADER % {
            'year': time.strftime('%Y'),
            'project': project,
            'version': version,
            'creation_date': time.strftime('%Y-%m-%d %H:%M%z'),
            'charset': charset,
        })

    locations = {}
    msgflags = {}
    msgids = []
    plurals = {}

    for filename, lineno, funcname, key, flags in messages:
        flags = set(flags or [])
        if isinstance(key, (list, tuple)):
            assert len(key) == 2
            plurals[key[0]] = key[1]
            key = key[0]
        if key in msgids:
            locations[key].append((filename, lineno))
            msgflags[key] |= flags
        else:
            if PYTHON_FORMAT(key):
                flags.add('python-format')
            else:
                flags.discard('python-format')              
        
            locations[key] = [(filename, lineno)]
            msgflags[key] = flags
            msgids.append(key)

    for msgid in msgids:
        if not no_location:
            locs = u' '.join([u'%s:%d' % item for item in locations[msgid]])
            if width and width > 0:
                locs = textwrap.wrap(locs, width, break_long_words=False)
            for line in locs:
                _write('#: %s\n' % line.strip())
        flags = msgflags[msgid]
        if flags:
            _write('#%s\n' % ', '.join([''] + list(flags)))

        if plurals.has_key(msgid):
            _write('msgid %s\n' % _normalize(msgid))
            _write('msgid_plural %s\n' % _normalize(plurals[msgid]))
            _write('msgstr[0] ""\n')
            _write('msgstr[1] ""\n')
        else:
            _write('msgid %s\n' % _normalize(msgid))
            _write('msgstr ""\n')
        _write('\n')

def write_po(fileobj, input_fileobj, language, country=None, project='PROJECT',
             version='VERSION', first_author=None, first_author_email=None,
             plurals=('INTEGER', 'EXPRESSION')):
    r"""Write a ``gettext`` PO (portable object) file to the given file-like 
    object, from the given input PO template file.
    
    >>> from StringIO import StringIO
    >>> inbuf = StringIO(r'''# Translations Template for FooBar.
    ... # Copyright (C) 2007 ORGANIZATION
    ... # This file is distributed under the same license as the
    ... # FooBar project.
    ... # FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
    ... #
    ... #, fuzzy
    ... msgid ""
    ... msgstr ""
    ... "Project-Id-Version: FooBar 0.1\n"
    ... "POT-Creation-Date: 2007-06-07 22:54+0100\n"
    ... "PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
    ... "Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
    ... "Language-Team: LANGUAGE <LL@li.org>\n"
    ... "MIME-Version: 1.0\n"
    ... "Content-Type: text/plain; charset=utf-8\n"
    ... "Content-Transfer-Encoding: 8bit\n"
    ... "Generated-By: Babel 0.1dev-r50\n"
    ...
    ... #: base.py:83 templates/index.html:9
    ... #: templates/index2.html:9
    ... msgid "Home"
    ... msgstr ""
    ...
    ... #: base.py:84 templates/index.html:9
    ... msgid "Accounts"
    ... msgstr ""
    ... ''')
    >>> outbuf = StringIO()
    >>> write_po(outbuf, inbuf, 'English', project='FooBar',
    ...          version='0.1', first_author='A Name', 
    ...          first_author_email='user@domain.tld',
    ...          plurals=(2, '(n != 1)'))
    >>> print outbuf.getvalue() # doctest: +ELLIPSIS
    # English Translations for FooBar
    # Copyright (C) 2007 ORGANIZATION
    # This file is distributed under the same license as the
    # FooBar project.
    # A Name <user@domain.tld>, ...
    #
    #, fuzzy
    msgid ""
    msgstr ""
    "Project-Id-Version: FooBar 0.1\n"
    "POT-Creation-Date: 2007-06-07 22:54+0100\n"
    "PO-Revision-Date: ...\n"
    "Last-Translator: A Name <user@domain.tld>\n"
    "Language-Team: LANGUAGE <LL@li.org>\n"
    "MIME-Version: 1.0\n"
    "Content-Type: text/plain; charset=utf-8\n"
    "Content-Transfer-Encoding: 8bit\n"
    "Plural-Forms: nplurals=2; plural=(n != 1);\n"
    "Generated-By: Babel ...\n"
    <BLANKLINE>
    #: base.py:83 templates/index.html:9
    #: templates/index2.html:9
    msgid "Home"
    msgstr ""
    <BLANKLINE>
    #: base.py:84 templates/index.html:9
    msgid "Accounts"
    msgstr ""
    <BLANKLINE>
    >>>
    """
    
    _first_author = ''
    if first_author:
        _first_author += first_author
    if first_author_email:
        _first_author += ' <%s>' % first_author_email

    inlines = input_fileobj.readlines()
    outlines = []
    in_header = True
    for index in range(len(inlines)):
        if in_header:
            if '# Translations Template' in inlines[index]:
                if country:
                    line = '# %s (%s) Translations for %%s\n' % \
                                                            (language, country)
                else:
                    line = '# %s Translations for %%s\n' % language
                outlines.append(line % project)
            elif '# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.' in inlines[index]:
                if _first_author:
                    outlines.append(
                        '# %s, %s\n' % (_first_author, time.strftime('%Y'))
                    )
                else:
                    outlines.append(inlines[index])
            elif '"PO-Revision-Date:' in inlines[index]:
                outlines.append(
                    '"PO-Revision-Date: %s\\n"\n' % \
                    time.strftime('%Y-%m-%d %H:%M%z')
                )
            elif '"Last-Translator:' in inlines[index]:
                if _first_author:
                    outlines.append(
                        '"Last-Translator: %s\\n"\n' % _first_author
                    )
                else:
                    outlines.append(inlines[index])
            elif '"Content-Transfer-Encoding:' in inlines[index]:
                outlines.append(inlines[index])
                if '"Plural-Forms:' not in inlines[index+1]:
                    outlines.append(
                        '"Plural-Forms: nplurals=%s; plural=%s;\\n"\n' % plurals
                    )
            elif inlines[index].endswith('\\n"\n') and \
                 inlines[index+1] == '\n':
                in_header = False
                outlines.append(inlines[index])
            else:
                outlines.append(inlines[index])
        else:
            outlines.extend(inlines[index:])
            break
    fileobj.writelines(outlines)
