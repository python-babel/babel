from io import BytesIO

import pytest

from babel.messages import extract


def test_simple_extract():
    buf = BytesIO(b"""\
msg1 = _('simple')
msg2 = gettext('simple')
msg3 = ngettext('s', 'p', 42)
    """)
    messages = \
        list(extract.extract('javascript', buf, extract.DEFAULT_KEYWORDS,
                             [], {}))

    assert messages == [(1, 'simple', [], None),
                        (2, 'simple', [], None),
                        (3, ('s', 'p'), [], None)]


def test_various_calls():
    buf = BytesIO(b"""\
msg1 = _(i18n_arg.replace(/"/, '"'))
msg2 = ungettext(i18n_arg.replace(/"/, '"'), multi_arg.replace(/"/, '"'), 2)
msg3 = ungettext("Babel", multi_arg.replace(/"/, '"'), 2)
msg4 = ungettext(i18n_arg.replace(/"/, '"'), "Babels", 2)
msg5 = ungettext('bunny', 'bunnies', parseInt(Math.random() * 2 + 1))
msg6 = ungettext(arg0, 'bunnies', rparseInt(Math.random() * 2 + 1))
msg7 = _(hello.there)
msg8 = gettext('Rabbit')
msg9 = dgettext('wiki', model.addPage())
msg10 = dngettext(domain, 'Page', 'Pages', 3)
""")
    messages = \
        list(extract.extract('javascript', buf, extract.DEFAULT_KEYWORDS, [],
                             {}))
    assert messages == [
        (5, ('bunny', 'bunnies'), [], None),
        (8, 'Rabbit', [], None),
        (10, ('Page', 'Pages'), [], None),
    ]


def test_message_with_line_comment():
    buf = BytesIO("""\
// NOTE: hello
msg = _('Bonjour à tous')
""".encode('utf-8'))
    messages = list(extract.extract_javascript(buf, ('_',), ['NOTE:'], {}))
    assert messages[0][2] == 'Bonjour à tous'
    assert messages[0][3] == ['NOTE: hello']


def test_message_with_multiline_comment():
    buf = BytesIO("""\
/* NOTE: hello
and bonjour
  and servus */
msg = _('Bonjour à tous')
""".encode('utf-8'))
    messages = list(extract.extract_javascript(buf, ('_',), ['NOTE:'], {}))
    assert messages[0][2] == 'Bonjour à tous'
    assert messages[0][3] == ['NOTE: hello', 'and bonjour', '  and servus']


def test_ignore_function_definitions():
    buf = BytesIO(b"""\
function gettext(value) {
return translations[language][value] || value;
}""")

    messages = list(extract.extract_javascript(buf, ('gettext',), [], {}))
    assert not messages


def test_misplaced_comments():
    buf = BytesIO(b"""\
/* NOTE: this won't show up */
foo()

/* NOTE: this will */
msg = _('Something')

// NOTE: this will show up
// too.
msg = _('Something else')

// NOTE: but this won't
bar()

_('no comment here')
""")
    messages = list(extract.extract_javascript(buf, ('_',), ['NOTE:'], {}))
    assert messages[0][2] == 'Something'
    assert messages[0][3] == ['NOTE: this will']
    assert messages[1][2] == 'Something else'
    assert messages[1][3] == ['NOTE: this will show up', 'too.']
    assert messages[2][2] == 'no comment here'
    assert messages[2][3] == []


JSX_SOURCE = b"""
class Foo {
    render() {
        const value = gettext("hello");
        return (
            <option value="val1">{ i18n._('String1') }</option>
            <option value="val2">{ i18n._('String 2') }</option>
            <option value="val3">{ i18n._('String 3') }</option>
            <option value="val4">{ _('String 4') }</option>
            <option>{ _('String 5') }</option>
        );
    }
"""
EXPECTED_JSX_MESSAGES = ["hello", "String1", "String 2", "String 3", "String 4", "String 5"]


@pytest.mark.parametrize("jsx_enabled", (False, True))
def test_jsx_extraction(jsx_enabled):
    buf = BytesIO(JSX_SOURCE)
    messages = [m[2] for m in extract.extract_javascript(buf, ('_', 'gettext'), [], {"jsx": jsx_enabled})]
    if jsx_enabled:
        assert messages == EXPECTED_JSX_MESSAGES
    else:
        assert messages != EXPECTED_JSX_MESSAGES


def test_dotted_keyword_extract():
    buf = BytesIO(b"msg1 = com.corporate.i18n.formatMessage('Insert coin to continue')")
    messages = list(
        extract.extract('javascript', buf, {"com.corporate.i18n.formatMessage": None}, [], {}),
    )

    assert messages == [(1, 'Insert coin to continue', [], None)]


def test_template_string_standard_usage():
    buf = BytesIO(b"msg1 = gettext(`Very template, wow`)")
    messages = list(
        extract.extract('javascript', buf, {"gettext": None}, [], {}),
    )

    assert messages == [(1, 'Very template, wow', [], None)]


def test_template_string_tag_usage():
    buf = BytesIO(b"function() { if(foo) msg1 = i18n`Tag template, wow`; }")
    messages = list(
        extract.extract('javascript', buf, {"i18n": None}, [], {}),
    )

    assert messages == [(1, 'Tag template, wow', [], None)]


def test_inside_template_string():
    buf = BytesIO(b"const msg = `${gettext('Hello')} ${user.name}`")
    messages = list(
        extract.extract('javascript', buf, {"gettext": None}, [], {'parse_template_string': True}),
    )

    assert messages == [(1, 'Hello', [], None)]


def test_inside_template_string_with_linebreaks():
    buf = BytesIO(b"""\
const userName = gettext('Username')
const msg = `${
gettext('Hello')
} ${userName} ${
gettext('Are you having a nice day?')
}`
const msg2 = `${
gettext('Howdy')
} ${userName} ${
gettext('Are you doing ok?')
}`
""")
    messages = list(
        extract.extract('javascript', buf, {"gettext": None}, [], {'parse_template_string': True}),
    )

    assert messages == [(1, 'Username', [], None), (3, 'Hello', [], None), (5, 'Are you having a nice day?', [], None), (8, 'Howdy', [], None), (10, 'Are you doing ok?', [], None)]


def test_inside_nested_template_string():
    buf = BytesIO(b"const msg = `${gettext('Greetings!')} ${ evening ? `${user.name}: ${gettext('This is a lovely evening.')}` : `${gettext('The day is really nice!')} ${user.name}`}`")
    messages = list(
        extract.extract('javascript', buf, {"gettext": None}, [], {'parse_template_string': True}),
    )

    assert messages == [(1, 'Greetings!', [], None), (1, 'This is a lovely evening.', [], None), (1, 'The day is really nice!', [], None)]

def test_nested_gettext_calls():
    buf = BytesIO(b"""\
gettext("Hello %s", gettext("User"));
// NOTE: Double
gettext("Hello %(user)s", { user: gettext("User") });
// NOTE: Non Preceding

gettext("Hello %s", dummy.dummyFunction(gettext("User")));
gettext(
    "Hello %(user)s",
    { user: dummy.dummyFunction(gettext("User")) },
);
// NOTE: Another Comment
gettext("Random %s", gettext`Shizzle`);
""")
    messages = list(
        extract.extract('javascript', buf, {"gettext": None}, ['NOTE:'], {}),
    )

    assert messages == [
        (1, 'User', [], None),
        (1, 'Hello %s', [], None),
        (3, 'User', ['NOTE: Double'], None),
        (3, 'Hello %(user)s', ['NOTE: Double'], None),
        (6, 'User', [], None),
        (6, 'Hello %s', [], None),
        (9, 'User', [], None),
        (8, 'Hello %(user)s', [], None),
        (12, 'Shizzle', ['NOTE: Another Comment'], None),
        (12, 'Random %s', ['NOTE: Another Comment'], None),
    ]
