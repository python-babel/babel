import pytest

from babel import Locale


def test_attributes():
    locale = Locale('en', 'US')
    assert locale.language == 'en'
    assert locale.territory == 'US'


def test_default(monkeypatch):
    for name in ['LANGUAGE', 'LC_ALL', 'LC_CTYPE', 'LC_MESSAGES']:
        monkeypatch.setenv(name, '')
    monkeypatch.setenv('LANG', 'fr_FR.UTF-8')
    default = Locale.default('LC_MESSAGES')
    assert (default.language, default.territory) == ('fr', 'FR')


def test_negotiate():
    de_DE = Locale.negotiate(['de_DE', 'en_US'], ['de_DE', 'de_AT'])
    assert (de_DE.language, de_DE.territory) == ('de', 'DE')
    de = Locale.negotiate(['de_DE', 'en_US'], ['en', 'de'])
    assert (de.language, de.territory) == ('de', None)
    nothing = Locale.negotiate(['de_DE', 'de'], ['en_US'])
    assert nothing is None


def test_negotiate_custom_separator():
    de_DE = Locale.negotiate(['de-DE', 'de'], ['en-us', 'de-de'], sep='-')
    assert (de_DE.language, de_DE.territory) == ('de', 'DE')


def test_parse():
    locale = Locale.parse('de-DE', sep='-')
    assert locale.display_name == 'Deutsch (Deutschland)'

    de_DE = Locale.parse(locale)
    assert (de_DE.language, de_DE.territory) == ('de', 'DE')


def test_parse_likely_subtags():
    locale = Locale.parse('zh-TW', sep='-')
    assert locale.language == 'zh'
    assert locale.territory == 'TW'
    assert locale.script == 'Hant'

    locale = Locale.parse('zh_CN')
    assert locale.language == 'zh'
    assert locale.territory == 'CN'
    assert locale.script == 'Hans'

    locale = Locale.parse('zh_SG')
    assert locale.language == 'zh'
    assert locale.territory == 'SG'
    assert locale.script == 'Hans'

    locale = Locale.parse('und_AT')
    assert locale.language == 'de'
    assert locale.territory == 'AT'

    locale = Locale.parse('und_UK')
    assert locale.language == 'en'
    assert locale.territory == 'GB'
    assert locale.script is None


def test_get_display_name():
    zh_CN = Locale('zh', 'CN', script='Hans')
    assert zh_CN.get_display_name('en') == 'Chinese (Simplified, China)'


def test_display_name_property():
    assert Locale('en').display_name == 'English'
    assert Locale('en', 'US').display_name == 'English (United States)'
    assert Locale('sv').display_name == 'svenska'


def test_english_name_property():
    assert Locale('de').english_name == 'German'
    assert Locale('de', 'DE').english_name == 'German (Germany)'


def test_languages_property():
    assert Locale('de', 'DE').languages['ja'] == 'Japanisch'


def test_scripts_property():
    assert Locale('en', 'US').scripts['Hira'] == 'Hiragana'


def test_territories_property():
    assert Locale('es', 'CO').territories['DE'] == 'Alemania'


def test_variants_property():
    assert Locale('de', 'DE').variants['1901'] == 'Alte deutsche Rechtschreibung'


def test_currencies_property():
    assert Locale('en').currencies['COP'] == 'Colombian Peso'
    assert Locale('de', 'DE').currencies['COP'] == 'Kolumbianischer Peso'


def test_currency_symbols_property():
    assert Locale('en', 'US').currency_symbols['USD'] == '$'
    assert Locale('es', 'CO').currency_symbols['USD'] == 'US$'


def test_number_symbols_property():
    assert Locale('fr', 'FR').number_symbols["latn"]['decimal'] == ','
    assert Locale('ar', 'IL').number_symbols["arab"]['percentSign'] == '٪\u061c'
    assert Locale('ar', 'IL').number_symbols["latn"]['percentSign'] == '\u200e%\u200e'


def test_other_numbering_systems_property():
    assert Locale('fr', 'FR').other_numbering_systems['native'] == 'latn'
    assert 'traditional' not in Locale('fr', 'FR').other_numbering_systems

    assert Locale('el', 'GR').other_numbering_systems['native'] == 'latn'
    assert Locale('el', 'GR').other_numbering_systems['traditional'] == 'grek'


def test_default_numbering_systems_property():
    assert Locale('en', 'GB').default_numbering_system == 'latn'
    assert Locale('ar', 'EG').default_numbering_system == 'arab'


@pytest.mark.all_locales
def test_all_locales_have_default_numbering_system(locale):
    locale = Locale.parse(locale)
    assert locale.default_numbering_system


def test_decimal_formats():
    assert Locale('en', 'US').decimal_formats[None].pattern == '#,##0.###'


def test_currency_formats_property():
    en_us_currency_format = Locale('en', 'US').currency_formats
    assert en_us_currency_format['standard'].pattern == '\xa4#,##0.00'
    assert en_us_currency_format['accounting'].pattern == '\xa4#,##0.00;(\xa4#,##0.00)'


def test_percent_formats_property():
    assert Locale('en', 'US').percent_formats[None].pattern == '#,##0%'


def test_scientific_formats_property():
    assert Locale('en', 'US').scientific_formats[None].pattern == '#E0'


def test_periods_property():
    assert Locale('en', 'US').periods['am'] == 'AM'


def test_days_property():
    assert Locale('de', 'DE').days['format']['wide'][3] == 'Donnerstag'


def test_months_property():
    assert Locale('de', 'DE').months['format']['wide'][10] == 'Oktober'


def test_quarters_property():
    assert Locale('de', 'DE').quarters['format']['wide'][1] == '1. Quartal'


def test_eras_property():
    assert Locale('en', 'US').eras['wide'][1] == 'Anno Domini'
    assert Locale('en', 'US').eras['abbreviated'][0] == 'BC'


def test_time_zones_property():
    time_zones = Locale('en', 'US').time_zones
    assert time_zones['Europe/London']['long']['daylight'] == 'British Summer Time'
    assert time_zones['America/St_Johns']['city'] == 'St. John\u2019s'


def test_meta_zones_property():
    meta_zones = Locale('en', 'US').meta_zones
    assert meta_zones['Europe_Central']['long']['daylight'] == 'Central European Summer Time'


def test_zone_formats_property():
    assert Locale('en', 'US').zone_formats['fallback'] == '%(1)s (%(0)s)'
    assert Locale('pt', 'BR').zone_formats['region'] == 'Hor\xe1rio %s'


def test_first_week_day_property():
    assert Locale('de', 'DE').first_week_day == 0
    assert Locale('en', 'US').first_week_day == 6


def test_weekend_start_property():
    assert Locale('de', 'DE').weekend_start == 5


def test_weekend_end_property():
    assert Locale('de', 'DE').weekend_end == 6


def test_min_week_days_property():
    assert Locale('de', 'DE').min_week_days == 4


def test_date_formats_property():
    assert Locale('en', 'US').date_formats['short'].pattern == 'M/d/yy'
    assert Locale('fr', 'FR').date_formats['long'].pattern == 'd MMMM y'


def test_time_formats_property():
    assert Locale('en', 'US').time_formats['short'].pattern == 'h:mm\u202fa'
    assert Locale('fr', 'FR').time_formats['long'].pattern == 'HH:mm:ss z'


def test_datetime_formats_property():
    assert Locale('en').datetime_formats['full'] == "{1}, {0}"
    assert Locale('th').datetime_formats['medium'] == '{1} {0}'


def test_datetime_skeleton_property():
    assert Locale('en').datetime_skeletons['Md'].pattern == "M/d"
    assert Locale('th').datetime_skeletons['Md'].pattern == 'd/M'


def test_plural_form_property():
    assert Locale('en').plural_form(1) == 'one'
    assert Locale('en').plural_form(0) == 'other'
    assert Locale('fr').plural_form(0) == 'one'
    assert Locale('ru').plural_form(100) == 'many'


def test_locale_provides_access_to_cldr_locale_data():
    locale = Locale('en', 'US')
    assert locale.display_name == 'English (United States)'
    assert locale.number_symbols["latn"]['decimal'] == '.'


def test_locale_repr():
    # fmt: off
    assert repr(Locale('en', 'US')) == "Locale('en', territory='US')"
    assert repr(Locale('de', 'DE')) == "Locale('de', territory='DE')"
    assert repr(Locale('zh', 'CN', script='Hans')) == "Locale('zh', territory='CN', script='Hans')"
    # fmt: on


def test_locale_comparison():
    en_US = Locale('en', 'US')
    en_US_2 = Locale('en', 'US')
    fi_FI = Locale('fi', 'FI')
    bad_en_US = Locale('en_US')
    assert en_US == en_US
    assert en_US == en_US_2
    assert en_US != fi_FI
    assert not (en_US != en_US_2)
    assert en_US is not None
    assert en_US != bad_en_US
    assert fi_FI != bad_en_US


def test_hash():
    locale_a = Locale('en', 'US')
    locale_b = Locale('en', 'US')
    locale_c = Locale('fi', 'FI')
    assert hash(locale_a) == hash(locale_b)
    assert hash(locale_a) != hash(locale_c)


def test_language_alt_official_not_used():
    # If there exists an official and customary language name, the customary
    # name should be used.
    #
    # For example, here 'Muscogee' should be used instead of 'Mvskoke':
    # <language type="mus">Muscogee</language>
    # <language type="mus" alt="official">Mvskoke</language>

    locale = Locale('mus')
    assert locale.get_display_name() == 'Mvskoke'
    assert locale.get_display_name(Locale('en')) == 'Muscogee'
