import json
from urllib.request import urlopen

from babel.core import get_cldr_version
from babel.localedata import locale_identifiers


def write_dict(data):
    ids = set(locale_identifiers())
    ids |= {l.partition("_")[0] for l in ids}

    print("PLURALS: dict[str, tuple[int, str]] = {")
    for key, info in sorted(data.items()):
        if key not in ids:
            continue

        n = info['plurals']
        formula = info['formulas']['standard']
        if not formula.isdigit() and "(" not in formula:
            formula = f"({formula})"
        tup = (n, formula)
        # We could be tempted to compare to `DEFAULT_PLURAL`
        # here and emit a reference to it, but CPython is
        # smart enough to do constant folding on constant tuples:
        #   >>> p.PLURALS["ak"] is p.PLURALS["am"]
        #   True
        # so it actually becomes cheaper to emit these tuples,
        # and avoid loading global values when the dict is
        # being constructed.
        # It also doesn't feel right to not emit DEFAULT_PLURAL
        # valued items, because then we'd spend more time doing
        # the fallback logic in `get_plural`.
        print(f"    # {info['name']}")
        print(f"    {key!r}: {tup!r},")
    print("}  # fmt: skip")

def main() -> None:
    # The PHP-Gettext project has more concise/optimal gettext conversions of the CLDR rules
    # than what our `_GettextCompiler` (correct, but not optimal) generates, so let's use those.

    version = get_cldr_version()
    if version == "48":  # get_cldr_version only emits the major version
        version = "48.1"
    with urlopen(f"https://php-gettext.github.io/Languages/data/versions/{version}.json") as fp:
        data = json.loads(fp.read().decode('utf-8'))

    write_dict(data)


if __name__ == '__main__':
    main()
