from io import BytesIO

import pytest

from babel.messages.extract import extract, extract_javascript
from babel.messages.jslexer import tokenize, unquote_string


@pytest.mark.parametrize('newline', ['\n', '\r', '\r\n', '\u2028', '\u2029'])
@pytest.mark.parametrize('comment', ['// ignored', '<!-- ignored'])
def test_line_comments_end_at_all_javascript_line_terminators(newline, comment):
    source = comment + newline + 'gettext("visible");'
    assert list(extract('javascript', BytesIO(source.encode()), options={})) == [
        (2, 'visible', [], None),
    ]


@pytest.mark.parametrize('newline', ['\n', '\r', '\r\n', '\u2028', '\u2029'])
def test_translator_comments_with_javascript_line_terminators(newline):
    lines = [
        '// NOTE: translator comment',
        '// continued',
        'gettext("visible");',
    ]
    source = newline.join(lines)
    assert list(extract_javascript(BytesIO(source.encode()), ('gettext',), ['NOTE:'], {})) == [
        (3, 'gettext', 'visible', ['NOTE: translator comment', 'continued']),
    ]


@pytest.mark.parametrize('newline', ['\u2028', '\u2029'])
@pytest.mark.parametrize(
    'source',
    [
        '{newline}gettext("visible");',
        '/* comment{newline}continued */gettext("visible");',
        '`template{newline}continued`;gettext("visible");',
    ],
)
def test_unicode_line_terminators_advance_source_lines(newline, source):
    tokens = list(tokenize(source.format(newline=newline)))
    gettext = next(token for token in tokens if token.value == 'gettext')
    assert gettext.lineno == 2


@pytest.mark.parametrize('newline', ['\u2028', '\u2029'])
def test_unicode_blank_line_separates_translator_comment(newline):
    source = '// NOTE: separated' + newline + newline + 'gettext("visible");'
    assert list(extract_javascript(BytesIO(source.encode()), ('gettext',), ['NOTE:'], {})) == [
        (3, 'gettext', 'visible', []),
    ]


@pytest.mark.parametrize('quote', ["'", '"', '`'])
@pytest.mark.parametrize('newline', ['\u2028', '\u2029'])
def test_escaped_backslash_before_unicode_line_terminator(quote, newline):
    literal = quote + 'before' + r'\\' + newline + 'after' + quote
    expected = 'before\\' + newline + 'after'
    assert unquote_string(literal) == expected
    source = 'gettext(' + literal + ');'
    assert list(extract('javascript', BytesIO(source.encode()), options={})) == [
        (1, expected, [], None),
    ]
