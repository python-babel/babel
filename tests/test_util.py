#
# Copyright (C) 2007-2011 Edgewall Software, 2013-2025 the Babel team
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution. The terms
# are also available at https://github.com/python-babel/babel/blob/master/LICENSE.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at https://github.com/python-babel/babel/commits/master/.

import __future__

from io import BytesIO

import pytest

from babel import util
from babel.util import parse_future_flags


class _FF:
    division = __future__.division.compiler_flag
    print_function = __future__.print_function.compiler_flag
    with_statement = __future__.with_statement.compiler_flag
    unicode_literals = __future__.unicode_literals.compiler_flag


def test_distinct():
    assert list(util.distinct([1, 2, 1, 3, 4, 4])) == [1, 2, 3, 4]
    assert list(util.distinct('foobar')) == ['f', 'o', 'b', 'a', 'r']


def test_pathmatch():
    assert util.pathmatch('**.py', 'bar.py')
    assert util.pathmatch('**.py', 'foo/bar/baz.py')
    assert not util.pathmatch('**.py', 'templates/index.html')
    assert util.pathmatch('**/templates/*.html', 'templates/index.html')
    assert not util.pathmatch('**/templates/*.html', 'templates/foo/bar.html')
    assert util.pathmatch('^foo/**.py', 'foo/bar/baz/blah.py')
    assert not util.pathmatch('^foo/**.py', 'blah/foo/bar/baz.py')
    assert util.pathmatch('./foo/**.py', 'foo/bar/baz/blah.py')
    assert util.pathmatch('./blah.py', 'blah.py')
    assert not util.pathmatch('./foo/**.py', 'blah/foo/bar/baz.py')


def test_fixed_zone_negative_offset():
    assert util.FixedOffsetTimezone(-60).zone == 'Etc/GMT-60'


def test_fixed_zone_zero_offset():
    assert util.FixedOffsetTimezone(0).zone == 'Etc/GMT+0'


def test_fixed_zone_positive_offset():
    assert util.FixedOffsetTimezone(330).zone == 'Etc/GMT+330'


def parse_encoding(s):
    return util.parse_encoding(BytesIO(s.encode('utf-8')))


def test_parse_encoding_defined():
    assert parse_encoding('# coding: utf-8') == 'utf-8'


def test_parse_encoding_undefined():
    assert parse_encoding('') is None


def test_parse_encoding_non_ascii():
    assert parse_encoding('K\xf6ln') is None


def test_parse_encoding_second_line_allowed():
    for prefix in (
        '\n',
        '\r\n',
        '  \t\f\n',
        '#!/usr/bin/env python3\n',
        '  # comment\n',
    ):
        assert parse_encoding(f'{prefix}# coding: latin-1\n') == 'latin-1'

    assert util.parse_encoding(BytesIO(b'# K\xf6ln\n# coding: latin-1\n')) == 'latin-1'


def test_parse_encoding_second_line_ignored_after_code():
    for first_line in (
        'x = 1\n',
        '"""docstring"""\n',
        ';\n',
        'pass\n',
        '\\\n',
        '\x0b\n',
        '  x = 1  # trailing comment\n',
    ):
        assert parse_encoding(f'{first_line}# coding: latin-1\n') is None


def test_parse_encoding_bom_with_code_ignores_second_line_coding():
    buf = BytesIO('x = 1\n# coding: latin-1\n'.encode('utf-8-sig'))
    assert util.parse_encoding(buf) == 'utf-8'


def test_parse_encoding_preserves_stream_position():
    buf = BytesIO(b'x = 1\n# coding: latin-1\n')
    buf.seek(5)
    assert util.parse_encoding(buf) is None
    assert buf.tell() == 5


@pytest.mark.parametrize(('source', 'result'), [
    ('''
from __future__ import print_function,
    division, with_statement,
    unicode_literals
''', _FF.print_function | _FF.division | _FF.with_statement | _FF.unicode_literals),
    ('''
from __future__ import print_function, division
print('hello')
''', _FF.print_function | _FF.division),
    ('''
from __future__ import print_function, division, unknown,,,,,
print 'hello'
''', _FF.print_function | _FF.division),
    ('''
from __future__ import (
    print_function,
    division)
''', _FF.print_function | _FF.division),
    ('''
from __future__ import \\
    print_function, \\
    division
''', _FF.print_function | _FF.division),
])
def test_parse_future(source, result):
    fp = BytesIO(source.encode('latin-1'))
    flags = parse_future_flags(fp)
    assert flags == result
