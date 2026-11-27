from io import BytesIO

import pytest

from babel.messages.extract import extract
from babel.messages.jslexer import tokenize


@pytest.mark.parametrize('value', ['`1`', '`1${2}`', 'String.raw`1`'])
def test_division_after_template_strings(value):
    source = f'{value} / 2; gettext("visible") / 3;'
    assert list(extract('javascript', BytesIO(source.encode()), options={})) == [
        (1, 'visible', [], None),
    ]
    operators = [token.value for token in tokenize(source) if token.type == 'operator']
    assert operators.count('/') == 2


@pytest.mark.parametrize('value', ['1', '"1"', '(1)', '[1]', '/one/'])
def test_division_after_other_values(value):
    source = f'{value} / 2; gettext("visible") / 3;'
    assert list(extract('javascript', BytesIO(source.encode()), options={})) == [
        (1, 'visible', [], None),
    ]


def test_regexp_after_template_statement():
    source = '`1`; /gettext("hidden")/; gettext("visible");'
    assert list(extract('javascript', BytesIO(source.encode()), options={})) == [
        (1, 'visible', [], None),
    ]
    regexps = [token.value for token in tokenize(source) if token.type == 'regexp']
    assert regexps == ['/gettext("hidden")/']
