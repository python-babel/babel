from io import BytesIO

import pytest

from babel.messages import extract, jslexer


@pytest.mark.parametrize('quote', ["'", '"', '`'])
@pytest.mark.parametrize('newline', ['\n', '\r', '\r\n', '\u2028', '\u2029'])
def test_unquote_line_continuation(quote, newline):
    source = f'{quote}hello\\{newline}world{quote}'
    assert jslexer.unquote_string(source) == 'helloworld'


@pytest.mark.parametrize('quote', ["'", '"', '`'])
@pytest.mark.parametrize('newline', ['\n', '\r', '\r\n'])
def test_extract_line_continuation_and_keep_source_line_numbers(quote, newline):
    source = f'gettext({quote}hello\\{newline}world{quote});\ngettext("after");'
    messages = list(extract.extract('javascript', BytesIO(source.encode('utf-8'))))
    assert messages == [(1, 'helloworld', [], None), (3, 'after', [], None)]


@pytest.mark.parametrize('quote', ["'", '"', '`'])
@pytest.mark.parametrize(('content', 'expected'), [
    (r'hello\nworld', 'hello\nworld'),
    (r'hello\\nworld', r'hello\nworld'),
])
def test_ordinary_escapes_are_preserved(quote, content, expected):
    assert jslexer.unquote_string(quote + content + quote) == expected


def test_escaped_backslash_does_not_start_template_line_continuation():
    source = '`hello' + '\\\\' + '\nworld`'
    assert jslexer.unquote_string(source) == 'hello\\\nworld'
