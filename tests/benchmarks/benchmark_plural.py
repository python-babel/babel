from __future__ import annotations

import pytest

from babel import Locale
from babel.plural import PluralRule, to_gettext

# A synthetic ruleset, comparable in complexity to real CLDR rule sets.
RULES = {
    "one": "v in 0 and i mod 10 in 1..2 and i mod 100 not in 11..12",
    "few": "v in 0 and i mod 10 in 3..6",
    "many": "v in 0 and i mod 10 in 7..9 or v in 0 and i mod 100 in 11..12",
}


@pytest.fixture
def plural_rule() -> PluralRule:
    return PluralRule(RULES)


def test_plural_rule_parse(benchmark):
    assert benchmark(lambda: PluralRule(RULES).tags) == frozenset({"one", "few", "many"})


def test_plural_rule_call_int(benchmark, plural_rule: PluralRule):
    assert benchmark(lambda: plural_rule(21)) == "one"


def test_plural_rule_call_float(benchmark, plural_rule):
    # Floats go through the Decimal path in extract_operands.
    assert benchmark(lambda: plural_rule(2.5)) == "other"


def test_locale_plural_form(benchmark):
    locale = Locale.parse("fi")
    assert benchmark(lambda: locale.plural_form(1)) == "one"


def test_to_gettext(benchmark):
    expected = to_gettext(RULES)
    assert expected.startswith("nplurals=4; plural=(")
    assert benchmark(lambda: to_gettext(RULES)) == expected
