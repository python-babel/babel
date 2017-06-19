# -*- coding: utf-8 -*-
"""
    babel.pi_support
    ~~~~~~~~~~

    PyInstaller support function.
    direct usage of __file__ is not working in frozen environments

    :copyright: (c) 2017 by the Babel Team.
    :license: BSD, see LICENSE for more details.
"""

import sys
import os


def get_base_dir():
    if getattr(sys, 'frozen', False):
        # we are running in a |PyInstaller| bundle
        basedir = sys._MEIPASS
    else:
        # we are running in a normal Python environment
        basedir = os.path.dirname(__file__)
    return basedir
