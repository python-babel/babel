# -*- coding: utf-8 -*-
"""
Utility functions for the babel.numbers._spelling module
and also for the locale specific implementations.
"""
from __future__ import division, print_function, unicode_literals

def prod(*strings):
    """Generate chartesian products of strings after splitting them"""
    import itertools
    return [''.join(r) for r in itertools.product(*[s.split(' ') for s in strings])]

