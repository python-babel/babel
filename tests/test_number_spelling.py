import os
import sys

import pytest

from babel import numbers, rbnf

soft_hyphen = '\xad'


def test_basic():
    x = rbnf.RuleBasedNumberFormat.negotiate('hu_HU')
    assert str(x._locale) == 'hu'
    assert 'spellout-numbering' in x.available_rulesets


@pytest.mark.all_rbnf_locales
def test_negotiation(locale):
    negotiated_speller = rbnf.RuleBasedNumberFormat.negotiate(locale)
    negotiated_locale = negotiated_speller._locale

    # test groups
    for k in negotiated_locale._data['rbnf_rules']:
        assert k in rbnf.RuleBasedNumberFormat.group_types

    negotiated_speller.match_ruleset("numbering")

    with pytest.raises(rbnf.RulesetNotFound):
        negotiated_speller.match_ruleset("nonexistent")


def test_tokenization():
    x = list(rbnf.tokenize("text[opt];"))
    res = [
        rbnf.TokenInfo(type=1, reference='text', optional=False),
        rbnf.TokenInfo(type=1, reference='opt', optional=True),
    ]
    assert x == res

    rbnf.tokenize("→→→;")  # should not raise

    with pytest.raises(ValueError, match=r"Unable to.*"):
        list(rbnf.tokenize("==="))

    with pytest.warns(SyntaxWarning, match=r"Reference parsing error.*"):
        list(rbnf.tokenize("←bad←;"))


@pytest.mark.all_rbnf_locales
def test_xml_parsing(locale):
    """
    All the rues implicitly go through the arsing during CLDR import.

    This tests replicates the parsing for the English locale to
    add coverage to the parsing parts of the code.
    """
    from xml.etree import ElementTree

    rules = numbers.get_rbnf_rules(locale)

    assert rules

    rbnf_file = f"cldr/cldr-common-47.0/common/rbnf/{locale}.xml"

    assert os.path.isfile(rbnf_file)

    data = {}

    rbnf_tree = ElementTree.parse(rbnf_file)
    rbnf.parse_rbnf_rules(data, rbnf_tree)

    assert 'rbnf_rules' in data

    if 'SpelloutRules' in data['rbnf_rules']:
        for rs in data['rbnf_rules']['SpelloutRules']:
            assert rs.rules
            assert str(rs) != ""
            for rule in rs.rules:
                assert str(rule) != ""


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
    except RecursionError:
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
