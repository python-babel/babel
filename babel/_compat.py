import sys
import array

PY2 = sys.version_info[0] == 2

_identity = lambda x: x


if not PY2:
    text_type = str
    binary_type = bytes
    string_types = (str,)
    integer_types = (int, )

    text_to_native = lambda s, enc: s
    unichr = chr

    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())

    from io import StringIO, BytesIO
    import pickle

    izip = zip
    imap = map
    range_type = range

    cmp = lambda a, b: (a > b) - (a < b)

    array_tobytes = array.array.tobytes

else:
    text_type = unicode
    binary_type = str
    string_types = (str, unicode)
    integer_types = (int, long)

    text_to_native = lambda s, enc: s.encode(enc)
    unichr = unichr

    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()

    from cStringIO import StringIO as BytesIO
    from StringIO import StringIO
    import cPickle as pickle

    from itertools import imap
    from itertools import izip
    range_type = xrange

    cmp = cmp

    array_tobytes = array.array.tostring


number_types = integer_types + (float,)


def force_text(s, encoding='utf-8', errors='strict'):
    if isinstance(s, text_type):
        return s
    if isinstance(s, binary_type):
        return s.decode(encoding, errors)
    return text_type(s)


#
# Since Python 3.3, a fast decimal implementation is already included in the
# standard library.  Otherwise use cdecimal when available
#
if sys.version_info[:2] >= (3, 3):
    import decimal
else:
    try:
        import cdecimal as decimal
    except ImportError:
        import decimal

# In Python 3.7, importing ABCs directly from the collections module shows a
# warning and in Python 3.8 it will stop working
# Refer : https://github.com/python/cpython/commit/c66f9f8d3909f588c251957d499599a1680e2320

if not PY2:
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping
