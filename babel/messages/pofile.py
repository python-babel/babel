# -*- coding: utf-8 -*-
"""
    babel.messages.pofile
    ~~~~~~~~~~~~~~~~~~~~~

    Reading and writing of files in the ``gettext`` PO (portable object)
    format.

    :copyright: (c) 2013-2020 by the Babel Team.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import print_function

import os
import re

from babel._compat import text_type, cmp
from babel.messages.catalog import Catalog, Message
from babel.util import wraptext


def unescape(string):
    r"""Reverse `escape` the given string.

    >>> print(unescape('"Say:\\n  \\"hello, world!\\"\\n"'))
    Say:
      "hello, world!"
    <BLANKLINE>

    :param string: the string to unescape
    """

    def replace_escapes(match):
        m = match.group(1)
        if m == 'n':
            return '\n'
        elif m == 't':
            return '\t'
        elif m == 'r':
            return '\r'
        # m is \ or "
        return m

    return re.compile(r'\\([\\trn"])').sub(replace_escapes, string[1:-1])


def denormalize(string):
    r"""Reverse the normalization done by the `normalize` function.

    >>> print(denormalize(r'''""
    ... "Say:\n"
    ... "  \"hello, world!\"\n"'''))
    Say:
      "hello, world!"
    <BLANKLINE>

    >>> print(denormalize(r'''""
    ... "Say:\n"
    ... "  \"Lorem ipsum dolor sit "
    ... "amet, consectetur adipisicing"
    ... " elit, \"\n"'''))
    Say:
      "Lorem ipsum dolor sit amet, consectetur adipisicing elit, "
    <BLANKLINE>

    :param string: the string to denormalize
    """
    if '\n' in string:
        escaped_lines = string.splitlines()
        if string.startswith('""'):
            escaped_lines = escaped_lines[1:]
        lines = map(unescape, escaped_lines)
        return ''.join(lines)
    else:
        return unescape(string)


class PoFileError(Exception):
    """Exception thrown by PoParser when an invalid po file is encountered."""

    def __init__(self, message, catalog, line, lineno):
        super(PoFileError, self).__init__('{message} on {lineno}'.format(message=message, lineno=lineno))
        self.catalog = catalog
        self.line = line
        self.lineno = lineno


class _NormalizedString(object):

    def __init__(self, *args):
        self._strs = []
        for arg in args:
            self.append(arg)

    def append(self, s):
        self._strs.append(s.strip())

    def denormalize(self):
        return ''.join(map(unescape, self._strs))

    def __nonzero__(self):
        return bool(self._strs)

    __bool__ = __nonzero__

    def __repr__(self):
        return os.linesep.join(self._strs)

    def __cmp__(self, other):
        if not other:
            return 1

        return cmp(text_type(self), text_type(other))

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0


class PoFileParser(object):
    """Support class to  read messages from a ``gettext`` PO (portable object) file
    and add them to a `Catalog`

    See `read_po` for simple cases.
    """

    _keywords = [
        'msgid',
        'msgstr',
        'msgctxt',
        'msgid_plural',
    ]

    def __init__(self, catalog, ignore_obsolete=False, abort_invalid=False):
        self.catalog = catalog
        self.ignore_obsolete = ignore_obsolete
        self.counter = 0
        self.offset = 0
        self.abort_invalid = abort_invalid
        self._reset_message_state()

    def _reset_message_state(self):
        self.messages = []
        self.previous_messages = []
        self.translations = []
        self.locations = []
        self.flags = []
        self.translator_comments = []
        self.extracted_comments = []
        self.context = None
        self.previous_context = None
        self.obsolete = False
        self.previous = False
        self.in_msgid = False
        self.in_msgstr = False
        self.in_msgctxt = False

    def _add_message(self):
        """
        Add a message to the catalog based on the current parser state and
        clear the state ready to process the next message.
        """
        self.translations.sort()
        if len(self.messages) > 1:
            msgid = tuple([m.denormalize() for m in self.messages])
        else:
            msgid = self.messages[0].denormalize()
        if isinstance(msgid, (list, tuple)):
            string = ['' for _ in range(self.catalog.num_plurals)]
            for idx, translation in self.translations:
                if idx >= self.catalog.num_plurals:
                    self._invalid_pofile(u"", self.offset, "msg has more translations than num_plurals of catalog")
                    continue
                string[idx] = translation.denormalize()
            string = tuple(string)
        else:
            string = self.translations[0][1].denormalize()
        if self.context:
            msgctxt = self.context.denormalize()
        else:
            msgctxt = None

        if len(self.previous_messages) > 1:
            previous_msgid = tuple([m.denormalize() for m in self.previous_messages])
        elif len(self.previous_messages) == 1:
            previous_msgid = self.previous_messages[0].denormalize()
        else:
            previous_msgid = ()
        if self.previous_context:
            previous_msgctxt = self.previous_context.denormalize()
        else:
            previous_msgctxt = None
        message = Message(msgid, string, list(self.locations), set(self.flags),
                          self.extracted_comments, self.translator_comments, previous_msgid,
                          previous_msgctxt, self.offset + 1, msgctxt)
        if self.obsolete:
            if not self.ignore_obsolete:
                self.catalog.obsolete[msgid] = message
        else:
            self.catalog[msgid] = message
        self.counter += 1
        self._reset_message_state()

    def _finish_current_message(self):
        if self.messages:
            self._add_message()

    def _process_message_line(self, lineno, line, obsolete=False, previous=False):
        if line.startswith('"'):
            self._process_string_continuation_line(line, lineno, previous)
        else:
            self._process_keyword_line(lineno, line, obsolete, previous)

    def _process_keyword_line(self, lineno, line, obsolete=False, previous=False):

        for keyword in self._keywords:
            try:
                if line.startswith(keyword) and line[len(keyword)] in [' ', '[']:
                    if previous and line.startswith('msgstr'):
                        continue
                    arg = line[len(keyword):]
                    break
            except IndexError:
                self._invalid_pofile(line, lineno, "Keyword must be followed by a string")
        else:
            self._invalid_pofile(line, lineno, "Start of line didn't match any expected keyword.")
            return

        if keyword in ['msgid', 'msgctxt']:
            self._finish_current_message()

        if not previous:
            self.obsolete = obsolete
        self.previous = previous

        # The line that has the msgid is stored as the offset of the msg
        # should this be the msgctxt if it has one?
        if keyword == 'msgid':
            self.offset = lineno

        self.in_msgid = keyword in {'msgid', 'msgid_plural'}
        self.in_msgstr = keyword == 'msgstr' and not previous
        self.in_msgctxt = keyword == 'msgctxt'

        if self.in_msgid:
            if previous:
                self.previous_messages.append(_NormalizedString(arg))
            else:
                self.messages.append(_NormalizedString(arg))

        elif self.in_msgstr:
            if arg.startswith('['):
                idx, msg = arg[1:].split(']', 1)
                self.translations.append([int(idx), _NormalizedString(msg)])
            else:
                self.translations.append([0, _NormalizedString(arg)])

        elif self.in_msgctxt:
            if previous:
                self.previous_context = _NormalizedString(arg)
            else:
                self.context = _NormalizedString(arg)

    def _process_string_continuation_line(self, line, lineno, previous=False):
        if self.previous != previous:
            self._invalid_pofile(line, lineno,
                                 "Got line starting with #| \" but not in previous msgid or previous msgctxt")
            return

        if self.in_msgid:
            if previous:
                s = self.previous_messages[-1]
            else:
                s = self.messages[-1]
        elif self.in_msgstr:
            if previous:
                self._invalid_pofile(line, lineno, "Got line starting with \" in previous msgstr")
                return
            s = self.translations[-1][1]
        elif self.in_msgctxt:
            if previous:
                s = self.previous_context
            else:
                s = self.context
        else:
            self._invalid_pofile(line, lineno, "Got line starting with \" but not in msgid, msgstr or msgctxt")
            return
        s.append(line)

    def _process_comment(self, line, lineno):

        self._finish_current_message()

        original_line = line
        if line[1:].startswith('~'):
            line = '#' + line[2:]

        if line[1:].startswith(':'):
            for location in line[2:].lstrip().split():
                pos = location.rfind(':')
                if pos >= 0:
                    try:
                        lineno = int(location[pos + 1:])
                    except ValueError:
                        continue
                    self.locations.append((location[:pos], lineno))
                else:
                    self.locations.append((location, None))
        elif line[1:].startswith(','):
            for flag in line[2:].split(','):
                self.flags.append(flag.strip())
        elif line[1:].startswith('.'):
            # These are called extracted-comments
            self.extracted_comments.append(line[2:].strip())
        elif line[1:].startswith(' ') or len(line) == 1:
            # These are called translator-comments
            self.translator_comments.append(line[2:].strip())
        elif line[1:].startswith('|'):
            self._process_message_line(lineno, line[2:].strip(), self.obsolete, True)
        else:
            self._invalid_pofile(original_line, lineno, "Unknown comment type")

    def parse(self, fileobj):
        """
        Reads from the file-like object `fileobj` and adds any po file
        units found in it to the `Catalog` supplied to the constructor.
        """

        for lineno, line in enumerate(fileobj):
            if not isinstance(line, text_type):
                line = line.decode(self.catalog.charset)
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                if line[1:].startswith('~'):
                    if line[2:].lstrip().startswith(tuple(self._keywords)) or (
                            line[2:].lstrip().startswith('"') and (self.in_msgid or self.in_msgstr or self.in_msgctxt)
                    ):
                        self._process_message_line(lineno, line[2:].lstrip(), obsolete=True)
                    else:
                        self._process_comment(line, lineno)
                else:
                    self._process_comment(line, lineno)
            else:
                self._process_message_line(lineno, line)

        self._finish_current_message()

        # No actual messages found, but there was some info in comments, from which
        # we'll construct an empty header message
        if not self.counter and (self.flags or self.translator_comments or self.extracted_comments):
            self.messages.append(_NormalizedString(u'""'))
            self.translations.append([0, _NormalizedString(u'""')])
            self._add_message()

    def _invalid_pofile(self, line, lineno, msg):
        assert isinstance(line, text_type)
        if self.abort_invalid:
            raise PoFileError(msg, self.catalog, line, lineno)
        print("WARNING:", msg)
        # `line` is guaranteed to be unicode so u"{}"-interpolating would always
        # succeed, but on Python < 2 if not in a TTY, `sys.stdout.encoding`
        # is `None`, unicode may not be printable so we `repr()` to ASCII.
        print(u"WARNING: Problem on line {0}: {1}".format(lineno + 1, repr(line)))


def read_po(fileobj, locale=None, domain=None, ignore_obsolete=False, charset=None, abort_invalid=False):
    """Read messages from a ``gettext`` PO (portable object) file from the given
    file-like object and return a `Catalog`.

    >>> from datetime import datetime
    >>> from babel._compat import StringIO
    >>> buf = StringIO('''
    ... #: main.py:1
    ... #, fuzzy, python-format
    ... msgid "foo %(name)s"
    ... msgstr "quux %(name)s"
    ...
    ... # A user comment
    ... #. An auto comment
    ... #: main.py:3
    ... msgid "bar"
    ... msgid_plural "baz"
    ... msgstr[0] "bar"
    ... msgstr[1] "baaz"
    ... ''')
    >>> catalog = read_po(buf)
    >>> catalog.revision_date = datetime(2007, 4, 1)

    >>> for message in catalog:
    ...     if message.id:
    ...         print((message.id, message.string))
    ...         print(' ', (message.locations, sorted(list(message.flags))))
    ...         print(' ', (message.translator_comments, message.extracted_comments))
    (u'foo %(name)s', u'quux %(name)s')
      ([(u'main.py', 1)], [u'fuzzy', u'python-format'])
      ([], [])
    ((u'bar', u'baz'), (u'bar', u'baaz'))
      ([(u'main.py', 3)], [])
      ([u'A user comment'], [u'An auto comment'])

    .. versionadded:: 1.0
       Added support for explicit charset argument.

    :param fileobj: the file-like object to read the PO file from
    :param locale: the locale identifier or `Locale` object, or `None`
                   if the catalog is not bound to a locale (which basically
                   means it's a template)
    :param domain: the message domain
    :param ignore_obsolete: whether to ignore obsolete messages in the input
    :param charset: the character set of the catalog.
    :param abort_invalid: abort read if po file is invalid
    """
    catalog = Catalog(locale=locale, domain=domain, charset=charset)
    parser = PoFileParser(catalog, ignore_obsolete, abort_invalid=abort_invalid)
    parser.parse(fileobj)
    return catalog


WORD_SEP = re.compile('('
                      r'\s+|'  # any whitespace
                      r'[^\s\w]*\w+[a-zA-Z]-(?=\w+[a-zA-Z])|'  # hyphenated words
                      r'(?<=[\w\!\"\'\&\.\,\?])-{2,}(?=\w)'  # em-dash
                      ')')


def escape(string):
    r"""Escape the given string so that it can be included in double-quoted
    strings in ``PO`` files.

    >>> escape('''Say:
    ...   "hello, world!"
    ... ''')
    '"Say:\\n  \\"hello, world!\\"\\n"'

    :param string: the string to escape
    """
    return '"%s"' % string.replace('\\', '\\\\') \
        .replace('\t', '\\t') \
        .replace('\r', '\\r') \
        .replace('\n', '\\n') \
        .replace('\"', '\\"')


def normalize(string, prefix='', width=76):
    r"""Convert a string into a format that is appropriate for .po files.

    >>> print(normalize('''Say:
    ...   "hello, world!"
    ... ''', width=None))
    ""
    "Say:\n"
    "  \"hello, world!\"\n"

    >>> print(normalize('''Say:
    ...   "Lorem ipsum dolor sit amet, consectetur adipisicing elit, "
    ... ''', width=32))
    ""
    "Say:\n"
    "  \"Lorem ipsum dolor sit "
    "amet, consectetur adipisicing"
    " elit, \"\n"

    :param string: the string to normalize
    :param prefix: a string that should be prepended to every line
    :param width: the maximum line width; use `None`, 0, or a negative number
                  to completely disable line wrapping
    """
    if width and width > 0:
        prefixlen = len(prefix)
        lines = []
        for line in string.splitlines(True):
            if len(escape(line)) + prefixlen > width:
                chunks = WORD_SEP.split(line)
                chunks.reverse()
                while chunks:
                    buf = []
                    size = 2
                    while chunks:
                        l = len(escape(chunks[-1])) - 2 + prefixlen
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
    return u'""\n' + u'\n'.join([(prefix + escape(line)) for line in lines])


def write_po(fileobj, catalog, width=76, no_location=False, omit_header=False,
             sort_output=False, sort_by_file=False, ignore_obsolete=False,
             include_previous=False, include_lineno=True):
    r"""Write a ``gettext`` PO (portable object) template file for a given
    message catalog to the provided file-like object.

    >>> catalog = Catalog()
    >>> catalog.add(u'foo %(name)s', locations=[('main.py', 1)],
    ...             flags=('fuzzy',))
    <Message...>
    >>> catalog.add((u'bar', u'baz'), locations=[('main.py', 3)])
    <Message...>
    >>> from babel._compat import BytesIO
    >>> buf = BytesIO()
    >>> write_po(buf, catalog, omit_header=True)
    >>> print(buf.getvalue().decode("utf8"))
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
    :param sort_output: whether to sort the messages in the output by msgid
    :param sort_by_file: whether to sort the messages in the output by their
                         locations
    :param ignore_obsolete: whether to ignore obsolete messages and not include
                            them in the output; by default they are included as
                            comments
    :param include_previous: include the old msgid as a comment when
                             updating the catalog
    :param include_lineno: include line number in the location comment
    """

    def _normalize(key, prefix=''):
        return normalize(key, prefix=prefix, width=width)

    def _write(text):
        if isinstance(text, text_type):
            text = text.encode(catalog.charset, 'backslashreplace')
        fileobj.write(text)

    def _write_comment(comment, prefix=''):
        # xgettext always wraps comments even if --no-wrap is passed;
        # provide the same behaviour
        if width and width > 0:
            _width = width
        else:
            _width = 76
        for line in wraptext(comment, _width):
            _write('#%s %s\n' % (prefix, line.strip()))

    def _write_message_and_context(message_context, message_id, message_string, prefix='', previous=False):
        if isinstance(message_id, (list, tuple)):
            if message_context is not None:
                _write('%smsgctxt %s\n' % (prefix,
                                           _normalize(message_context, prefix)))
            if not previous or message_id:
                _write('%smsgid %s\n' % (prefix, _normalize(message_id[0], prefix)))
                _write('%smsgid_plural %s\n' % (
                    prefix, _normalize(message_id[1], prefix)
                ))

            if not previous:
                for idx in range(catalog.num_plurals):
                    try:
                        string = message_string[idx] or ''
                    except IndexError:
                        string = ''
                    _write('%smsgstr[%d] %s\n' % (
                        prefix, idx, _normalize(string, prefix)
                    ))
        else:
            if message_context is not None:
                _write('%smsgctxt %s\n' % (prefix,
                                           _normalize(message_context, prefix)))
            _write('%smsgid %s\n' % (prefix, _normalize(message_id, prefix)))
            if not previous:
                _write('%smsgstr %s\n' % (
                    prefix, _normalize(message_string or '', prefix)
                ))

    def _write_entry(message, obsolete=False):

        for comment in message.translator_comments:
            _write_comment(comment)
        for comment in message.extracted_comments:
            _write_comment(comment, prefix='.')

        if not no_location:
            locs = []

            # sort locations by filename and lineno.
            # if there's no <int> as lineno, use `-1`.
            # if no sorting possible, leave unsorted.
            # (see issue #606)
            try:
                locations = sorted(message.locations,
                                   key=lambda x: (x[0], isinstance(x[1], int) and x[1] or -1))
            except TypeError:  # e.g. "TypeError: unorderable types: NoneType() < int()"
                locations = message.locations

            for filename, lineno in locations:
                if lineno and include_lineno:
                    locs.append(u'%s:%d' % (filename.replace(os.sep, '/'), lineno))
                else:
                    locs.append(u'%s' % filename.replace(os.sep, '/'))
            _write_comment(' '.join(locs), prefix=':')
        if message.flags:
            _write_comment(', '.join(sorted(message.flags)), prefix=',')

        if include_previous:
            _write_message_and_context(message.previous_context, message.previous_id, None, prefix='#| ', previous=True)

        _write_message_and_context(message.context, message.id, message.string, prefix='#~ ' if obsolete else '')

    sort_by = None
    if sort_output:
        sort_by = "message"
    elif sort_by_file:
        sort_by = "location"

    for message in _sort_messages(catalog, sort_by=sort_by):
        if not message.id:  # This is the header "message"
            if omit_header:
                continue
            comment_header = catalog.header_comment
            if width and width > 0:
                lines = []
                for line in comment_header.splitlines():
                    lines += wraptext(line, width=width,
                                      subsequent_indent='# ')
                comment_header = u'\n'.join(lines)
            _write(comment_header + u'\n')

        _write_entry(message)
        _write('\n')

    if not ignore_obsolete:
        for message in _sort_messages(
                catalog.obsolete.values(),
                sort_by=sort_by
        ):
            _write_entry(message, obsolete=True)
            _write('\n')


def _sort_messages(messages, sort_by):
    """
    Sort the given message iterable by the given criteria.

    Always returns a list.

    :param messages: An iterable of Messages.
    :param sort_by: Sort by which criteria? Options are `message` and `location`.
    :return: list[Message]
    """
    messages = list(messages)
    if sort_by == "message":
        messages.sort()
    elif sort_by == "location":
        messages.sort(key=lambda m: m.locations)
    return messages
