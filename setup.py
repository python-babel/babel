#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2011 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

import os
import sys
from setuptools import setup

sys.path.append(os.path.join('doc', 'common'))
try:
    from doctools import build_doc, test_doc
except ImportError:
    build_doc = test_doc = None


setup(
    name = 'Babel',
    version = '1.0',
    description = 'Internationalization utilities',
    long_description = \
"""A collection of tools for internationalizing Python applications.""",
    author = 'Edgewall Software',
    author_email = 'info@edgewall.org',
    license = 'BSD',
    url = 'http://babel.edgewall.org/',
    download_url = 'http://babel.edgewall.org/wiki/Download',

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = ['babel', 'babel.messages', 'babel.localtime'],
    package_data = {'babel': ['global.dat', 'localedata/*.dat']},
    install_requires=[
        'pytz',
    ],

    cmdclass = {'build_doc': build_doc, 'test_doc': test_doc},

    zip_safe = False,
    test_suite = 'babel.tests.suite',

    entry_points = """
    [console_scripts]
    pybabel = babel.messages.frontend:main

    [distutils.commands]
    compile_catalog = babel.messages.frontend:compile_catalog
    extract_messages = babel.messages.frontend:extract_messages
    init_catalog = babel.messages.frontend:init_catalog
    update_catalog = babel.messages.frontend:update_catalog

    [distutils.setup_keywords]
    message_extractors = babel.messages.frontend:check_message_extractors

    [babel.checkers]
    num_plurals = babel.messages.checkers:num_plurals
    python_format = babel.messages.checkers:python_format

    [babel.extractors]
    ignore = babel.messages.extract:extract_nothing
    python = babel.messages.extract:extract_python
    javascript = babel.messages.extract:extract_javascript
    """
)
