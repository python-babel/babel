import pytest

from babel.messages.pofile import _NormalizedString


def test_normalized_string():
    ab1 = _NormalizedString('"a"', '"b" ')
    ab2 = _NormalizedString('"a"', ' "b"')
    ac1 = _NormalizedString('"a"', '"c"')
    ac2 = _NormalizedString('  "a"', '"c"  ')
    z = _NormalizedString()
    assert ab1 == ab2 and ac1 == ac2  # __eq__
    assert ab1 < ac1  # __lt__
    assert ac1 > ab2  # __gt__
    assert ac1 >= ac2  # __ge__
    assert ab1 <= ab2  # __le__
    assert ab1 != ac1  # __ne__
    assert not z  # __nonzero__ / __bool__
    assert sorted([ab1, ab2, ac1]) == [ab1, ab2, ac1] # sorted() is stable


@pytest.mark.parametrize(
    "original, denormalized",
    (
        ('""', ""),
        ('"a"', "a"),
        ('"a\\n"', "a\n"),
        ('"a\\r"', "a\r"),
        ('"a\\t"', "a\t"),
        ('"a\\""', 'a"'),
        ('"a\\\\"', "a\\"),
    ),
)
def test_denormalized_simple_normalized_string(original, denormalized):
    assert denormalized == _NormalizedString(original).denormalize()

@pytest.mark.parametrize(
    "originals, denormalized",
    (
        (('"a"', '"b"'), "ab"),
        (('"a" ', '"b"'), "ab"),
        (('"ab"', '""'), "ab"),
        (('"ab"', '"c"'), "abc"),
        (('"a"', '     "bc"'), "abc"),
    ),
)
def test_denormalized_multi_normalized_string(originals, denormalized):
    assert denormalized == _NormalizedString(*originals).denormalize()
