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

"""Various routines that help with validation of translations."""

from babel.messages.catalog import TranslationError, PYTHON_FORMAT

def num_plurals(catalog, message):
    """Verify the number of plurals in the translation."""
    if not message.pluralizable:
        if not isinstance(message.string, basestring):
            raise TranslationError("Found plural forms for non-pluralizable "
                                   "message")
        return

    msgstrs = message.string
    if not isinstance(msgstrs, (list, tuple)):
        msgstrs = (msgstrs,)
    if len(msgstrs) != catalog.num_plurals:
        raise TranslationError("Wrong number of plural forms (expected %d)" %
                               catalog.num_plurals)

def python_format(catalog, message):
    if 'python-format' in message.flags:
        msgids = message.id
        if not isinstance(msgids, (list, tuple)):
            msgids = (msgids,)
        msgstrs = message.string
        if not isinstance(msgstrs, (list, tuple)):
            msgstrs = (msgstrs,)
        for idx, msgid in enumerate(msgids):
            if not msgstrs[idx]:
                continue # no translation
            for match in PYTHON_FORMAT.finditer(msgid):
                param = match.group(0)
                if param not in msgstrs[idx]:
                    raise TranslationError("Python parameter %s not found in "
                                           "translation" % param)
