from __future__ import annotations

from babel.languages import get_official_languages, get_territory_language_info


def test_get_official_languages(benchmark):
    benchmark(lambda: get_official_languages("CH"))


def test_get_official_languages_regional(benchmark):
    benchmark(lambda: get_official_languages("CH", regional=True, de_facto=True))


def test_get_territory_language_info(benchmark):
    benchmark(lambda: get_territory_language_info("CH"))
