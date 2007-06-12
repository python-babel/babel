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

from datetime import datetime
import re
try:
    set
except NameError:
    from sets import Set as set
import time

from babel import __version__ as VERSION
from babel.core import Locale
from babel.messages.plurals import PLURALS
from babel.util import odict, LOCAL, UTC

__all__ = ['Message', 'Catalog']
__docformat__ = 'restructuredtext en'

PYTHON_FORMAT = re.compile(r'\%(\([\w]+\))?[diouxXeEfFgGcrs]').search


class Message(object):
    """Representation of a single message in a catalog."""

    def __init__(self, id, string='', locations=(), flags=(), comments=()):
        """Create the message object.
        
        :param id: the message ID, or a ``(singular, plural)`` tuple for
                   pluralizable messages
        :param string: the translated message string, or a
                       ``(singular, plural)`` tuple for pluralizable messages
        :param locations: a sequence of ``(filenname, lineno)`` tuples
        :param flags: a set or sequence of flags
        :param comments: a sequence of translator comments for the message
        """
        self.id = id
        if not string and self.pluralizable:
            string = (u'', u'')
        self.string = string
        self.locations = list(locations)
        self.flags = set(flags)
        if id and self.python_format:
            self.flags.add('python-format')
        else:
            self.flags.discard('python-format')
        self.comments = list(comments)

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.id)

    def fuzzy(self):
        return 'fuzzy' in self.flags
    fuzzy = property(fuzzy, doc="""\
        Whether the translation is fuzzy.
        
        >>> Message('foo').fuzzy
        False
        >>> Message('foo', 'foo', flags=['fuzzy']).fuzzy
        True
        
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


class Catalog(object):
    """Representation of a message catalog."""

    def __init__(self, locale=None, domain=None, project=None, version=None,
                 msgid_bugs_address=None, creation_date=None,
                 revision_date=None, last_translator=None, charset='utf-8'):
        """Initialize the catalog object.
        
        :param locale: the locale identifier or `Locale` object, or `None`
                       if the catalog is not bound to a locale (which basically
                       means it's a template)
        :param domain: the message domain
        :param project: the project's name
        :param version: the project's version
        :param msgid_bugs_address: the address to report bugs about the catalog
        :param creation_date: the date the catalog was created
        :param revision_date: the date the catalog was revised
        :param last_translator: the name and email of the last translator
        """
        self.domain = domain #: the message domain
        if locale:
            locale = Locale.parse(locale)
        self.locale = locale #: the locale or `None`
        self._messages = odict()

        self.project = project or 'PROJECT' #: the project name
        self.version = version or 'VERSION' #: the project version
        self.msgid_bugs_address = msgid_bugs_address or 'EMAIL@ADDRESS'
        self.last_translator = last_translator #: last translator name + email
        self.charset = charset or 'utf-8'

        if creation_date is None:
            creation_date = datetime.now(LOCAL)
        elif isinstance(creation_date, datetime) and not creation_date.tzinfo:
            creation_date = creation_date.replace(tzinfo=LOCAL)
        self.creation_date = creation_date #: creation date of the template
        if revision_date is None:
            revision_date = datetime.now(LOCAL)
        elif isinstance(revision_date, datetime) and not revision_date.tzinfo:
            revision_date = revision_date.replace(tzinfo=LOCAL)
        self.revision_date = revision_date #: last revision date of the catalog

    def headers(self):
        headers = []
        headers.append(('Project-Id-Version',
                        '%s %s' % (self.project, self.version)))
        headers.append(('Report-Msgid-Bugs-To', self.msgid_bugs_address))
        headers.append(('POT-Creation-Date',
                        self.creation_date.strftime('%Y-%m-%d %H:%M%z')))
        if self.locale is None:
            headers.append(('PO-Revision-Date', 'YEAR-MO-DA HO:MI+ZONE'))
            headers.append(('Last-Translator', 'FULL NAME <EMAIL@ADDRESS>'))
            headers.append(('Language-Team', 'LANGUAGE <LL@li.org>'))
        else:
            headers.append(('PO-Revision-Date',
                            self.revision_date.strftime('%Y-%m-%d %H:%M%z')))
            headers.append(('Last-Translator', self.last_translator))
            headers.append(('Language-Team', '%s <LL@li.org>' % self.locale))
            headers.append(('Plural-Forms', self.plural_forms))
        headers.append(('MIME-Version', '1.0'))
        headers.append(('Content-Type',
                        'text/plain; charset=%s' % self.charset))
        headers.append(('Content-Transfer-Encoding', '8bit'))
        headers.append(('Generated-By', 'Babel %s' % VERSION))
        return headers
    headers = property(headers, doc="""\
    The MIME headers of the catalog, used for the special ``msgid ""`` entry.
    
    The behavior of this property changes slightly depending on whether a locale
    is set or not, the latter indicating that the catalog is actually a template
    for actual translations.
    
    Here's an example of the output for such a catalog template:
    
    >>> created = datetime(1990, 4, 1, 15, 30, tzinfo=UTC)
    >>> catalog = Catalog(project='Foobar', version='1.0',
    ...                   creation_date=created)
    >>> for name, value in catalog.headers:
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
    >>> for name, value in catalog.headers:
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
    
    >>> Catalog(locale='en_US').plural_forms
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
        for name, value in self.headers:
            buf.append('%s: %s' % (name, value))
        yield Message('', '\n'.join(buf), flags=set(['fuzzy']))
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
        <Message u'foo'>
        
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
            current.comments.extend(message.comments)
            current.flags |= message.flags
            message = current
        else:
            if isinstance(id, (list, tuple)):
                assert isinstance(message.string, (list, tuple))
            self._messages[key] = message

    def add(self, id, string=None, locations=(), flags=(), comments=()):
        """Add or update the message with the specified ID.
        
        >>> catalog = Catalog()
        >>> catalog.add(u'foo')
        >>> catalog[u'foo']
        <Message u'foo'>
        
        This method simply constructs a `Message` object with the given
        arguments and invokes `__setitem__` with that object.
        
        :param id: the message ID, or a ``(singular, plural)`` tuple for
                   pluralizable messages
        :param string: the translated message string, or a
                       ``(singular, plural)`` tuple for pluralizable messages
        :param locations: a sequence of ``(filenname, lineno)`` tuples
        :param flags: a set or sequence of flags
        :param comments: a list of translator comments
        """
        self[id] = Message(id, string, list(locations), flags, comments)

    def _key_for(self, id):
        """The key for a message is just the singular ID even for pluralizable
        messages.
        """
        key = id
        if isinstance(key, (list, tuple)):
            key = id[0]
        return key
