import pytest

from babel.messages import jslexer


def test_unquote():
    assert jslexer.unquote_string('""') == ''
    assert jslexer.unquote_string(r'"h\u00ebllo"') == "hëllo"
    assert jslexer.unquote_string(r'"h\xebllo"') == "hëllo"
    assert jslexer.unquote_string(r'"\xebb"') == "ëb"


def test_dollar_in_identifier():
    assert list(jslexer.tokenize('dollar$dollar')) == [('name', 'dollar$dollar', 1)]


def test_dotted_name():
    assert list(jslexer.tokenize("foo.bar(quux)", dotted=True)) == [
        ('name', 'foo.bar', 1),
        ('operator', '(', 1),
        ('name', 'quux', 1),
        ('operator', ')', 1),
    ]


def test_dotted_name_end():
    assert list(jslexer.tokenize("foo.bar", dotted=True)) == [
        ('name', 'foo.bar', 1),
    ]


def test_template_string():
    assert list(jslexer.tokenize("gettext `foo\"bar\"p`", template_string=True)) == [
        ('name', 'gettext', 1),
        ('template_string', '`foo"bar"p`', 1),
    ]


def test_jsx():
    assert list(jslexer.tokenize("""
         <option value="val1">{ i18n._('String1') }</option>
         <option value="val2">{ i18n._('String 2') }</option>
         <option value="val3">{ i18n._('String 3') }</option>
         <component value={i18n._('String 4')} />
         <comp2 prop={<comp3 />} data={{active: true}}>
             <btn text={ i18n._('String 5') } />
         </comp2>
    """, jsx=True)) == [
        ('jsx_tag', '<option', 2),
        ('name', 'value', 2),
        ('operator', '=', 2),
        ('string', '"val1"', 2),
        ('operator', '>', 2),
        ('operator', '{', 2),
        ('name', 'i18n._', 2),
        ('operator', '(', 2),
        ('string', "'String1'", 2),
        ('operator', ')', 2),
        ('operator', '}', 2),
        ('jsx_tag', '</option', 2),
        ('operator', '>', 2),
        ('jsx_tag', '<option', 3),
        ('name', 'value', 3),
        ('operator', '=', 3),
        ('string', '"val2"', 3),
        ('operator', '>', 3),
        ('operator', '{', 3),
        ('name', 'i18n._', 3),
        ('operator', '(', 3),
        ('string', "'String 2'", 3),
        ('operator', ')', 3),
        ('operator', '}', 3),
        ('jsx_tag', '</option', 3),
        ('operator', '>', 3),
        ('jsx_tag', '<option', 4),
        ('name', 'value', 4),
        ('operator', '=', 4),
        ('string', '"val3"', 4),
        ('operator', '>', 4),
        ('operator', '{', 4),
        ('name', 'i18n._', 4),
        ('operator', '(', 4),
        ('string', "'String 3'", 4),
        ('operator', ')', 4),
        ('operator', '}', 4),
        ('jsx_tag', '</option', 4),
        ('operator', '>', 4),
        ('jsx_tag', '<component', 5),
        ('name', 'value', 5),
        ('operator', '=', 5),
        ('operator', '{', 5),
        ('name', 'i18n._', 5),
        ('operator', '(', 5),
        ('string', "'String 4'", 5),
        ('operator', ')', 5),
        ('operator', '}', 5),
        ('jsx_tag', '/>', 5),
        ('jsx_tag', '<comp2', 6),
        ('name', 'prop', 6),
        ('operator', '=', 6),
        ('operator', '{', 6),
        ('jsx_tag', '<comp3', 6),
        ('jsx_tag', '/>', 6),
        ('operator', '}', 6),
        ('name', 'data', 6),
        ('operator', '=', 6),
        ('operator', '{', 6),
        ('operator', '{', 6),
        ('name', 'active', 6),
        ('operator', ':', 6),
        ('name', 'true', 6),
        ('operator', '}', 6),
        ('operator', '}', 6),
        ('operator', '>', 6),
        ('jsx_tag', '<btn', 7),
        ('name', 'text', 7),
        ('operator', '=', 7),
        ('operator', '{', 7),
        ('name', 'i18n._', 7),
        ('operator', '(', 7),
        ('string', "'String 5'", 7),
        ('operator', ')', 7),
        ('operator', '}', 7),
        ('jsx_tag', '/>', 7),
        ('jsx_tag', '</comp2', 8),
        ('operator', '>', 8),
    ]


LINE_TERMINATORS = ["\n", "\r", "\r\n", "\u2028", "\u2029"]


@pytest.mark.parametrize("terminator", LINE_TERMINATORS)
def test_regexp_literal_cannot_span_lines(terminator):
    # A JS regex literal may not contain any of the ECMAScript line terminators;
    # the fallback regex match must stop at one instead of swallowing the rest
    # of the file (issue #640).
    source = terminator.join((
        'alert(gettext("x"));',
        'var e = />/g;',
        'alert(gettext("y"));',
    ))
    tokens = list(jslexer.tokenize(source))
    assert any(kind == 'string' and value == '"y"' for kind, value, _ in tokens)
    for kind, value, _lineno in tokens:
        assert not any(t in value for t in LINE_TERMINATORS), \
            f"{kind} token spans lines: {value!r}"


@pytest.mark.parametrize("terminator", LINE_TERMINATORS)
def test_regexp_literal_cannot_continue_after_a_backslash(terminator):
    # A backslash is not a line continuation inside a regexp literal, so the
    # literal must not be continued past the terminator either.
    source = f'var e = /a\\{terminator}b/;\nalert(gettext("still here"));'
    tokens = list(jslexer.tokenize(source))
    assert any(kind == 'string' and value == '"still here"' for kind, value, _ in tokens)
    for kind, value, _lineno in tokens:
        if kind != 'regexp':
            continue
        assert not any(t in value for t in LINE_TERMINATORS), f"regexp spans lines: {value!r}"


def test_ordinary_regexp_literals_still_match():
    # Escaped slashes and flags are unaffected by the line terminator guard.
    tokens = list(jslexer.tokenize(r'var e = /a\/b+c/gi;'))
    assert ('regexp', r'/a\/b+c/gi', 1) in tokens
