import pickle

import pytest

from babel.numbers import _cached_parse_pattern, format_decimal, parse_pattern


def test_number_patterns_remain_independent_and_pickleable():
    first = parse_pattern('#,##0.00')
    expected = vars(first).copy()
    first.prefix = ('changed', 'negative')
    first.frac_prec = (0, 0)
    second = parse_pattern('#,##0.00')
    assert first is not second
    assert vars(second) == expected
    assert vars(pickle.loads(pickle.dumps(second))) == expected
    assert format_decimal(1234.5, '#,##0.00', locale='en_US') == '1,234.50'
    assert parse_pattern(first) is first


def test_number_pattern_string_subclass_is_not_cached():
    class Pattern(str):
        __hash__ = None
        calls = 0

        def __contains__(self, item):
            self.calls += 1
            return super().__contains__(item)

    pattern = Pattern('0.00')
    first = parse_pattern(pattern)
    calls = pattern.calls
    second = parse_pattern(pattern)
    assert pattern.calls == 2 * calls
    assert vars(first) == vars(second)
    assert second.pattern is pattern


@pytest.mark.parametrize('pattern', [None, [], {}, 0, b'0'])
def test_number_pattern_unsupported_inputs(pattern):
    with pytest.raises(TypeError):
        parse_pattern(pattern)


def test_number_pattern_cache_is_bounded():
    _cached_parse_pattern.cache_clear()
    for i in range(1100):
        parse_pattern(f"'{i}'0.00")
    assert _cached_parse_pattern.cache_info().currsize == 1024
