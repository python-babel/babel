import os

import tomllib

from babel.core import Locale, get_global
from babel.rbnf import RBNFError, RuleBasedNumberFormat

print(os.system("pwd"))


test_cases = None

def get_test_cases(
        template_toml_path: str = None,
        ruleset_name: str = None,
    ) -> dict:

    global test_cases

    if test_cases is None:
        if template_toml_path is None:
            with open("tests/rbnf_test_cases/_template.toml", "rb") as f:
                test_cases_temp = tomllib.load(f)
                test_cases = test_cases_temp
        else:
            with open(template_toml_path, "rb") as f:
                test_cases_temp = tomllib.load(f)
    else:
        test_cases_temp = test_cases

    return test_cases_temp[get_mapped_ruleset_name(ruleset_name)].items()


def get_mapped_ruleset_name(ruleset: str) -> str:
    print(ruleset)
    mapping = {
        "spellout-numbering-year": "year",
        "spellout-numbering": "numbering",
        "spellout-ordinal": "ordinal",
        "spellout-cardinal": "cardinal",
    }
    for k, v in mapping.items():
        if ruleset.startswith(k):
            return v
    return 'numbering'  # default fallback


def generate_test_for_locale(
        locale: Locale,
        output_toml_path: str,
        test_cases: dict = None,


) -> None:

    lines = []
    lines.append("# generated test files")
    lines.append("# CURATED BY [please add if curated]")
    lines.append(f'locale = "{locale}"')
    lines.append("version = 1")
    lines.append("generated = true")

    speller = RuleBasedNumberFormat.negotiate(locale)
    print(locale)

    for ruleset in speller.available_rulesets:

        lines.append("")
        lines.append(f"[{ruleset}]")
        print(f" {ruleset}")

        for k, _ in get_test_cases(ruleset_name=ruleset):

            try:
                v2 = speller.format(k, ruleset=ruleset)
                print(f"    {k} : '{v2}'")
                lines.append(f'{k} = "{v2}"')
            except RBNFError as e:
                print(k, locale, ruleset, e)
                input()


    with open(output_toml_path, "w") as f:
        f.write("\n".join(lines))



def generate_all_tests(
        test_cases_toml_path: str = "tests/rbnf_test_cases/_template.toml",
        output_dir: str = "tests/rbnf_test_cases/",
) -> None:

    for locale in list(get_global('rbnf_locales')):
        output_toml_path = os.path.join(output_dir, f"{locale}.toml")
        generate_test_for_locale(locale, output_toml_path)



def dump_rbnf_style_rules(locale: Locale) -> None:
    # TODO add RBNF style dump to Rule's __str__ method
    pass


if __name__ == "__main__":
    generate_all_tests()
