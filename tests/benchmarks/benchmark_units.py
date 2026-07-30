from __future__ import annotations

from babel.units import format_compound_unit, format_unit, get_unit_name


def test_format_unit_long(benchmark, fi_locale):
    assert (
        benchmark(lambda: format_unit(15.5, "length-mile", locale=fi_locale)) == "15,5 mailia"
    )


def test_format_unit_short(benchmark, fi_locale):
    assert (
        benchmark(lambda: format_unit(15.5, "length-mile", "short", locale=fi_locale))
        == "15,5 mi"
    )


def test_format_unit_length_fallback(benchmark):
    # et's "long" duration-month only has a "per" pattern, so this falls back to "short".
    assert benchmark(lambda: format_unit(1, "duration-month", "long", locale="et")) == "1 kuu"


def test_format_compound_unit_predefined(benchmark, fi_locale):
    # Resolves to the predefined speed-kilometer-per-hour pattern.
    expected = "150 kilometriä tunnissa"
    assert (
        benchmark(
            lambda: format_compound_unit(
                150,
                "kilometer",
                denominator_unit="hour",
                locale=fi_locale,
            ),
        )
        == expected
    )


def test_format_compound_unit_constructed(benchmark, fi_locale):
    # No predefined compound unit; both sides get formatted and joined with the "per" pattern.
    expected = "32,5 am. tonnia/15 tuntia"
    assert (
        benchmark(
            lambda: format_compound_unit(
                32.5,
                "ton",
                15,
                denominator_unit="hour",
                locale=fi_locale,
            ),
        )
        == expected
    )


def test_get_unit_name(benchmark, fi_locale):
    # An unqualified unit id, so the pattern table is scanned to qualify it.
    assert benchmark(lambda: get_unit_name("radian", locale=fi_locale)) == "radiaanit"
