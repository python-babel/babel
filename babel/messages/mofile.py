# -*- coding: utf-8 -*-
"""
    babel.messages.mofile
    ~~~~~~~~~~~~~~~~~~~~~

    Writing of files in the ``gettext`` MO (machine object) format.

    :copyright: (c) 2013-2018 by the Babel Team.
    :license: BSD, see LICENSE for more details.
"""

import array
import struct

from babel.messages.catalog import Catalog, Message
from babel._compat import range_type, array_tobytes


LE_MAGIC = 0x950412de
BE_MAGIC = 0xde120495


def read_mo(fileobj, coverage):
    """Read a binary MO file from the given file-like object and return a
    corresponding `Catalog` object.

    :param fileobj: the file-like object to read the MO file from

    :note: The implementation of this function is heavily based on the
           ``GNUTranslations._parse`` method of the ``gettext`` module in the
           standard library.
    """
    coverage[0] = 1
    catalog = Catalog()
    headers = {}

    filename = getattr(fileobj, 'name', '')

    buf = fileobj.read()
    buflen = len(buf)
    unpack = struct.unpack

    # Parse the .mo file header, which consists of 5 little endian 32
    # bit words.
    magic = unpack('<I', buf[:4])[0]  # Are we big endian or little endian?
    if magic == LE_MAGIC:
        coverage[1] = 1
        version, msgcount, origidx, transidx = unpack('<4I', buf[4:20])
        ii = '<II'
    elif magic == BE_MAGIC:
        coverage[2] = 1
        version, msgcount, origidx, transidx = unpack('>4I', buf[4:20])
        ii = '>II'
    else:
        coverage[3] = 1
        raise IOError(0, 'Bad magic number', filename)

    # Now put all messages from the .mo file buffer into the catalog
    # dictionary
    for i in range_type(0, msgcount):
        coverage[4] = 1
        mlen, moff = unpack(ii, buf[origidx:origidx + 8])
        mend = moff + mlen
        tlen, toff = unpack(ii, buf[transidx:transidx + 8])
        tend = toff + tlen
        if mend < buflen and tend < buflen:
            coverage[5] = 1
            msg = buf[moff:mend]
            tmsg = buf[toff:tend]
        else:
            coverage[6] = 1
            raise IOError(0, 'File is corrupt', filename)

        # See if we're looking at GNU .mo conventions for metadata
        if mlen == 0:
            coverage[7] = 1
            # Catalog description
            lastkey = key = None
            for item in tmsg.splitlines():
                coverage[8] = 1
                item = item.strip()
                if not item:
                    coverage[9] = 1
                    continue
                else:
                    coverage[10] = 1
                if b':' in item:
                    coverage[11] = 1
                    key, value = item.split(b':', 1)
                    lastkey = key = key.strip().lower()
                    headers[key] = value.strip()
                elif lastkey:
                    coverage[12] = 1
                    headers[lastkey] += b'\n' + item
                else:
                    coverage[13] = 1
        else:
            coverage[14] = 1
        if b'\x04' in msg:  # context
            coverage[15] = 1
            ctxt, msg = msg.split(b'\x04')
        else:
            coverage[16] = 1
            ctxt = None

        if b'\x00' in msg:  # plural forms
            coverage[17] = 1
            msg = msg.split(b'\x00')
            tmsg = tmsg.split(b'\x00')
            if catalog.charset:
                coverage[18] = 1
                msg = [x.decode(catalog.charset) for x in msg]
                tmsg = [x.decode(catalog.charset) for x in tmsg]
            else:
                coverage[19] = 1
        else:
            coverage[20] = 1
            if catalog.charset:
                coverage[21] = 1
                msg = msg.decode(catalog.charset)
                tmsg = tmsg.decode(catalog.charset)
            else:
                coverage[22] = 1
        catalog[msg] = Message(msg, tmsg, context=ctxt)

        # advance to next entry in the seek tables
        origidx += 8
        transidx += 8

    catalog.mime_headers = headers.items()
    return catalog


def write_mo(fileobj, catalog, coverage, use_fuzzy=False):
    """Write a catalog to the specified file-like object using the GNU MO file
    format.

    >>> import sys
    >>> from babel.messages import Catalog
    >>> from gettext import GNUTranslations
    >>> from babel._compat import BytesIO

    >>> catalog = Catalog(locale='en_US')
    >>> catalog.add('foo', 'Voh')
    <Message ...>
    >>> catalog.add((u'bar', u'baz'), (u'Bahr', u'Batz'))
    <Message ...>
    >>> catalog.add('fuz', 'Futz', flags=['fuzzy'])
    <Message ...>
    >>> catalog.add('Fizz', '')
    <Message ...>
    >>> catalog.add(('Fuzz', 'Fuzzes'), ('', ''))
    <Message ...>
    >>> buf = BytesIO()

    >>> write_mo(buf, catalog)
    >>> x = buf.seek(0)
    >>> translations = GNUTranslations(fp=buf)
    >>> if sys.version_info[0] >= 3:
    ...     translations.ugettext = translations.gettext
    ...     translations.ungettext = translations.ngettext
    >>> translations.ugettext('foo')
    u'Voh'
    >>> translations.ungettext('bar', 'baz', 1)
    u'Bahr'
    >>> translations.ungettext('bar', 'baz', 2)
    u'Batz'
    >>> translations.ugettext('fuz')
    u'fuz'
    >>> translations.ugettext('Fizz')
    u'Fizz'
    >>> translations.ugettext('Fuzz')
    u'Fuzz'
    >>> translations.ugettext('Fuzzes')
    u'Fuzzes'

    :param fileobj: the file-like object to write to
    :param catalog: the `Catalog` instance
    :param use_fuzzy: whether translations marked as "fuzzy" should be included
                      in the output
    """
    coverage[0] = 1
    messages = list(catalog)
    messages[1:] = [m for m in messages[1:]
                    if m.string and (use_fuzzy or not m.fuzzy)]
    messages.sort()

    ids = strs = b''
    offsets = []

    for message in messages:
        coverage[1] = 1
        # For each string, we need size and file offset.  Each string is NUL
        # terminated; the NUL does not count into the size.
        if message.pluralizable:
            coverage[2] = 1
            msgid = b'\x00'.join([
                msgid.encode(catalog.charset) for msgid in message.id
            ])
            msgstrs = []
            for idx, string in enumerate(message.string):
                coverage[3] = 1
                if not string:
                    coverage[4] = 1
                    msgstrs.append(message.id[min(int(idx), 1)])
                else:
                    coverage[5] = 1
                    msgstrs.append(string)
            msgstr = b'\x00'.join([
                msgstr.encode(catalog.charset) for msgstr in msgstrs
            ])
        else:
            coverage[6] = 1
            msgid = message.id.encode(catalog.charset)
            msgstr = message.string.encode(catalog.charset)
        if message.context:
            coverage[7] = 1
            msgid = b'\x04'.join([message.context.encode(catalog.charset),
                                  msgid])
        else:
            coverage[8] = 1
        offsets.append((len(ids), len(msgid), len(strs), len(msgstr)))
        ids += msgid + b'\x00'
        strs += msgstr + b'\x00'

    # The header is 7 32-bit unsigned integers.  We don't use hash tables, so
    # the keys start right after the index tables.
    keystart = 7 * 4 + 16 * len(messages)
    valuestart = keystart + len(ids)

    # The string table first has the list of keys, then the list of values.
    # Each entry has first the size of the string, then the file offset.
    koffsets = []
    voffsets = []
    for o1, l1, o2, l2 in offsets:
        coverage[9] = 1
        koffsets += [l1, o1 + keystart]
        voffsets += [l2, o2 + valuestart]
    offsets = koffsets + voffsets

    fileobj.write(struct.pack('Iiiiiii',
                              LE_MAGIC,                   # magic
                              0,                          # version
                              len(messages),              # number of entries
                              7 * 4,                      # start of key index
                              7 * 4 + len(messages) * 8,  # start of value index
                              0, 0                        # size and offset of hash table
                              ) + array_tobytes(array.array("i", offsets)) + ids + strs)
