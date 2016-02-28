# -*- coding: utf-8 -*-

import subprocess
import sys
from distutils.cmd import Command

from setuptools import setup

try:
    from babel import __version__
except SyntaxError as exc:
    sys.stderr.write("Unable to import Babel (%s). Are you running a supported version of Python?\n" % exc)
    sys.exit(1)


class import_cldr(Command):
    description = 'imports and converts the CLDR data'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        subprocess.check_call([sys.executable, 'scripts/download_import_cldr.py'])


setup(
    name='Babel',
    version=__version__,
    description='Internationalization utilities',
    long_description="""A collection of tools for internationalizing Python applications.""",
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
        'Programming Language :: Python :: Implementation :: PyPy',
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

    cmdclass={'import_cldr': import_cldr},

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
