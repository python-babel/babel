# -*- coding: utf-8 -*-

from babel.messages import jslexer


def test_unquote():
    assert jslexer.unquote_string('""') == ''
    assert jslexer.unquote_string(r'"h\u00ebllo"') == u"hëllo"


def test_dotted_name():
    assert list(jslexer.tokenize_dotted("foo.bar(quux)")) == [
        ('dotted_name', 'foo.bar', 1),
        ('operator', '(', 1),
        ('name', 'quux', 1),
        ('operator', ')', 1)
    ]


def test_dotted_name_end():
    assert list(jslexer.tokenize_dotted("foo.bar")) == [
        ('dotted_name', 'foo.bar', 1),
    ]
