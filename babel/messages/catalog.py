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

"""Data structures for message catalogs."""

from cgi import parse_header
from datetime import datetime
from difflib import get_close_matches
from email import message_from_string
import re
try:
    set
except NameError:
    from sets import Set as set
import time

from babel import __version__ as VERSION
from babel.core import Locale
from babel.dates import format_datetime
from babel.messages.plurals import PLURALS
from babel.util import odict, LOCALTZ, UTC, FixedOffsetTimezone

__all__ = ['Message', 'Catalog']
__docformat__ = 'restructuredtext en'

PYTHON_FORMAT = re.compile(r'\%(\([\w]+\))?[diouxXeEfFgGcrs]').search


class Message(object):
    """Representation of a single message in a catalog."""

    def __init__(self, id, string=u'', locations=(), flags=(), auto_comments=(),
                 user_comments=()):
        """Create the message object.
        
        :param id: the message ID, or a ``(singular, plural)`` tuple for
                   pluralizable messages
        :param string: the translated message string, or a
                       ``(singular, plural)`` tuple for pluralizable messages
        :param locations: a sequence of ``(filenname, lineno)`` tuples
        :param flags: a set or sequence of flags
        :param auto_comments: a sequence of automatic comments for the message
        :param user_comments: a sequence of user comments for the message
        """
        self.id = id #: The message ID
        if not string and self.pluralizable:
            string = (u'', u'')
        self.string = string #: The message translation
        self.locations = list(locations)
        self.flags = set(flags)
        if id and self.python_format:
            self.flags.add('python-format')
        else:
            self.flags.discard('python-format')
        self.auto_comments = list(auto_comments)
        self.user_comments = list(user_comments)

    def __repr__(self):
        return '<%s %r (Flags: %r)>' % (type(self).__name__, self.id,
                                       ', '.join([flag for flag in self.flags]))

    def fuzzy(self):
        return 'fuzzy' in self.flags
    fuzzy = property(fuzzy, doc="""\
        Whether the translation is fuzzy.
        
        >>> Message('foo').fuzzy
        False
        >>> msg = Message('foo', 'foo', flags=['fuzzy'])
        >>> msg.fuzzy
        True
        >>> msg
        <Message 'foo' (Flags: 'fuzzy')>
        
        :type:  `bool`
        """)

    def pluralizable(self):
        return isinstance(self.id, (list, tuple))
    pluralizable = property(pluralizable, doc="""\
        Whether the message is plurizable.
        
        >>> Message('foo').pluralizable
        False
        >>> Message(('foo', 'bar')).pluralizable
        True
        
        :type:  `bool`
        """)

    def python_format(self):
        ids = self.id
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        return bool(filter(None, [PYTHON_FORMAT(id) for id in ids]))
    python_format = property(python_format, doc="""\
        Whether the message contains Python-style parameters.
        
        >>> Message('foo %(name)s bar').python_format
        True
        >>> Message(('foo %(name)s', 'foo %(name)s')).python_format
        True
        
        :type:  `bool`
        """)


DEFAULT_HEADER = u"""\
# Translations template for PROJECT.
# Copyright (C) YEAR ORGANIZATION
# This file is distributed under the same license as the PROJECT project.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#"""

class Catalog(object):
    """Representation of a message catalog."""

    def __init__(self, locale=None, domain=None, header_comment=DEFAULT_HEADER,
                 project=None, version=None, copyright_holder=None,
                 msgid_bugs_address=None, creation_date=None,
                 revision_date=None, last_translator=None, charset='utf-8',
                 fuzzy=True):
        """Initialize the catalog object.
        
        :param locale: the locale identifier or `Locale` object, or `None`
                       if the catalog is not bound to a locale (which basically
                       means it's a template)
        :param domain: the message domain
        :param header_comment: the header comment as string, or `None` for the
                               default header
        :param project: the project's name
        :param version: the project's version
        :param copyright_holder: the copyright holder of the catalog
        :param msgid_bugs_address: the email address or URL to submit bug
                                   reports to
        :param creation_date: the date the catalog was created
        :param revision_date: the date the catalog was revised
        :param last_translator: the name and email of the last translator
        :param charset: the encoding to use in the output
        :param fuzzy: the fuzzy bit on the catalog header
        """
        self.domain = domain #: The message domain
        if locale:
            locale = Locale.parse(locale)
        self.locale = locale #: The locale or `None`
        self._header_comment = header_comment
        self._messages = odict()

        self.project = project or 'PROJECT' #: The project name
        self.version = version or 'VERSION' #: The project version
        self.copyright_holder = copyright_holder or 'ORGANIZATION'
        self.msgid_bugs_address = msgid_bugs_address or 'EMAIL@ADDRESS'

        self.last_translator = last_translator or 'FULL NAME <EMAIL@ADDRESS>'
        """Name and email address of the last translator."""

        self.charset = charset or 'utf-8'

        if creation_date is None:
            creation_date = datetime.now(LOCALTZ)
        elif isinstance(creation_date, datetime) and not creation_date.tzinfo:
            creation_date = creation_date.replace(tzinfo=LOCALTZ)
        self.creation_date = creation_date #: Creation date of the template
        if revision_date is None:
            revision_date = datetime.now(LOCALTZ)
        elif isinstance(revision_date, datetime) and not revision_date.tzinfo:
            revision_date = revision_date.replace(tzinfo=LOCALTZ)
        self.revision_date = revision_date #: Last revision date of the catalog
        self.fuzzy = fuzzy #: Catalog header fuzzy bit (`True` or `False`)

        self.obsolete = odict() #: Dictionary of obsolete messages

    def _get_header_comment(self):
        comment = self._header_comment
        comment = comment.replace('PROJECT', self.project) \
                         .replace('VERSION', self.version) \
                         .replace('YEAR', self.revision_date.strftime('%Y')) \
                         .replace('ORGANIZATION', self.copyright_holder)
        if self.locale:
            comment = comment.replace('Translations template', '%s translations'
                                      % self.locale.english_name)
        return comment

    def _set_header_comment(self, string):
        self._header_comment = string

    header_comment = property(_get_header_comment, _set_header_comment, doc="""\
    The header comment for the catalog.
    
    >>> catalog = Catalog(project='Foobar', version='1.0',
    ...                   copyright_holder='Foo Company')
    >>> print catalog.header_comment
    # Translations template for Foobar.
    # Copyright (C) 2007 Foo Company
    # This file is distributed under the same license as the Foobar project.
    # FIRST AUTHOR <EMAIL@ADDRESS>, 2007.
    #
    
    The header can also be set from a string. Any known upper-case variables
    will be replaced when the header is retrieved again:
    
    >>> catalog = Catalog(project='Foobar', version='1.0',
    ...                   copyright_holder='Foo Company')
    >>> catalog.header_comment = '''\\
    ... # The POT for my really cool PROJECT project.
    ... # Copyright (C) 1990-2003 ORGANIZATION
    ... # This file is distributed under the same license as the PROJECT
    ... # project.
    ... #'''
    >>> print catalog.header_comment
    # The POT for my really cool Foobar project.
    # Copyright (C) 1990-2003 Foo Company
    # This file is distributed under the same license as the Foobar
    # project.
    #

    :type: `unicode`
    """)

    def _get_mime_headers(self):
        headers = []
        headers.append(('Project-Id-Version',
                        '%s %s' % (self.project, self.version)))
        headers.append(('Report-Msgid-Bugs-To', self.msgid_bugs_address))
        headers.append(('POT-Creation-Date',
                        format_datetime(self.creation_date, 'yyyy-MM-dd HH:mmZ',
                                        locale='en')))
        if self.locale is None:
            headers.append(('PO-Revision-Date', 'YEAR-MO-DA HO:MI+ZONE'))
            headers.append(('Last-Translator', 'FULL NAME <EMAIL@ADDRESS>'))
            headers.append(('Language-Team', 'LANGUAGE <LL@li.org>'))
        else:
            headers.append(('PO-Revision-Date',
                            format_datetime(self.revision_date,
                                            'yyyy-MM-dd HH:mmZ', locale='en')))
            headers.append(('Last-Translator', self.last_translator))
            headers.append(('Language-Team', '%s <LL@li.org>' % self.locale))
            headers.append(('Plural-Forms', self.plural_forms))
        headers.append(('MIME-Version', '1.0'))
        headers.append(('Content-Type',
                        'text/plain; charset=%s' % self.charset))
        headers.append(('Content-Transfer-Encoding', '8bit'))
        headers.append(('Generated-By', 'Babel %s\n' % VERSION))
        return headers

    def _set_mime_headers(self, headers):
        for name, value in headers:
            name = name.lower()
            if name == 'project-id-version':
                parts = value.split(' ')
                self.project = ' '.join(parts[:-1])
                self.version = parts[-1]
            elif name == 'report-msgid-bugs-to':
                self.msgid_bugs_address = value
            elif name == 'last-translator':
                self.last_translator = value
            elif name == 'pot-creation-date':
                # FIXME: this should use dates.parse_datetime as soon as that
                #        is ready
                value, tzoffset, _ = re.split('[+-](\d{4})$', value, 1)
                tt = time.strptime(value, '%Y-%m-%d %H:%M')
                ts = time.mktime(tt)
                tzoffset = FixedOffsetTimezone(int(tzoffset[:2]) * 60 +
                                               int(tzoffset[2:]))
                dt = datetime.fromtimestamp(ts)
                self.creation_date = dt.replace(tzinfo=tzoffset)
            elif name == 'content-type':
                mimetype, params = parse_header(value)
                if 'charset' in params:
                    self.charset = params['charset'].lower()

    mime_headers = property(_get_mime_headers, _set_mime_headers, doc="""\
    The MIME headers of the catalog, used for the special ``msgid ""`` entry.
    
    The behavior of this property changes slightly depending on whether a locale
    is set or not, the latter indicating that the catalog is actually a template
    for actual translations.
    
    Here's an example of the output for such a catalog template:
    
    >>> created = datetime(1990, 4, 1, 15, 30, tzinfo=UTC)
    >>> catalog = Catalog(project='Foobar', version='1.0',
    ...                   creation_date=created)
    >>> for name, value in catalog.mime_headers:
    ...     print '%s: %s' % (name, value)
    Project-Id-Version: Foobar 1.0
    Report-Msgid-Bugs-To: EMAIL@ADDRESS
    POT-Creation-Date: 1990-04-01 15:30+0000
    PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
    Last-Translator: FULL NAME <EMAIL@ADDRESS>
    Language-Team: LANGUAGE <LL@li.org>
    MIME-Version: 1.0
    Content-Type: text/plain; charset=utf-8
    Content-Transfer-Encoding: 8bit
    Generated-By: Babel ...
    
    And here's an example of the output when the locale is set:
    
    >>> revised = datetime(1990, 8, 3, 12, 0, tzinfo=UTC)
    >>> catalog = Catalog(locale='de_DE', project='Foobar', version='1.0',
    ...                   creation_date=created, revision_date=revised,
    ...                   last_translator='John Doe <jd@example.com>')
    >>> for name, value in catalog.mime_headers:
    ...     print '%s: %s' % (name, value)
    Project-Id-Version: Foobar 1.0
    Report-Msgid-Bugs-To: EMAIL@ADDRESS
    POT-Creation-Date: 1990-04-01 15:30+0000
    PO-Revision-Date: 1990-08-03 12:00+0000
    Last-Translator: John Doe <jd@example.com>
    Language-Team: de_DE <LL@li.org>
    Plural-Forms: nplurals=2; plural=(n != 1)
    MIME-Version: 1.0
    Content-Type: text/plain; charset=utf-8
    Content-Transfer-Encoding: 8bit
    Generated-By: Babel ...
    
    :type: `list`
    """)

    def num_plurals(self):
        num = 2
        if self.locale:
            if str(self.locale) in PLURALS:
                num = PLURALS[str(self.locale)][0]
            elif self.locale.language in PLURALS:
                num = PLURALS[self.locale.language][0]
        return num
    num_plurals = property(num_plurals, doc="""\
    The number of plurals used by the locale.
    
    >>> Catalog(locale='en').num_plurals
    2
    >>> Catalog(locale='cs_CZ').num_plurals
    3
    
    :type: `int`
    """)

    def plural_forms(self):
        num, expr = ('INTEGER', 'EXPRESSION')
        if self.locale:
            if str(self.locale) in PLURALS:
                num, expr = PLURALS[str(self.locale)]
            elif self.locale.language in PLURALS:
                num, expr = PLURALS[self.locale.language]
        return 'nplurals=%s; plural=%s' % (num, expr)
    plural_forms = property(plural_forms, doc="""\
    Return the plural forms declaration for the locale.
    
    >>> Catalog(locale='en').plural_forms
    'nplurals=2; plural=(n != 1)'
    >>> Catalog(locale='pt_BR').plural_forms
    'nplurals=2; plural=(n > 1)'
    
    :type: `str`
    """)

    def __contains__(self, id):
        """Return whether the catalog has a message with the specified ID."""
        return self._key_for(id) in self._messages

    def __len__(self):
        """The number of messages in the catalog.
        
        This does not include the special ``msgid ""`` entry.
        """
        return len(self._messages)

    def __iter__(self):
        """Iterates through all the entries in the catalog, in the order they
        were added, yielding a `Message` object for every entry.
        
        :rtype: ``iterator``
        """
        buf = []
        for name, value in self.mime_headers:
            buf.append('%s: %s' % (name, value))
        if self.fuzzy:
            flags = set(['fuzzy'])
        else:
            flags = set()
        yield Message('', '\n'.join(buf), flags=flags)
        for key in self._messages:
            yield self._messages[key]

    def __repr__(self):
        locale = ''
        if self.locale:
            locale = ' %s' % self.locale
        return '<%s %r%s>' % (type(self).__name__, self.domain, locale)

    def __delitem__(self, id):
        """Delete the message with the specified ID."""
        key = self._key_for(id)
        if key in self._messages:
            del self._messages[key]

    def __getitem__(self, id):
        """Return the message with the specified ID.
        
        :param id: the message ID
        :return: the message with the specified ID, or `None` if no such message
                 is in the catalog
        :rtype: `Message`
        """
        return self._messages.get(self._key_for(id))

    def __setitem__(self, id, message):
        """Add or update the message with the specified ID.
        
        >>> catalog = Catalog()
        >>> catalog[u'foo'] = Message(u'foo')
        >>> catalog[u'foo']
        <Message u'foo' (Flags: '')>
        
        If a message with that ID is already in the catalog, it is updated
        to include the locations and flags of the new message.
        
        >>> catalog = Catalog()
        >>> catalog[u'foo'] = Message(u'foo', locations=[('main.py', 1)])
        >>> catalog[u'foo'].locations
        [('main.py', 1)]
        >>> catalog[u'foo'] = Message(u'foo', locations=[('utils.py', 5)])
        >>> catalog[u'foo'].locations
        [('main.py', 1), ('utils.py', 5)]
        
        :param id: the message ID
        :param message: the `Message` object
        """
        assert isinstance(message, Message), 'expected a Message object'
        key = self._key_for(id)
        current = self._messages.get(key)
        if current:
            if message.pluralizable and not current.pluralizable:
                # The new message adds pluralization
                current.id = message.id
                current.string = message.string
            current.locations.extend(message.locations)
            current.auto_comments.extend(message.auto_comments)
            current.user_comments.extend(message.user_comments)
            current.flags |= message.flags
            message = current
        elif id == '':
            # special treatment for the header message
            headers = message_from_string(message.string.encode(self.charset))
            self.mime_headers = headers.items()
            self.header_comment = '\n'.join(['# %s' % comment for comment
                                             in message.user_comments])
        else:
            if isinstance(id, (list, tuple)):
                assert isinstance(message.string, (list, tuple))
            self._messages[key] = message

    def add(self, id, string=None, locations=(), flags=(), auto_comments=(),
            user_comments=()):
        """Add or update the message with the specified ID.
        
        >>> catalog = Catalog()
        >>> catalog.add(u'foo')
        >>> catalog[u'foo']
        <Message u'foo' (Flags: '')>
        
        This method simply constructs a `Message` object with the given
        arguments and invokes `__setitem__` with that object.
        
        :param id: the message ID, or a ``(singular, plural)`` tuple for
                   pluralizable messages
        :param string: the translated message string, or a
                       ``(singular, plural)`` tuple for pluralizable messages
        :param locations: a sequence of ``(filenname, lineno)`` tuples
        :param flags: a set or sequence of flags
        :param auto_comments: a sequence of automatic comments
        :param user_comments: a sequence of user comments
        """
        self[id] = Message(id, string, list(locations), flags, auto_comments,
                           user_comments)

    def update(self, template, fuzzy_matching=True):
        """Update the catalog based on the given template catalog.
        
        >>> from babel.messages import Catalog
        >>> template = Catalog()
        >>> template.add('green', locations=[('main.py', 99)])
        >>> template.add('blue', locations=[('main.py', 100)])
        >>> template.add(('salad', 'salads'), locations=[('util.py', 42)])
        >>> catalog = Catalog(locale='de_DE')
        >>> catalog.add('blue', u'blau', locations=[('main.py', 98)])
        >>> catalog.add('head', u'Kopf', locations=[('util.py', 33)])
        >>> catalog.add(('salad', 'salads'), (u'Salat', u'Salate'),
        ...             locations=[('util.py', 38)])
        
        >>> catalog.update(template)
        >>> len(catalog)
        3
        
        >>> msg1 = catalog['green']
        >>> msg1.string
        >>> msg1.locations
        [('main.py', 99)]
        
        >>> msg2 = catalog['blue']
        >>> msg2.string
        u'blau'
        >>> msg2.locations
        [('main.py', 100)]
        
        >>> msg3 = catalog['salad']
        >>> msg3.string
        (u'Salat', u'Salate')
        >>> msg3.locations
        [('util.py', 42)]
        
        Messages that are in the catalog but not in the template are removed
        from the main collection, but can still be accessed via the `obsolete`
        member:
        
        >>> 'head' in catalog
        False
        >>> catalog.obsolete.values()
        [<Message 'head' (Flags: '')>]
        
        :param template: the reference catalog, usually read from a POT file
        :param fuzzy_matching: whether to use fuzzy matching of message IDs
        """
        messages = self._messages
        self._messages = odict()

        for message in template:
            if message.id:
                key = self._key_for(message.id)
                if key in messages:
                    oldmsg = messages.pop(key)
                    message.string = oldmsg.string
                    message.flags |= oldmsg.flags
                    self[message.id] = message

                else:
                    if fuzzy_matching:
                        # do some fuzzy matching with difflib
                        matches = get_close_matches(key.lower().strip(),
                            [self._key_for(msgid) for msgid in messages], 1)
                        if matches:
                            oldmsg = messages.pop(matches[0])
                            message.string = oldmsg.string
                            message.flags |= oldmsg.flags | set([u'fuzzy'])
                            self[message.id] = message
                            continue

                    self[message.id] = message

        self.obsolete = messages

    def _key_for(self, id):
        """The key for a message is just the singular ID even for pluralizable
        messages.
        """
        key = id
        if isinstance(key, (list, tuple)):
            key = id[0]
        return key
