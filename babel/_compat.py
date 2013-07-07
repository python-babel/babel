# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2011 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.


import sys

PY2 = sys.version_info[0] == 2

_identity = lambda x: x


if not PY2:
    text_type = str
    string_types = (str,)
    integer_types = (int, )

    text_to_native = lambda s, enc: s

    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())

    from io import StringIO, BytesIO
    import pickle

    izip = zip
    imap = map
    range_type = range

    cmp = lambda a, b: (a > b) - (a < b)

else:
    text_type = unicode
    string_types = (str, unicode)
    integer_types = (int, long)

    text_to_native = lambda s, enc: s.encode(enc)

    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()

    from cStringIO import StringIO as BytesIO
    from StringIO import StringIO
    import cPickle as pickle

    from itertools import izip, imap
    range_type = xrange

    cmp = cmp


number_types = integer_types + (float,)
