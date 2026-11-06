from io import BytesIO

import pytest

from babel.messages.extract import extract


@pytest.mark.parametrize('prefix', ['', 'async ', 'const example = '])
@pytest.mark.parametrize('dotted', [False, True])
@pytest.mark.parametrize(
    'between',
    [' ', '* ', ' /* comment */ ', ' /* comment */ * /* comment */ '],
)
def test_ignore_named_function_parameters(prefix, dotted, between):
    source = (
        prefix + 'function' + between + 'gettext(value="definition") {}; gettext("visible");'
    )
    keywords = {'gettext': None, 'i18n.gettext' if dotted else '__unused__': None}
    messages = extract('javascript', BytesIO(source.encode()), keywords=keywords, options={})
    assert list(messages) == [
        (1, 'visible', [], None),
    ]


@pytest.mark.parametrize(
    'source',
    [
        'obj.function * gettext("visible");',
        'obj. /* comment */ function * gettext("visible");',
        'const example = function(value=gettext("visible")) {};',
        'function* example(value=gettext("visible")) {}',
        'function gettext(value) { return other(gettext("visible")); }',
        'const values = [...function gettext(value="definition") {}]; gettext("visible");',
        '1..function * gettext("visible");',
        '1.. /* comment */ function * gettext("visible");',
        '1. /* comment */ .function * gettext("visible");',
    ],
)
@pytest.mark.parametrize('dotted', [False, True])
def test_real_calls_around_function_syntax_are_extracted(source, dotted):
    keywords = {'gettext': None, 'i18n.gettext' if dotted else '__unused__': None}
    messages = extract('javascript', BytesIO(source.encode()), keywords=keywords, options={})
    assert list(messages) == [
        (1, 'visible', [], None),
    ]
