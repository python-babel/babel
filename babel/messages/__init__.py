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

"""Support for ``gettext`` message catalogs."""

import gettext

__all__ = ['Translations']

DEFAULT_DOMAIN = 'messages'


class Translations(gettext.GNUTranslations):
    """An extended translation catalog class."""

    def __init__(self, fileobj=None):
        """Initialize the translations catalog.
        
        :param fileobj: the file-like object the translation should be read
                        from
        """
        gettext.GNUTranslations.__init__(self, fp=fileobj)
        self.files = [getattr(fileobj, 'name')]

    def load(cls, dirname=None, locales=None, domain=DEFAULT_DOMAIN):
        """Load translations from the given directory.
        
        :param dirname: the directory containing the ``MO`` files
        :param locales: the list of locales in order of preference (items in
                        this list can be either `Locale` objects or locale
                        strings)
        :param domain: the message domain
        :return: the loaded catalog, or a ``NullTranslations`` instance if no
                 matching translations were found
        :rtype: `Translations`
        """
        if not isinstance(locales, (list, tuple)):
            locales = [locales]
        locales = [str(locale) for locale in locales]
        filename = gettext.find(domain, dirname, locales)
        if not filename:
            return gettext.NullTranslations()
        return cls(fileobj=open(filename, 'rb'))
    load = classmethod(load)

    def merge(self, translations):
        """Merge the given translations into the catalog.
        
        Message translations in the specfied catalog override any messages with
        the same identifier in the existing catalog.
        
        :param translations: the `Translations` instance with the messages to
                             merge
        :return: the `Translations` instance (``self``) so that `merge` calls
                 can be easily chained
        :rtype: `Translations`
        """
        if isinstance(translations, Translations):
            self._catalog.update(translations._catalog)
            self.files.extend(translations.files)
        return self

    def __repr__(self):
        return "<%s %r>" % (type(self).__name__)
