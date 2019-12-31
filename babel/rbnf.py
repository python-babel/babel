# -*- coding: utf-8 -*-
"""
babel.rbnf
~~~~~~~~~~

Locale dependent spelling of numbers.

Documentation:
-   http://www.unicode.org/reports/tr35/tr35-47/tr35-numbers.html#Rule-Based_Number_Formatting
-   http://www.icu-project.org/apiref/icu4c/classRuleBasedNumberFormat.html

Examples
-   http://userguide.icu-project.org/formatparse/numbers/rbnf-examples
-   http://source.icu-project.org/repos/icu/trunk/icu4j/demos/src/com/ibm/icu/dev/demo/rbnf/RbnfSampleRuleSets.java

    
"""
# Dev notes
#
# Reloading cldr:
# python ./scripts/import_cldr.py ./cldr/cldr-core-35.1/common/ -f
# 
# Tokenization is inspired by Ka-Ping Yee's tokenize library

# Undocumented syntax (←%rule-name←←)
# Trac ticket filed for CLDR update PL rbnf
#     http://unicode.org/cldr/trac/ticket/10544
# Maybe the syntax need to be supported:
#     http://bugs.icu-project.org/trac/ticket/13264
# Original request for Hebrew (currently not used in Hebrew):
#     http://bugs.icu-project.org/trac/ticket/4039

from __future__ import unicode_literals

import re
import math
import decimal
import collections
import warnings

from babel.core import Locale, get_global

TEXT_TOKEN = 1
INTEGRAL_TOKEN = 2
REMAINDER_TOKEN = 3
PREVIOUS_TOKEN = 4
SUBSTITUTION_TOKEN = 5
PLURAL_TOKEN = 6
OPT_START = 7
OPT_END = 8

token_regexes = [
    (t, re.compile(r))
    for (t, r) in [
        (PLURAL_TOKEN, r"\$\((.+)\)\$"),
        (INTEGRAL_TOKEN, r"←([^←[]*)←(←?)"),
        (PREVIOUS_TOKEN, r"→→→"),
        (REMAINDER_TOKEN, r"→([^→[]*)→"),
        (SUBSTITUTION_TOKEN, r"=([^=[]+)="),
        (OPT_START, r"\["),
        (OPT_END, r"\]"),
        (TEXT_TOKEN, r"[^[\]=→←]+"),
    ]
]

INTERNAL_REF = 1
PRIVATE_REF = 2
PUBLIC_REF = 3
PLURAL_REF = 4
DECIMAL_REF = 5

REFERENCE_TOKENS = (INTEGRAL_TOKEN, REMAINDER_TOKEN, SUBSTITUTION_TOKEN)

NEGATIVE_NUMBER_RULE = '-x'
IMPROPER_FRACTION_RULE = 'x.x'
PROPER_FRACTION_RULE = '0.x'
MASTER_RULE = 'x.0'
INFINITY_RULE = 'Inf'
NOT_A_NUMBER_RULE = 'NaN'
SPECIAL_FRACTION_RULE = 'x,x'  # there are other options but not existent in CLDR


# locale.number_symbols['decimal']
# normal rule means a number is specified


class RBNFError(Exception): pass
class TokenizationError(RBNFError): pass
class RulesetNotFound(RBNFError): pass
class RuleNotFound(RBNFError): pass

TokenInfo = collections.namedtuple('TokenInfo', 'type reference optional')


def tokenize(text):
    """
    Each rule has a list of tokens
    
    Text parsed by matching a list of regular expressions
    against the beginning of the text. If the regex match
    a token is generated, and we continue with the rest of
    the text.

    Some tokens are optional if they are in squared
    brackets. From regular expressions for the beginning and
    end of the optional section no tokens are generated.
    Instead, all the tokens inside the optional section are
    flagged as optional.
    
    Some of the tokens are referencing other rulesets by name.
    This information is stored in the token along with the type
    of reference.

    """
    # remove unnecessary syntax (only used in the non-xml form)
    if text.endswith(";"):
        text = text[:-1]
    if text.startswith("'"):
        text = text[1:]

    optional = False

    while text:
        stop = True
        # print("TEXT: ", text)
        for tok, regex in token_regexes:
            # print(token, regex)
            match = regex.match(text)
            if match:
                stop = False
                text = text[match.end():]
                if tok == OPT_START:
                    optional = True
                elif tok == OPT_END:
                    optional = False
                else:
                    token = _gen_token(tok, match, optional)
                    if token:
                        yield token
                break  # always start searching with the first regex
        if stop:
            raise ValueError(text)


def _gen_token(tok, match, optional):
    # remove this if CLDR is updated based on ticket
    # http://unicode.org/cldr/trac/ticket/10544
    if tok == INTEGRAL_TOKEN and match.group(2) == '←':
        warnings.warn('Unsupported syntax ←...←←', SyntaxWarning)

    if tok in REFERENCE_TOKENS:
        reference = _parse_reference(match.group(1))
        return TokenInfo(tok, reference, optional)

    # currently only `en` has this
    if tok == PLURAL_TOKEN:
        return TokenInfo(tok, (PLURAL_REF, match.group(1)), optional)

    if tok == PREVIOUS_TOKEN:
        return TokenInfo(tok, None, optional)

    if tok == TEXT_TOKEN:
        return TokenInfo(tok, match.group(0), optional)


def _parse_reference(string):
    if string == "":
        return INTERNAL_REF, ""
    if string.startswith('%%'):
        return PRIVATE_REF, string[2:]
    if string.startswith('%'):
        return PUBLIC_REF, string[1:]
    if string[0] in '0#':
        return DECIMAL_REF, string
    warnings.warn('Reference parsing error: %s' % string, SyntaxWarning)
    return INTERNAL_REF, ""  # defaults to this


class RuleBasedNumberFormat(object):
    """
    RuleBasedNumberFormat's behavior consists of one or more rule sets

    The first ruleset in a locale is the default ruleset.
    The substitution descriptor (i.e., the text between the token characters)
    may take one of three forms:
    :a rule set name:
        Perform the mathematical operation on the number, and format the result
        using the named rule set.
    :a DecimalFormat pattern:
        Perform the mathematical operation on the number, and format the
        result using a DecimalFormat with the specified pattern. The
        pattern must begin with 0 or #.
    :nothing:
        Perform the mathematical operation on the number, and format the
        result using the rule set containing the current rule, except:
        
        -   You can't have an empty substitution descriptor with
            a == substitution.
        -   If you omit the substitution descriptor in a >> substitution
            in a fraction rule, format the result one digit at a time
            using the rule set containing the current rule.
        -   If you omit the substitution descriptor in a << substitution
            in a rule in a fraction rule set, format the result using
            the default rule set for this formatter.
    """
    group_types = ('SpelloutRules', 'OrdinalRules', 'NumberingSystemRules')

    # spell number should go for Spelloutrules
    # make interface for the other two groups

    def __init__(self, locale, group='SpelloutRules'):
        self._locale = locale
        self._group = group

    @property
    def rulesets(self):
        return self._locale._data['rbnf_rules'][self._group]

    @property
    def available_rulesets(self):
        """list available public rulesets"""
        return [r.name for r in self.rulesets if not r.private]


    def format(self, number, ordinal=False, year=False, ruleset=None, **kwargs):
        """spell an actual number (int/float/decimal)
        
        Search available_rulesets for an entry point
        default is `spellout-numbering`.

        If year is True: use spellout-numbering-year
        If ordinal is True: use spellout-ordinal
        If year and ordinal both True: raise error
        
        TODO
        If no `spellout-ordinal`:
            if has `spellout-ordinal-*`: use first one, issue warning

        """
        if ordinal and year:
            raise ValueError('both ordinal and year is not possible')
        if ordinal:
            search = ruleset or 'spellout-ordinal'
        elif year:
            search = ruleset or 'spellout-year'
        else:
            search = ruleset or 'spellout-numbering'

        ruleset = self.get_ruleset(search)

        if ruleset is None:
            raise RulesetNotFound(search)

        return ruleset.apply(number, self)


    def get_ruleset(self, name):
        for r in self.rulesets:
            if r.name == name:
                return r


    @classmethod
    def negotiate(cls, locale):
        """
        Negotiate proper RBNF rules based on global data item `rbnf_locales`
        Caching is not necessary the Locale object does that pretty well
        """
        loc = Locale.negotiate([str(Locale.parse(locale))], get_global('rbnf_locales'))
        return cls(loc)


class Ruleset(object):
    """
    Each rule set consists of a name, a colon, and a list of rules.
    (in the ICU syntax, CLDR differs because of XML)

    If the rule's rule descriptor is left out, the base value is one plus the
    preceding rule's base value (or zero if this is the first rule in the list)
    in a normal rule set.  In a fraction rule set, the base value is the same as
    the preceding rule's base value.

    A rule set may be either a regular rule set or a fraction rule set, depending
    on whether it is used to format a number's integral part (or the whole number)
    or a number's fractional part. Using a rule set to format a rule's fractional
    part makes it a fraction rule set.

    Which rule is used to format a number is defined according to one of the
    following algorithms:

    REGULAR (NON-FRACTION) PROCESSING
    ---------------------------------
    If the rule set is a regular rule set, do the following:
    
    MASTER_RULE
    If the rule set includes a master rule (and the number was passed in as a
    double), use the master rule.  (If the number being formatted was passed
    in as a long, the master rule is ignored.)
    
    NEGATIVE_NUMBER_RULE
    If the number is negative, use the negative-number rule.
    
    IMPROPER_FRACTION_RULE
    If the number has a fractional part and is greater than 1, use
    the improper fraction rule.
    
    PROPER_FRACTION_RULE
    If the number has a fractional part and is between 0 and 1, use
    the proper fraction rule.

    Binary-search the rule list for the rule with the highest base value
    less than or equal to the number. If that rule has two substitutions,
    its base value is not an even multiple of its divisor, and the number
    is an even multiple of the rule's divisor, use the rule that precedes
    it in the rule list. Otherwise, use the rule itself.
    
    FRACTION PROCESSING
    -------------------
    If the rule set is a fraction rule set, do the following:

    Ignore negative-number and fraction rules.
    
    For each rule in the list, multiply the number being formatted (which
    will always be between 0 and 1) by the rule's base value. Keep track
    of the distance between the result and the nearest integer.
    
    Use the rule that produced the result closest to zero in the above
    calculation. In the event of a tie or a direct hit, use the first
    matching rule encountered. (The idea here is to try each rule's base
    value as a possible denominator of a fraction. Whichever denominator
    produces the fraction closest in value to the number being formatted
    wins.)

    If the rule following the matching rule has the same base value,
    use it if the numerator of the fraction is anything other than 1; if
    the numerator is 1, use the original matching rule. (This is to allow
    singular and plural forms of the rule text without a lot of extra hassle.)

    ----

    A rule's body consists of a string of characters terminated by a semicolon.
    The rule may include zero, one, or two substitution tokens, and a range of
    text in brackets. The brackets denote optional text (and may also include
    one or both substitutions). The exact meanings of the substitution tokens,
    and under what conditions optional text is omitted, depend on the syntax
    of the substitution token and the context. The rest of the text in a rule
    body is literal text that is output when the rule matches the number
    being formatted.

    A substitution token begins and ends with a token character. The token
    character and the context together specify a mathematical operation to
    be performed on the number being formatted. An optional substitution
    descriptor specifies how the value resulting from that operation is
    used to fill in the substitution. The position of the substitution
    token in the rule body specifies the location of the resultant text
    in the original rule text.

    The meanings of the substitution token characters are as follows:
    
    →→  REMAINDER_TOKEN
        :in normal rule:
            Divide the number by the rule's divisor and format the remainder
        :in negative-number rule:
            Find the absolute value of the number and format the result
        :in fraction or master rule:
            Isolate the number's fractional part and format it.
        :in rule in fraction rule set:
            Not allowed.
    
    →→→  PREVIOUS_TOKEN
        :in normal rule:
            Divide the number by the rule's divisor and format the
            remainder, but bypass the normal rule-selection process
            and just use the rule that precedes this one in this
            rule list.
        :in all other rules:
            Not allowed.
    
    ←←  INTEGRAL_TOKEN
        :in normal rule:
            Divide the number by the rule's divisor and format the quotient
        :in negative-number rule:
            Not allowed.
        :in fraction or master rule:
            Isolate the number's integral part and format it.
        :in rule in fraction rule set:
            Multiply the number by the rule's base value and format the result.
    
    ==  SUBSTITUTION_TOKEN
        :in all rule sets:
            Format the number unchanged
    
    []  OPT_START, OPT_END
        :in normal rule:
            Omit the optional text if the number is an even
            multiple of the rule's divisor
        :in negative-number rule:
            Not allowed.
        :in improper-fraction rule:
            Omit the optional text if the number is between 0 and 1
            (same as specifying both an x.x rule and a 0.x rule)
        :in master rule:
            Omit the optional text if the number is an integer
            (same as specifying both an x.x rule and an x.0 rule)
            !!! contradicts the above as it says the master rule is ignored
        :in proper-fraction rule:
            Not allowed.
        :in rule in fraction rule set:
            Omit the optional text if multiplying the number by the
            rule's base value yields 1.
    
    $(cardinal,plural syntax)$  PLURAL_TOKEN
        :in all rule sets:
            This provides the ability to choose a word based on the
            number divided by the radix to the power of the exponent
            of the base value for the specified locale, which is
            normally equivalent to the ←← value. This uses the cardinal
            plural rules from PluralFormat. All strings used in the
            plural format are treated as the same base value for parsing.
    
    $(ordinal,plural syntax)$  PLURAL_TOKEN
        :in all rule sets:
            This provides the ability to choose a word based on the
            number divided by the radix to the power of the exponent
            of the base value for the specified locale, which is
            normally equivalent to the ←← value. This uses the ordinal
            plural rules from PluralFormat. All strings used in the
            plural format are treated as the same base value for parsing.
    
    INFINITY_RULE = 'Inf'
    
    NOT_A_NUMBER_RULE = 'NaN'
    
    SPECIAL_FRACTION_RULE = 'x,x'  # there are other options but not existent in CLDR
    """

    def __init__(self, name, private=False):
        self.name = name
        self.private = private
        self.rules = []

    def apply(self, number, parent, fractional=False):
        number = decimal.Decimal(str(number))
        # str is needed to avoid unnecessary precision
        # decimal is necessary for exact representation in fraction rules

        context = {
            'search_at': parent,
            'ruleset': self,
            'fractional': fractional,
            'omit_optional': False,  # no default value is defined in the spec
            SUBSTITUTION_TOKEN: number,
            'remainder_as_fractional': False  # format remainder as fractional rule?
        }
        integral, remainder = divmod(number, 1)

        # fractional rule (ruleset in fractional processing)
        # the value should always be between 0 and 1
        # not yet tested it needs clarification
        if fractional:
            index = self.get_rule_fractional(remainder)
            if index is None:
                raise RuleNotFound("rule for fractional processing of %s" % remainder)
            rule = self.rules[index]
            context[INTEGRAL_TOKEN] = rule.value * remainder  # here remainder == number
            context['omit_optional'] = rule.value * number == 1
            return rule.apply(number, context)

        # negative number rule
        if number < 0:
            rule = self.get_rule_special(NEGATIVE_NUMBER_RULE)
            if rule is None:
                raise RuleNotFound("negative number rule (%s)" % NEGATIVE_NUMBER_RULE)
            context[REMAINDER_TOKEN] = abs(number)
            return rule.apply(number, context)

        # master and fraction rules
        if remainder != 0:
            context[REMAINDER_TOKEN] = number - integral
            context[INTEGRAL_TOKEN] = integral
            context['remainder_as_fractional'] = True

            # search for master rule
            rule = self.get_rule_special(MASTER_RULE, strict=True)

            # no master rule found
            if rule is None:
                if integral == 0:
                    rule = self.get_rule_special(PROPER_FRACTION_RULE)
                    if rule is None:
                        raise RuleNotFound("proper fraction rule (%s)" % PROPER_FRACTION_RULE)

                else:
                    rule = self.get_rule_special(IMPROPER_FRACTION_RULE)
                    if rule is None:
                        raise RuleNotFound("improper fraction rule (%s)" % IMPROPER_FRACTION_RULE)
                    context['omit_optional'] = 0 < number < 1  # between 0 and 1

            return rule.apply(number, context)

        # normal rule
        index = self.get_rule_integral(integral)
        if index is None:
            raise RuleNotFound("normal rule for %s" % integral)
        rule = self.rules[index]
        i, r = divmod(integral, rule.divisor)
        context[REMAINDER_TOKEN] = r
        context[INTEGRAL_TOKEN] = i
        context[PREVIOUS_TOKEN] = index - 1  # get rule using ruleset
        context['omit_optional'] = r != 0  # only if not even multiple (TODO no need to store separately)
        return rule.apply(number, context)

    def get_rule_special(self, val, strict=False):
        if val in Rule.specials:
            for r in self.rules:
                if r.value == val:
                    return r

        # return last rule if no match occurred and strict is false
        if not strict:
            return self.rules[-1]

    def get_rule_integral(self, val):
        """
        Binary-search the rule list for the rule with the highest base value
        less than or equal to the number.

        If that rule has two substitutions,
        its base value is not an even multiple of its divisor, and the number
        is an even multiple of the rule's divisor, use the rule that precedes
        it in the rule list. Otherwise, use the rule itself.
        """
        # automatically return last rule if no range matched
        ret = len(self.rules) - 1

        for i in range(len(self.rules) - 1):
            if self.rules[i].value in Rule.specials:
                continue

            if self.rules[i].value <= val < self.rules[i + 1].value:
                ret = i
                break

        # need to have at least one normal rule? (otherwise ret could be None)
        rule = self.rules[ret]
        if rule.substitutions == 2 and \
                rule.value % rule.divisor == 0 and \
                val % rule.divisor == 0:
            ret -= 1

        return ret

    def get_rule_fractional(self, val):
        """If the rule set is a fraction rule set, do the following:

        Ignore negative-number and fraction rules.

        For each rule in the list, multiply the number being formatted (which
        will always be between 0 and 1) by the rule's base value. Keep track
        of the distance between the result and the nearest integer.

        Use the rule that produced the result closest to zero in the above
        calculation. In the event of a tie or a direct hit, use the first
        matching rule encountered. (The idea here is to try each rule's base
        value as a possible denominator of a fraction. Whichever denominator
        produces the fraction closest in value to the number being formatted
        wins.)

        If the rule following the matching rule has the same base value,
        use it if the numerator of the fraction is anything other than 1; if
        the numerator is 1, use the original matching rule. (This is to allow
        singular and plural forms of the rule text without a lot of extra hassle.)

        ??? what is considered the numerator of what fraction here
        ??? is it rather not the closeset integer
        """
        dists = []
        for i, rule in enumerate(self.rules):
            if rule.value in Rule.specials or rule.value == 0:  # ignore specials and 0 rules
                continue
            d = abs(round(val * rule.value) - val * rule.value)
            dists.append((i, d))

        # get the index of the closest 0 match
        bst = min(dists, key=lambda x: x[1])[0]

        # there is a following rule
        if len(self.rules) > bst + 1 and \
                self.rules[bst].value == self.rules[bst + 1].value and \
                val * self.rules[bst].value > 1:
            bst += 1

        return bst

    def __repr__(self):
        return 'Ruleset %s %s\n%s\n' % (self.name, self.private, '\n'.join(['\t' + str(r) for r in self.rules]))


class Rule(object):
    """
    base value, a divisor, rule text, and zero, one, or two substitutions.
    """
    specials = {
        NEGATIVE_NUMBER_RULE, IMPROPER_FRACTION_RULE,
        PROPER_FRACTION_RULE, MASTER_RULE, INFINITY_RULE,
        NOT_A_NUMBER_RULE, SPECIAL_FRACTION_RULE,
    }

    def __init__(self, value, text, radix=None):
        """
        divisor : iterator of literal, back_sub, fwd_sub, lit_exact elements parsed from rule 
        """
        if value in self.specials:
            self.value = value
        else:
            self.value = int(value)

        self.text = text
        self.radix = int(radix or 10)

        self._parse(text)

    def apply(self, number, context):
        """
        """
        from .numbers import format_decimal
        res = []
        for t in self.tokens:
            if t.optional and not context['omit_optional']:
                continue

            if t.type == TEXT_TOKEN:
                res.append(t.reference)

            elif t.type in REFERENCE_TOKENS:
                ref_type, ref = t.reference
                ruleset = None
                if ref_type == INTERNAL_REF:
                    ruleset = context['ruleset']
                elif ref_type in (PUBLIC_REF, PRIVATE_REF):  # currently no distinction
                    ruleset = context['search_at'].get_ruleset(ref)
                elif ref_type == DECIMAL_REF:
                    loc = context['search_at']._locale
                    res.append(format_decimal(number, format=ref, locale=loc))

                if ruleset:
                    if t.type == REMAINDER_TOKEN and context['remainder_as_fractional']:
                        fractional = True
                    else:
                        fractional = context['fractional']
                    res.append(ruleset.apply(
                        context[t.type],  # number
                        context['search_at'],  # parent
                        fractional,
                    ))

            elif t.type == PREVIOUS_TOKEN:
                rule = context['ruleset'].rules[context[PREVIOUS_TOKEN]]
                res.append(rule.apply(
                    context[REMAINDER_TOKEN],  # number
                    context,  # ???
                ))

            else:
                raise ValueError('unknown token %s', t)

        return ''.join(res)

    @property
    def divisor(self):
        """it is highest exponent of radix less then or equal to the rules's base"""
        if isinstance(self.value, int):
            if self.value == 0:
                return 1
            exp = decimal.Decimal(self.value).ln() / decimal.Decimal(self.radix).ln()
            return int(self.radix ** math.floor(exp))

    @property
    def substitutions(self):
        return len([t for t in self.tokens if t.type in REFERENCE_TOKENS])

    def _parse(self, text):
        try:
            self.tokens = [t for t in tokenize(text)]
        except ValueError:
            raise TokenizationError(text)

    def __repr__(self):
        return 'Rule %s (%s) - %s\n%s\n' % (
            self.value, self.text,
            self.radix,
            '\n'.join(['\t\t' + str(t) for t in self.tokens]))
