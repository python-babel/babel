from io import BytesIO

import pytest

from babel.messages.extract import extract
from babel.messages.jslexer import unquote_string


@pytest.mark.parametrize('quote', ["'", '"', '`'])
@pytest.mark.parametrize(('body', 'expected'), [
    (r'a\u{0}b', 'a\0b'),
    (r'\u{41}', 'A'),
    (r'\u{e9}', 'é'),
    (r'\u{1F600}', '😀'),
    (r'\u{10FFFF}', '\U0010ffff'),
    (r'\u{000000000041}', 'A'),
])
def test_unicode_codepoint_escapes(quote, body, expected):
    assert unquote_string(quote + body + quote) == expected


@pytest.mark.parametrize('quote', ["'", '"', '`'])
def test_unicode_codepoint_extraction_uses_runtime_message(quote):
    source = f'gettext({quote}Hello \\u{{1F600}}{quote});\ngettext("next");'
    messages = list(extract('javascript', BytesIO(source.encode()), options={}))
    assert messages == [(1, 'Hello 😀', [], None), (2, 'next', [], None)]


@pytest.mark.parametrize(('body', 'expected'), [
    (r'\u{1f600}\u{1f680}', '😀🚀'),
    (r'\u00e9\u{1f600}\x21', 'é😀!'),
    (r'\\u{1F600}', r'\u{1F600}'),
    (r'\U{41}', 'U{41}'),
    (r'\u{}', 'u{}'),
    (r'\u{xyz}', 'u{xyz}'),
    (r'\u{110000}', 'u{110000}'),
    (r'\u{41', 'u{41'),
])
def test_codepoint_escapes_preserve_existing_escape_behavior(body, expected):
    assert unquote_string('"' + body + '"') == expected
