#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

from distutils.cmd import Command
import doctest
from glob import glob
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import sys


class build_doc(Command):
    description = 'Builds the documentation'
    user_options = [
        ('force', None,
         "force regeneration even if no reStructuredText files have changed"),
        ('without-apidocs', None,
         "whether to skip the generation of API documentaton"),
    ]
    boolean_options = ['force', 'without-apidocs']

    def initialize_options(self):
        self.force = False
        self.without_apidocs = False

    def finalize_options(self):
        pass

    def run(self):
        from docutils.core import publish_cmdline
        from docutils.nodes import raw
        from docutils.parsers import rst

        docutils_conf = os.path.join('doc', 'conf', 'docutils.ini')
        epydoc_conf = os.path.join('doc', 'conf', 'epydoc.ini')

        try:
            from pygments import highlight
            from pygments.lexers import get_lexer_by_name
            from pygments.formatters import HtmlFormatter

            def code_block(name, arguments, options, content, lineno,
                           content_offset, block_text, state, state_machine):
                lexer = get_lexer_by_name(arguments[0])
                html = highlight('\n'.join(content), lexer, HtmlFormatter())
                return [raw('', html, format='html')]
            code_block.arguments = (1, 0, 0)
            code_block.options = {'language' : rst.directives.unchanged}
            code_block.content = 1
            rst.directives.register_directive('code-block', code_block)
        except ImportError:
            print 'Pygments not installed, syntax highlighting disabled'

        for source in glob('doc/*.txt'):
            dest = os.path.splitext(source)[0] + '.html'
            if self.force or not os.path.exists(dest) or \
                    os.path.getmtime(dest) < os.path.getmtime(source):
                print 'building documentation file %s' % dest
                publish_cmdline(writer_name='html',
                                argv=['--config=%s' % docutils_conf, source,
                                      dest])

        if not self.without_apidocs:
            try:
                from epydoc import cli
                old_argv = sys.argv[1:]
                sys.argv[1:] = [
                    '--config=%s' % epydoc_conf,
                    '--no-private', # epydoc bug, not read from config
                    '--simple-term',
                    '--verbose'
                ]
                cli.cli()
                sys.argv[1:] = old_argv

            except ImportError:
                print 'epydoc not installed, skipping API documentation.'


class test_doc(Command):
    description = 'Tests the code examples in the documentation'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for filename in glob('doc/*.txt'):
            print 'testing documentation file %s' % filename
            doctest.testfile(filename, False, optionflags=doctest.ELLIPSIS)


setup(
    name = 'Babel',
    version = '0.9',
    description = 'Internationalization utilities',
    long_description = \
"""A collection of tools for internationalizing Python applications.""",
    author = 'Edgewall Software',
    author_email = 'info@edgewall.org',
    license = 'BSD',
    url = 'http://babel.edgewall.org/',
    download_url = 'http://babel.edgewall.org/wiki/Download',
    zip_safe = False,

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = ['babel', 'babel.messages'],
    package_data = {'babel': ['localedata/*.dat']},
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
    """,

    cmdclass = {'build_doc': build_doc, 'test_doc': test_doc}
)
