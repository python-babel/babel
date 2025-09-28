import sys

import pytest

from babel import numbers, rbnf
from babel.localedata import locale_identifiers

soft_hyphen = '\xad'


def test_basic():
    x = rbnf.RuleBasedNumberFormat.negotiate('hu_HU')
    assert str(x._locale) == 'hu'
    assert 'spellout-numbering' in x.available_rulesets


def test_negotiation():
    for lid in locale_identifiers():
        try:
            loc = rbnf.RuleBasedNumberFormat.negotiate(lid)._locale
        except rbnf.RulesetNotFound:
            # generate warning if necessary
            continue
        # test groups
        for k in loc._data['rbnf_rules']:
            assert k in rbnf.RuleBasedNumberFormat.group_types


def test_tokenization():
    x = list(rbnf.tokenize("text[opt];"))
    res = [
        rbnf.TokenInfo(type=1, reference='text', optional=False),
        rbnf.TokenInfo(type=1, reference='opt', optional=True),
    ]
    assert x == res


def test_xml_parsing():
    """
    all the rules should be able to go through the parser and tokenizer
    made up some rules and run the tokenizer on them

    TODO
    read data from all the locales that have rbnf_rules defined
    all the raw rules should be in a specific structure based
    on the XML specification
    """
    assert True


def test_compute_divisor():
    for rule, divisor in (
        (1001, 1000),
        (1_000_001, 1_000_000),
        (1_000_000_001, 1_000_000_000),
        (1_000_000_000_000_000_001, 1_000_000_000_000_000_000),
        (1001, 1000),
        (1_000_000, 1_000_000),
        (1_000_000_000, 1_000_000_000),
        (1_000_000_000_000_000_000, 1_000_000_000_000_000_000),
    ):
        assert rbnf.compute_divisor(rule, 10) == divisor


@pytest.mark.all_rbnf_locales
@pytest.mark.parametrize('ruleset', (None, 'year', 'ordinal'))
def test_spelling_smoke(locale, ruleset):
    try:
        assert numbers.spell_number(2020, locale=locale, ruleset=ruleset)
    except rbnf.RulesetNotFound:  # Not all locales have all rulesets, so skip the smoke test.
        pass
    except RecursionError:  # Some combinations currently fail with this :(
        pytest.xfail(f'Locale {locale}, ruleset {ruleset}')


@pytest.mark.all_rbnf_locales
@pytest.mark.skipif(sys.version_info < (3, 11), reason="requires python3.11 or higher for tomllib")
def test_spelling_smoke_toml(locale):
    import tomllib

    speller = rbnf.RuleBasedNumberFormat.negotiate(locale)

    with open(f"tests/rbnf_test_cases/{locale}.toml", "rb") as f:
        test_data = tomllib.load(f)

        for ruleset, test_cases in test_data.items():
            if ruleset in ("locale", "version", "generated"):
                continue
            for number, expected in test_cases.items():
                try:
                    result = speller.format(number, ruleset=ruleset)
                except rbnf.RBNFError as e:
                    print(f"RBNFError for {locale} in {ruleset} spelling {number}: {e}")
                    continue
                assert result == expected, f"{locale} {ruleset} {number}: expected {expected}, got {result}"
