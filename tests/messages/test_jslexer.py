import pytest

from babel.messages import jslexer


def test_unquote():
    assert jslexer._unquote_string('""') == ''
    assert jslexer._unquote_string(r'"h\u00ebllo"') == "hëllo"
    assert jslexer._unquote_string(r'"h\xebllo"') == "hëllo"
    assert jslexer._unquote_string(r'"\xebb"') == "ëb"
    assert jslexer._unquote_string(r'"a\vb"') == "a\vb"
    assert jslexer._unquote_string(r'"\\v"') == r"\v"


def test_dollar_in_identifier():
    assert list(jslexer._tokenize('dollar$dollar')) == [('name', 'dollar$dollar', 1)]


def test_dotted_name():
    assert list(jslexer._tokenize("foo.bar(quux)", dotted=True)) == [
        ('name', 'foo.bar', 1),
        ('operator', '(', 1),
        ('name', 'quux', 1),
        ('operator', ')', 1),
    ]


def test_dotted_name_end():
    assert list(jslexer._tokenize("foo.bar", dotted=True)) == [
        ('name', 'foo.bar', 1),
    ]


def test_template_string():
    assert list(jslexer._tokenize("gettext `foo\"bar\"p`", template_string=True)) == [
        ('name', 'gettext', 1),
        ('template_string', '`foo"bar"p`', 1),
    ]


def test_jsx():
    assert list(jslexer._tokenize("""
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


def test_deprecated_functions():
    with pytest.warns(DeprecationWarning, match="jslexer.tokenize"):
        tokens = list(jslexer.tokenize("foo / 2"))
    assert tokens == list(jslexer._tokenize("foo / 2"))
    with pytest.warns(DeprecationWarning, match="jslexer.get_rules"):
        rules = jslexer.get_rules(jsx=False, dotted=False, template_string=False)
    assert rules == jslexer._get_rules(jsx=False, dotted=False, template_string=False)
    with pytest.warns(DeprecationWarning, match="jslexer.indicates_division"):
        assert jslexer.indicates_division(tokens[0])
    with pytest.warns(DeprecationWarning, match="jslexer.unquote_string"):
        assert jslexer.unquote_string('"a\\tb"') == "a\tb"
