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

import re
try:
    set
except NameError:
    from sets import Set as set

from babel.core import Locale
from babel.util import odict

__all__ = ['Message', 'Catalog']
__docformat__ = 'restructuredtext en'

PYTHON_FORMAT = re.compile(r'\%(\([\w]+\))?[diouxXeEfFgGcrs]').search


class Message(object):
    """Representation of a single message in a catalog."""

    def __init__(self, id, string=None, locations=(), flags=()):
        """Create the message object.
        
        :param id: the message ID, or a ``(singular, plural)`` tuple for
                   pluralizable messages
        :param string: the translated message string, or a
                       ``(singular, plural)`` tuple for pluralizable messages
        :param locations: a sequence of ``(filenname, lineno)`` tuples
        :param flags: a set or sequence of flags
        """
        self.id = id
        self.string = string
        self.locations = locations
        self.flags = set(flags)
        if self.python_format:
            self.flags.add('python-format')
        else:
            self.flags.discard('python-format')

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.id)

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
    """Representation a message catalog."""

    def __init__(self, domain=None, locale=None):
        """Initialize the catalog object.
        
        :param domain: the message domain
        :param locale: the locale identifier or `Locale` object, or `None`
                       if the catalog is not bound to a locale (which basically
                       means it's a template)
        """
        self.domain = domain #: the message domain
        if locale:
            locale = Locale.parse(locale)
        self.locale = locale #: the locale or `None`
        self.messages = odict() #: the actual `Message` entries by ID

    def __iter__(self):
        """Iterates through all the entries in the catalog, in the order they
        were added, yielding a `Message` object for every entry.
        
        :rtype: ``iterator``
        """
        for id in self.messages:
            yield self.messages[id]

    def __repr__(self):
        locale = ''
        if self.locale:
            locale = ' %s' % self.locale
        return '<%s %r%s>' % (type(self).__name__, self.domain, locale)

    def __delitem__(self, id):
        """Delete the message with the specified ID."""
        if id in self.messaages:
            del self.messages[id]

    def __getitem__(self, id):
        """Return the message with the specified ID.
        
        :param id: the message ID
        :return: the message with the specified ID, or `None` if no such message
                 is in the catalog
        :rytpe: `Message`
        """
        return self.messages.get(id)

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
        current = self.messages.get(id)
        if current:
            assert current.string == message.string, 'translation mismatch'
            current.locations.extend(message.locations)
            current.flags |= message.flags
            message = current
        else:
            if isinstance(id, (list, tuple)):
                singular, plural = id
                id = singular
            self.messages[id] = message

    def add(self, id, string=None, locations=(), flags=()):
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
        """
        self[id] = Message(id, string, locations, flags)
