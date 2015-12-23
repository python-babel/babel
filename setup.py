# -*- coding: utf-8 -*-

import sys
if sys.version_info < (2, 6) or (3,) <= sys.version_info < (3, 3):
    print("Babel requires Python 2.6, 2.7 or 3.3+")
    sys.exit(1)


import os
import subprocess
from setuptools import setup

from babel import __version__

sys.path.append(os.path.join('doc', 'common'))
try:
    from doctools import build_doc, test_doc
except ImportError:
    build_doc = test_doc = None


from distutils.cmd import Command


class import_cldr(Command):
    description = 'imports and converts the CLDR data'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        c = subprocess.Popen([sys.executable, 'scripts/download_import_cldr.py'])
        c.wait()


setup(
    name='Babel',
    version=__version__,
    description='Internationalization utilities',
    long_description=\
"""A collection of tools for internationalizing Python applications.""",
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    license='BSD',
    url='http://babel.pocoo.org/',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['babel', 'babel.messages', 'babel.localtime'],
    include_package_data=True,
    install_requires=[
        # This version identifier is currently necessary as
        # pytz otherwise does not install on pip 1.4 or
        # higher.
        'pytz>=0a',
    ],

    cmdclass={'build_doc': build_doc, 'test_doc': test_doc,
              'import_cldr': import_cldr},

    zip_safe=False,

    # Note when adding extractors: builtin extractors we also want to
    # work if packages are not installed to simplify testing.  If you
    # add an extractor here also manually add it to the "extract"
    # function in babel.messages.extract.
    entry_points="""
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
