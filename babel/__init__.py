# -*- coding: utf-8 -*-
"""
    babel
    ~~~~~

    Integrated collection of utilities that assist in internationalizing and
    localizing applications.

    This package is basically composed of two major parts:

     * tools to build and work with ``gettext`` message catalogs
     * a Python interface to the CLDR (Common Locale Data Repository), providing
       access to various locale display names, localized number and date
       formatting, etc.

    :copyright: (c) 2013 by the Babel Team.
    :license: BSD, see LICENSE for more details.
"""

import os
import sys

from babel.core import UnknownLocaleError, Locale, default_locale, \
    negotiate_locale, parse_locale, get_locale_identifier


__version__ = '2.4.0'


def get_base_dir():
    if getattr(sys, 'frozen', False):
        # we are running in a |PyInstaller| bundle
        basedir = sys._MEIPASS
    else:
        # we are running in a normal Python environment
        basedir = os.path.dirname(__file__)
    return basedir
