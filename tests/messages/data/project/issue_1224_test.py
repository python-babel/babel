from myproject.i18n import lazy_gettext as _l, lazy_ngettext as _n


class Choices:
    # SPECIAL: This comment should be extracted
    CHOICE_X = 1, _l("Choice X")
    # SPECIAL: Another special comment
    CHOICE_Y = 2, _l("Choice Y")
    # No comment...
    OPTION_C = 3, _l("Option C")
    # Test for _n too! (but no comment... shush...)
    OPTION_A = 4, (_n("Option A", "Options of the A kind", 1))
