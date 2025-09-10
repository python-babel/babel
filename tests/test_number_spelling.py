import unittest
import pytest

from babel import numbers
from babel import rbnf
from babel.core import get_global
from babel.localedata import locale_identifiers

soft_hyphen = '\xad'

class TestRuleEngine(unittest.TestCase):
    """
    Test everything related to the rules engine
    """
    def test_basic(self):
        x = rbnf.RuleBasedNumberFormat.negotiate('hu_HU')
        assert str(x._locale) == 'hu'
        assert 'spellout-numbering' in x.available_rulesets


    def test_negotiation(self):
        valid_ruleset_groups = ("SpelloutRules", "OrdinalRules", "NumberingSystemRules")
        
        for lid in locale_identifiers():
            loc = rbnf.RuleBasedNumberFormat.negotiate(lid)._locale
            if loc is None:
                # generate warning if necessary
                pass
            else:
                # test groups
                for k in loc._data['rbnf_rules']:
                    assert k in valid_ruleset_groups


    def test_tokenization(self):

        x = list(rbnf.tokenize("text[opt];"))
        res = [
            rbnf.TokenInfo(type=1, reference='text', optional=False),
            rbnf.TokenInfo(type=1, reference='opt', optional=True),
        ]
        assert x == res


    def test_xml_parsing(self):
        """
        all the rules should be able to go through the parser and tokenizer
        made up some rules and run the tokenizer on them

        TODO
        read data from all the locales that have rbnf_rules defined
        all the raw rules should be in a specific structure based
        on the XML specification
        """
        assert True


class TestSpelling(unittest.TestCase):
    """
    Locale specific tests
    """
    def test_hu_HU_cardinal(self):
        def _spell(x):
            return numbers.spell_number(x, locale='hu_HU').replace(soft_hyphen, '')

        assert _spell(0) == "nulla"
        assert _spell(1) == "egy"
        assert _spell(2) == "kettő"
        assert _spell(3) == "három"
        assert _spell(10) == "tíz"
        assert _spell(20) == "húsz"
        # assert _spell('-0') == "mínusz nulla"
        # assert _spell(123.25) == "százhuszonhárom egész huszonöt század"
        assert _spell(-12) == "mínusz tizenkettő"
        # assert _spell(23457829) == "huszonhárommillió-négyszázötvenhétezer-nyolcszázhuszonkilenc"
        assert _spell(1950) == "ezerkilencszázötven"
        # only soft hyphens in the rules !!!
        # assert _spell(2001) == "kétezer-egy"
        # assert _spell('1999.2386') == "ezerkilencszázkilencvenkilenc egész kétezer-háromszáznyolcvanhat tízezred"
        # assert _spell(-.199923862) == "mínusz nulla egész százkilencvenkilencezer-kilencszázhuszonnégy milliomod"
        # assert _spell(-.199923862) == "kerekítve mínusz nulla egész ezerkilencszázkilencvenkilenc tízezred"
        # assert _spell(.4326752) == "nulla egész negyvenhárom század"


    def test_hu_HU_ordinal(self):
        def _spell(x):
            return numbers.spell_number(x, locale='hu_HU', ordinal=True).replace(soft_hyphen, '')

        assert _spell(0) == "nulla"
        # assert _spell(0) == "nulladik"
        assert _spell(1) == "első"
        assert _spell(2) == "második"
        assert _spell(3) == "harmadik"
        assert _spell(10) == "tizedik"
        assert _spell(20) == "huszadik"
        assert _spell(30) == "harmincadik"
        assert _spell(-12) == "mínusz tizenkettedik"
        # assert _spell(23457829) == "huszonhárommilliónégyszázötvenhétezernyolcszázhuszonkilencedik"  # wrong mutiple cldr errors
        # assert _spell(23457829) == "huszonhárommillió-négyszázötvenhétezer-nyolcszázhuszonkilencedik"
        assert _spell(1100) == "ezerszázadik"
        assert _spell(1950) == "ezerkilencszázötvenedik"
        # assert _spell(2001) == "kétezer-egyedik"


    def test_en_GB_cardinal(self):
        def _spell(x):
            return numbers.spell_number(x, locale='en_GB').replace(soft_hyphen, '')

        assert _spell(0) == "zero"
        assert _spell(1) == "one"
        assert _spell(2) == "two"
        assert _spell(3) == "three"
        # assert _spell('-0') == "minus zero"
        # assert _spell(123.25) == "one hundred and twenty-three point twenty-five hundredths"
        assert _spell(-12) == "minus twelve"
        assert _spell(23457829) == "twenty-three million four hundred fifty-seven thousand eight hundred twenty-nine"
        # assert _spell(23457829) == "twenty-three million four hundred and fifty-seven thousand eight hundred and twenty-nine"
        assert _spell(1950) == "one thousand nine hundred fifty"
        # assert _spell(1950) == "one thousand nine hundred and fifty"
        assert _spell(2001) == "two thousand one"
        # assert _spell('1999.238') == "one thousand nine hundred and ninety-nine point two hundred and thirty-eight thousandths"
        # assert _spell(-.199923862, precision=3, state_rounded=True) == "approximately minus zero point two tenths"
        # assert _spell(-.1) == "minus zero point one tenth" # float to string conversion preserves precision


    def test_en_GB_ordinal(self):
        def _spell(x):
            return numbers.spell_number(x, locale='en_GB', ordinal=True).replace(soft_hyphen, '')

        assert _spell(0) == "zeroth"
        assert _spell(1) == "first"
        assert _spell(2) == "second"
        assert _spell(3) == "third"
        assert _spell(4) == "fourth"
        assert _spell(5) == "fifth"
        assert _spell(6) == "sixth"
        assert _spell(7) == "seventh"
        assert _spell(8) == "eighth"
        assert _spell(9) == "ninth"
        assert _spell(10) == "tenth"
        assert _spell(11) == "eleventh"
        assert _spell(12) == "twelfth"
        assert _spell(13) == "thirteenth"
        assert _spell(20) == "twentieth"
        assert _spell(30) == "thirtieth"
        assert _spell(40) == "fortieth"
        # assert _spell(40) == "fourtieth"
        assert _spell(-12) == "minus twelfth"
        # assert _spell(23457829) == "twenty-three million four hundred fifty-seven thousand eight hundred twenty-ninth"  # apostrophes
        # assert _spell(23457829) == "twenty-three million four hundred and fifty-seven thousand eight hundred and twenty-ninth"
        assert _spell(1950) == "one thousand nine hundred fiftieth"
        # assert _spell(1950) == "one thousand nine hundred and fiftieth"
        assert _spell(2001) == "two thousand first"



# def test_hu_HU_error():
#     with pytest.raises(exceptions.TooBigToSpell) as excinfo:
#         _spell(10**66, ordinal=True)

#     with pytest.raises(exceptions.PrecisionError) as excinfo:
#         _spell(.4326752, locale='hu_HU', precision=7)

#     with pytest.raises(exceptions.PrecisionError) as excinfo:
#         _spell(.4326752)

#     with pytest.raises(exceptions.NoFractionOrdinalsAllowed) as excinfo:
#         _spell('1999.23862', ordinal=True)

# def test_en_GB_error():
#     with pytest.raises(exceptions.TooBigToSpell) as excinfo:
#         _spell(10**24, ordinal=True, locale='en_GB')

#     with pytest.raises(exceptions.PrecisionError) as excinfo:
#         _spell(.4326752, locale='en_GB', precision=4)

#     with pytest.raises(exceptions.PrecisionError) as excinfo:
#         _spell(.4326752, locale='en_GB')

#     with pytest.raises(exceptions.NoFractionOrdinalsAllowed) as excinfo:
#         _spell('1999.23', ordinal=True, locale='en_GB')

