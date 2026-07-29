from __future__ import annotations

from babel.lists import format_list

TWO = ["omena", "peruna"]
FIVE = ["omena", "peruna", "aplari", "kurpitsa", "porkkana"]


def test_format_list_two(benchmark, fi_locale):
    # Two items hit the special-cased "2" pattern.
    assert benchmark(lambda: format_list(TWO, locale=fi_locale)) == "omena ja peruna"


def test_format_list_five(benchmark, fi_locale):
    assert (
        benchmark(lambda: format_list(FIVE, locale=fi_locale))
        == "omena, peruna, aplari, kurpitsa ja porkkana"
    )


def test_format_list_or(benchmark, fi_locale):
    assert (
        benchmark(lambda: format_list(FIVE, "or", locale=fi_locale))
        == "omena, peruna, aplari, kurpitsa tai porkkana"
    )


def test_format_list_style_fallback(benchmark, fi_locale):
    # fi has no "standard-short" list patterns, so this falls back to "standard".
    assert (
        benchmark(lambda: format_list(FIVE, "standard-short", locale=fi_locale))
        == "omena, peruna, aplari, kurpitsa ja porkkana"
    )
