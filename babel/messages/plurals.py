"""
babel.messages.plurals
~~~~~~~~~~~~~~~~~~~~~~

Plural form definitions.

:copyright: (c) 2013-2026 by the Babel Team.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from babel.core import Locale, default_locale

# XXX: remove this file, duplication with babel.plural


LC_CTYPE: str | None = default_locale('LC_CTYPE')

# Generated with scripts/dump_plurals_dict.py
PLURALS: dict[str, tuple[int, str]] = {
    # Afrikaans
    'af': (2, '(n != 1)'),
    # Akan
    'ak': (2, '(n > 1)'),
    # Amharic
    'am': (2, '(n > 1)'),
    # Aragonese
    'an': (2, '(n != 1)'),
    # Arabic
    'ar': (6, '(n == 0 ? 0 : n == 1 ? 1 : n == 2 ? 2 : n % 100 >= 3 && n % 100 <= 10 ? 3 : n % 100 >= 11 && n % 100 <= 99 ? 4 : 5)'),
    # Assamese
    'as': (2, '(n > 1)'),
    # Asu
    'asa': (2, '(n != 1)'),
    # Asturian
    'ast': (2, '(n != 1)'),
    # Azerbaijani
    'az': (2, '(n != 1)'),
    # Baluchi
    'bal': (2, '(n != 1)'),
    # Belarusian
    'be': (3, 'n % 10 == 1 && n % 100 != 11 ? 0 : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? 1 : 2'),
    # Bemba
    'bem': (2, '(n != 1)'),
    # Bena
    'bez': (2, '(n != 1)'),
    # Bulgarian
    'bg': (2, '(n != 1)'),
    # Bhojpuri
    'bho': (2, '(n > 1)'),
    # Anii
    'blo': (3, '(n == 0 ? 0 : n == 1 ? 1 : 2)'),
    # Bambara
    'bm': (1, '0'),
    # Bangla
    'bn': (2, '(n > 1)'),
    # Tibetan
    'bo': (1, '0'),
    # Breton
    'br': (5, 'n % 10 == 1 && n % 100 != 11 && n % 100 != 71 && n % 100 != 91 ? 0 : n % 10 == 2 && n % 100 != 12 && n % 100 != 72 && n % 100 != 92 ? 1 : ((n % 10 == 3 || n % 10 == 4) || n % 10 == 9) && (n % 100 < 10 || n % 100 > 19) && (n % 100 < 70 || n % 100 > 79) && (n % 100 < 90 || n % 100 > 99) ? 2 : n != 0 && n % 1000000 == 0 ? 3 : 4'),
    # Bodo
    'brx': (2, '(n != 1)'),
    # Bosnian
    'bs': (3, 'n % 10 == 1 && n % 100 != 11 ? 0 : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? 1 : 2'),
    # Catalan
    'ca': (3, '(n == 1 ? 0 : n != 0 && n % 1000000 == 0 ? 1 : 2)'),
    # Chechen
    'ce': (2, '(n != 1)'),
    # Cebuano
    'ceb': (2, 'n != 1 && n != 2 && n != 3 && (n % 10 == 4 || n % 10 == 6 || n % 10 == 9)'),
    # Chiga
    'cgg': (2, '(n != 1)'),
    # Cherokee
    'chr': (2, '(n != 1)'),
    # Central Kurdish
    'ckb': (2, '(n != 1)'),
    # Czech
    'cs': (3, '(n == 1 ? 0 : n >= 2 && n <= 4 ? 1 : 2)'),
    # Swampy Cree
    'csw': (2, '(n > 1)'),
    # Chuvash
    'cv': (3, '(n == 0 ? 0 : n == 1 ? 1 : 2)'),
    # Welsh
    'cy': (6, '(n == 0 ? 0 : n == 1 ? 1 : n == 2 ? 2 : n == 3 ? 3 : n == 6 ? 4 : 5)'),
    # Danish
    'da': (2, '(n != 1)'),
    # German
    'de': (2, '(n != 1)'),
    # Dogri
    'doi': (2, '(n > 1)'),
    # Lower Sorbian
    'dsb': (4, 'n % 100 == 1 ? 0 : n % 100 == 2 ? 1 : (n % 100 == 3 || n % 100 == 4) ? 2 : 3'),
    # Divehi
    'dv': (2, '(n != 1)'),
    # Dzongkha
    'dz': (1, '0'),
    # Ewe
    'ee': (2, '(n != 1)'),
    # Greek
    'el': (2, '(n != 1)'),
    # English
    'en': (2, '(n != 1)'),
    # Esperanto
    'eo': (2, '(n != 1)'),
    # Spanish
    'es': (3, '(n == 1 ? 0 : n != 0 && n % 1000000 == 0 ? 1 : 2)'),
    # Estonian
    'et': (2, '(n != 1)'),
    # Basque
    'eu': (2, '(n != 1)'),
    # Persian
    'fa': (2, '(n > 1)'),
    # Fula
    'ff': (2, '(n > 1)'),
    # Finnish
    'fi': (2, '(n != 1)'),
    # Filipino
    'fil': (2, 'n != 1 && n != 2 && n != 3 && (n % 10 == 4 || n % 10 == 6 || n % 10 == 9)'),
    # Faroese
    'fo': (2, '(n != 1)'),
    # French
    'fr': (3, '(n == 0 || n == 1) ? 0 : n != 0 && n % 1000000 == 0 ? 1 : 2'),
    # Friulian
    'fur': (2, '(n != 1)'),
    # Western Frisian
    'fy': (2, '(n != 1)'),
    # Irish
    'ga': (5, '(n == 1 ? 0 : n == 2 ? 1 : n >= 3 && n <= 6 ? 2 : n >= 7 && n <= 10 ? 3 : 4)'),
    # Scottish Gaelic
    'gd': (4, '(n == 1 || n == 11) ? 0 : (n == 2 || n == 12) ? 1 : (n >= 3 && n <= 10 || n >= 13 && n <= 19) ? 2 : 3'),
    # Galician
    'gl': (2, '(n != 1)'),
    # Swiss German
    'gsw': (2, '(n != 1)'),
    # Gujarati
    'gu': (2, '(n > 1)'),
    # Manx
    'gv': (4, 'n % 10 == 1 ? 0 : n % 10 == 2 ? 1 : (n % 100 == 0 || n % 100 == 20 || n % 100 == 40 || n % 100 == 60 || n % 100 == 80) ? 2 : 3'),
    # Hausa
    'ha': (2, '(n != 1)'),
    # Hawaiian
    'haw': (2, '(n != 1)'),
    # Hebrew
    'he': (3, '(n == 1 ? 0 : n == 2 ? 1 : 2)'),
    # Hindi
    'hi': (2, '(n > 1)'),
    # Hmong Njua
    'hnj': (1, '0'),
    # Croatian
    'hr': (3, 'n % 10 == 1 && n % 100 != 11 ? 0 : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? 1 : 2'),
    # Upper Sorbian
    'hsb': (4, 'n % 100 == 1 ? 0 : n % 100 == 2 ? 1 : (n % 100 == 3 || n % 100 == 4) ? 2 : 3'),
    # Hungarian
    'hu': (2, '(n != 1)'),
    # Armenian
    'hy': (2, '(n > 1)'),
    # Interlingua
    'ia': (2, '(n != 1)'),
    # Indonesian
    'id': (1, '0'),
    # Interlingue
    'ie': (2, '(n != 1)'),
    # Igbo
    'ig': (1, '0'),
    # Sichuan Yi
    'ii': (1, '0'),
    # Ido
    'io': (2, '(n != 1)'),
    # Icelandic
    'is': (2, '(n % 10 != 1 || n % 100 == 11)'),
    # Italian
    'it': (3, '(n == 1 ? 0 : n != 0 && n % 1000000 == 0 ? 1 : 2)'),
    # Inuktitut
    'iu': (3, '(n == 1 ? 0 : n == 2 ? 1 : 2)'),
    # Japanese
    'ja': (1, '0'),
    # Lojban
    'jbo': (1, '0'),
    # Ngomba
    'jgo': (2, '(n != 1)'),
    # Machame
    'jmc': (2, '(n != 1)'),
    # Javanese
    'jv': (1, '0'),
    # Georgian
    'ka': (2, '(n != 1)'),
    # Kabyle
    'kab': (2, '(n > 1)'),
    # Jju
    'kaj': (2, '(n != 1)'),
    # Tyap
    'kcg': (2, '(n != 1)'),
    # Makonde
    'kde': (1, '0'),
    # Kabuverdianu
    'kea': (1, '0'),
    # Kazakh
    'kk': (2, '(n != 1)'),
    # Kako
    'kkj': (2, '(n != 1)'),
    # Kalaallisut
    'kl': (2, '(n != 1)'),
    # Khmer
    'km': (1, '0'),
    # Kannada
    'kn': (2, '(n > 1)'),
    # Korean
    'ko': (1, '0'),
    # Konkani
    'kok': (2, '(n > 1)'),
    # Kashmiri
    'ks': (2, '(n != 1)'),
    # Shambala
    'ksb': (2, '(n != 1)'),
    # Colognian
    'ksh': (3, '(n == 0 ? 0 : n == 1 ? 1 : 2)'),
    # Kurdish
    'ku': (2, '(n != 1)'),
    # Cornish
    'kw': (6, 'n == 0 ? 0 : n == 1 ? 1 : (n % 100 == 2 || n % 100 == 22 || n % 100 == 42 || n % 100 == 62 || n % 100 == 82) || n % 1000 == 0 && (n % 100000 >= 1000 && n % 100000 <= 20000 || n % 100000 == 40000 || n % 100000 == 60000 || n % 100000 == 80000) || n != 0 && n % 1000000 == 100000 ? 2 : (n % 100 == 3 || n % 100 == 23 || n % 100 == 43 || n % 100 == 63 || n % 100 == 83) ? 3 : n != 1 && (n % 100 == 1 || n % 100 == 21 || n % 100 == 41 || n % 100 == 61 || n % 100 == 81) ? 4 : 5'),
    # Kyrgyz
    'ky': (2, '(n != 1)'),
    # Langi
    'lag': (3, '(n == 0 ? 0 : n == 1 ? 1 : 2)'),
    # Luxembourgish
    'lb': (2, '(n != 1)'),
    # Ganda
    'lg': (2, '(n != 1)'),
    # Ligurian
    'lij': (2, '(n != 1)'),
    # Lakota
    'lkt': (1, '0'),
    # Dolomitic Ladin
    'lld': (3, '(n == 1 ? 0 : n != 0 && n % 1000000 == 0 ? 1 : 2)'),
    # Lingala
    'ln': (2, '(n > 1)'),
    # Lao
    'lo': (1, '0'),
    # Lithuanian
    'lt': (3, 'n % 10 == 1 && (n % 100 < 11 || n % 100 > 19) ? 0 : n % 10 >= 2 && n % 10 <= 9 && (n % 100 < 11 || n % 100 > 19) ? 1 : 2'),
    # Latvian
    'lv': (3, '(n % 10 == 0 || n % 100 >= 11 && n % 100 <= 19 ? 0 : n % 10 == 1 && n % 100 != 11 ? 1 : 2)'),
    # Masai
    'mas': (2, '(n != 1)'),
    # Malagasy
    'mg': (2, '(n > 1)'),
    # Metaʼ
    'mgo': (2, '(n != 1)'),
    # Macedonian
    'mk': (2, '(n % 10 != 1 || n % 100 == 11)'),
    # Malayalam
    'ml': (2, '(n != 1)'),
    # Mongolian
    'mn': (2, '(n != 1)'),
    # Marathi
    'mr': (2, '(n != 1)'),
    # Malay
    'ms': (1, '0'),
    # Maltese
    'mt': (5, '(n == 1 ? 0 : n == 2 ? 1 : n == 0 || n % 100 >= 3 && n % 100 <= 10 ? 2 : n % 100 >= 11 && n % 100 <= 19 ? 3 : 4)'),
    # Burmese
    'my': (1, '0'),
    # Nama
    'naq': (3, '(n == 1 ? 0 : n == 2 ? 1 : 2)'),
    # Norwegian Bokmål
    'nb': (2, '(n != 1)'),
    # North Ndebele
    'nd': (2, '(n != 1)'),
    # Nepali
    'ne': (2, '(n != 1)'),
    # Dutch
    'nl': (2, '(n != 1)'),
    # Norwegian Nynorsk
    'nn': (2, '(n != 1)'),
    # Ngiemboon
    'nnh': (2, '(n != 1)'),
    # Norwegian
    'no': (2, '(n != 1)'),
    # N’Ko
    'nqo': (1, '0'),
    # South Ndebele
    'nr': (2, '(n != 1)'),
    # Northern Sotho
    'nso': (2, '(n > 1)'),
    # Nyanja
    'ny': (2, '(n != 1)'),
    # Nyankole
    'nyn': (2, '(n != 1)'),
    # Oromo
    'om': (2, '(n != 1)'),
    # Odia
    'or': (2, '(n != 1)'),
    # Ossetic
    'os': (2, '(n != 1)'),
    # Osage
    'osa': (1, '0'),
    # Punjabi
    'pa': (2, '(n > 1)'),
    # Papiamento
    'pap': (2, '(n != 1)'),
    # Nigerian Pidgin
    'pcm': (2, '(n > 1)'),
    # Polish
    'pl': (3, 'n == 1 ? 0 : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? 1 : 2'),
    # Prussian
    'prg': (3, '(n % 10 == 0 || n % 100 >= 11 && n % 100 <= 19 ? 0 : n % 10 == 1 && n % 100 != 11 ? 1 : 2)'),
    # Pashto
    'ps': (2, '(n != 1)'),
    # Portuguese
    'pt': (3, '(n == 0 || n == 1) ? 0 : n != 0 && n % 1000000 == 0 ? 1 : 2'),
    # European Portuguese
    'pt_PT': (3, '(n == 1 ? 0 : n != 0 && n % 1000000 == 0 ? 1 : 2)'),
    # Romansh
    'rm': (2, '(n != 1)'),
    # Romanian
    'ro': (3, '(n == 1 ? 0 : n == 0 || n != 1 && n % 100 >= 1 && n % 100 <= 19 ? 1 : 2)'),
    # Rombo
    'rof': (2, '(n != 1)'),
    # Russian
    'ru': (3, 'n % 10 == 1 && n % 100 != 11 ? 0 : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? 1 : 2'),
    # Rwa
    'rwk': (2, '(n != 1)'),
    # Yakut
    'sah': (1, '0'),
    # Samburu
    'saq': (2, '(n != 1)'),
    # Santali
    'sat': (3, '(n == 1 ? 0 : n == 2 ? 1 : 2)'),
    # Sardinian
    'sc': (2, '(n != 1)'),
    # Sicilian
    'scn': (3, '(n == 1 ? 0 : n != 0 && n % 1000000 == 0 ? 1 : 2)'),
    # Sindhi
    'sd': (2, '(n != 1)'),
    # Southern Kurdish
    'sdh': (2, '(n != 1)'),
    # Northern Sami
    'se': (3, '(n == 1 ? 0 : n == 2 ? 1 : 2)'),
    # Sena
    'seh': (2, '(n != 1)'),
    # Koyraboro Senni
    'ses': (1, '0'),
    # Sango
    'sg': (1, '0'),
    # Samogitian
    'sgs': (4, 'n % 10 == 1 && n % 100 != 11 ? 0 : n == 2 ? 1 : n != 2 && n % 10 >= 2 && n % 10 <= 9 && (n % 100 < 11 || n % 100 > 19) ? 2 : 3'),
    # Tachelhit
    'shi': (3, '(n == 0 || n == 1 ? 0 : n >= 2 && n <= 10 ? 1 : 2)'),
    # Sinhala
    'si': (2, '(n > 1)'),
    # Slovak
    'sk': (3, '(n == 1 ? 0 : n >= 2 && n <= 4 ? 1 : 2)'),
    # Slovenian
    'sl': (4, 'n % 100 == 1 ? 0 : n % 100 == 2 ? 1 : (n % 100 == 3 || n % 100 == 4) ? 2 : 3'),
    # Southern Sami
    'sma': (3, '(n == 1 ? 0 : n == 2 ? 1 : 2)'),
    # Lule Sami
    'smj': (3, '(n == 1 ? 0 : n == 2 ? 1 : 2)'),
    # Inari Sami
    'smn': (3, '(n == 1 ? 0 : n == 2 ? 1 : 2)'),
    # Skolt Sami
    'sms': (3, '(n == 1 ? 0 : n == 2 ? 1 : 2)'),
    # Shona
    'sn': (2, '(n != 1)'),
    # Somali
    'so': (2, '(n != 1)'),
    # Albanian
    'sq': (2, '(n != 1)'),
    # Serbian
    'sr': (3, 'n % 10 == 1 && n % 100 != 11 ? 0 : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? 1 : 2'),
    # Swati
    'ss': (2, '(n != 1)'),
    # Saho
    'ssy': (2, '(n != 1)'),
    # Southern Sotho
    'st': (2, '(n != 1)'),
    # Sundanese
    'su': (1, '0'),
    # Swedish
    'sv': (2, '(n != 1)'),
    # Swahili
    'sw': (2, '(n != 1)'),
    # Syriac
    'syr': (2, '(n != 1)'),
    # Tamil
    'ta': (2, '(n != 1)'),
    # Telugu
    'te': (2, '(n != 1)'),
    # Teso
    'teo': (2, '(n != 1)'),
    # Thai
    'th': (1, '0'),
    # Tigrinya
    'ti': (2, '(n > 1)'),
    # Tigre
    'tig': (2, '(n != 1)'),
    # Turkmen
    'tk': (2, '(n != 1)'),
    # Tswana
    'tn': (2, '(n != 1)'),
    # Tongan
    'to': (1, '0'),
    # Tok Pisin
    'tpi': (1, '0'),
    # Turkish
    'tr': (2, '(n != 1)'),
    # Tsonga
    'ts': (2, '(n != 1)'),
    # Central Atlas Tamazight
    'tzm': (2, 'n >= 2 && (n < 11 || n > 99)'),
    # Uyghur
    'ug': (2, '(n != 1)'),
    # Ukrainian
    'uk': (3, 'n % 10 == 1 && n % 100 != 11 ? 0 : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? 1 : 2'),
    # Urdu
    'ur': (2, '(n != 1)'),
    # Uzbek
    'uz': (2, '(n != 1)'),
    # Venda
    've': (2, '(n != 1)'),
    # Venetian
    'vec': (3, '(n == 1 ? 0 : n != 0 && n % 1000000 == 0 ? 1 : 2)'),
    # Vietnamese
    'vi': (1, '0'),
    # Volapük
    'vo': (2, '(n != 1)'),
    # Vunjo
    'vun': (2, '(n != 1)'),
    # Walloon
    'wa': (2, '(n > 1)'),
    # Walser
    'wae': (2, '(n != 1)'),
    # Wolof
    'wo': (1, '0'),
    # Xhosa
    'xh': (2, '(n != 1)'),
    # Soga
    'xog': (2, '(n != 1)'),
    # Yiddish
    'yi': (2, '(n != 1)'),
    # Yoruba
    'yo': (1, '0'),
    # Cantonese
    'yue': (1, '0'),
    # Chinese
    'zh': (1, '0'),
    # Zulu
    'zu': (2, '(n > 1)'),
}  # fmt: skip

DEFAULT_PLURAL: tuple[int, str] = (2, '(n != 1)')


class _PluralTuple(tuple):
    """A tuple with plural information."""

    __slots__ = ()

    @property
    def num_plurals(self) -> int:
        """The number of plurals used by the locale."""
        return self[0]

    @property
    def plural_expr(self) -> str:
        """The plural expression used by the locale."""
        return self[1]

    @property
    def plural_forms(self) -> str:
        """The plural expression used by the catalog or locale."""
        return f'nplurals={self[0]}; plural={self[1]};'

    def __str__(self) -> str:
        return self.plural_forms


def get_plural(locale: Locale | str | None = None) -> _PluralTuple:
    """A tuple with the information catalogs need to perform proper
    pluralization.  The first item of the tuple is the number of plural
    forms, the second the plural expression.

    :param locale: the `Locale` object or locale identifier. Defaults to the system character type locale.

    >>> get_plural(locale='en')
    (2, '(n != 1)')
    >>> get_plural(locale='ga')
    (5, '(n == 1 ? 0 : n == 2 ? 1 : n >= 3 && n <= 6 ? 2 : n >= 7 && n <= 10 ? 3 : 4)')

    The object returned is a special tuple with additional members:

    >>> tup = get_plural("ja")
    >>> tup.num_plurals
    1
    >>> tup.plural_expr
    '0'
    >>> tup.plural_forms
    'nplurals=1; plural=0;'

    Converting the tuple into a string prints the plural forms for a
    gettext catalog:

    >>> str(tup)
    'nplurals=1; plural=0;'
    """
    locale = Locale.parse(locale or LC_CTYPE)
    try:
        tup = PLURALS[str(locale)]
    except KeyError:
        try:
            tup = PLURALS[locale.language]
        except KeyError:
            tup = DEFAULT_PLURAL
    return _PluralTuple(tup)
