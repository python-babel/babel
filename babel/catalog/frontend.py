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

"""Frontends for the message extraction functionality."""

from distutils import log
from distutils.cmd import Command
from optparse import OptionParser
import os
import sys

from babel import __version__ as VERSION
from babel.catalog.extract import extract_from_dir, KEYWORDS
from babel.catalog.pofile import write_po

__all__ = ['extract_messages', 'main']
__docformat__ = 'restructuredtext en'


class extract_messages(Command):
    """Message extraction command for use in ``setup.py`` scripts.
    
    If correctly installed, this command is available to Setuptools-using
    setup scripts automatically. For projects using plain old ``distutils``,
    the command needs to be registered explicitly in ``setup.py``::
    
        from babel.catalog.frontend import extract_messages
    
        setup(
            ...
            cmdclass = {'extract_messages': extract_messages}
        )

    :see: `Integrating new distutils commands <http://docs.python.org/dist/node32.html>`_
    :see: `setuptools <http://peak.telecommunity.com/DevCenter/setuptools>`_
    """

    description = 'extract localizable strings from the project code'
    user_options = [
        ('charset=', None,
         'charset to use in the output file'),
        ('keywords=', 'k',
         'comma-separated list of keywords to look for in addition to the '
         'defaults'),
        ('no-location', None,
         'do not include location comments with filename and line number'),
        ('omit-header', None,
         'do not include msgid "" entry in header'),
        ('output-file=', 'o',
         'name of the output file'),
    ]
    boolean_options = ['no-location', 'omit-header']

    def initialize_options(self):
        self.charset = 'utf-8'
        self.keywords = KEYWORDS
        self.no_location = False
        self.omit_header = False
        self.output_file = None
        self.input_dirs = None

    def finalize_options(self):
        if not self.input_dirs:
            self.input_dirs = dict.fromkeys([k.split('.',1)[0]
                for k in self.distribution.packages
            ]).keys()
        if isinstance(self.keywords, basestring):
            new_keywords = [k.strip() for k in self.keywords.split(',')]
            self.keywords = list(KEYWORDS) + new_keywords

    def run(self):
        outfile = open(self.output_file, 'w')
        try:
            messages = []
            for dirname in self.input_dirs:
                log.info('extracting messages from %r' % dirname)
                extracted = extract_from_dir(dirname, keywords=self.keywords)
                for filename, lineno, funcname, message in extracted:
                    messages.append((os.path.join(dirname, filename), lineno,
                                     funcname, message))
            write_po(outfile, messages, project=self.distribution.get_name(),
                     version=self.distribution.get_version(),
                     charset=self.charset, no_location=self.no_location,
                     omit_header=self.omit_header)
            log.info('writing PO file to %s' % self.output_file)
        finally:
            outfile.close()


def main(argv=sys.argv):
    """Command-line interface.
    
    This function provides a simple command-line interface to the message
    extraction and PO file generation functionality.
    
    :param argv: list of arguments passed on the command-line
    """
    parser = OptionParser(usage='%prog [options] dirname1 <dirname2> ...',
                          version='%%prog %s' % VERSION)
    parser.add_option('--charset', dest='charset', default='utf-8',
                      help='charset to use in the output')
    parser.add_option('-k', '--keyword', dest='keywords',
                      default=list(KEYWORDS), action='append',
                      help='keywords to look for in addition to the defaults. '
                           'You can specify multiple -k flags on the command '
                           'line.')
    parser.add_option('--no-location', dest='no_location', default=False,
                      action='store_true',
                      help='do not include location comments with filename and '
                           'line number')
    parser.add_option('--omit-header', dest='omit_header', default=False,
                      action='store_true',
                      help='do not include msgid "" entry in header')
    parser.add_option('-o', '--output', dest='output',
                      help='path to the output POT file')
    options, args = parser.parse_args(argv[1:])
    if not args:
        parser.error('incorrect number of arguments')

    if options.output not in (None, '-'):
        outfile = open(options.output, 'w')
    else:
        outfile = sys.stdout

    try:
        messages = []
        for dirname in args:
            if not os.path.isdir(dirname):
                parser.error('%r is not a directory' % dirname)
            extracted = extract_from_dir(dirname, keywords=options.keywords)
            for filename, lineno, funcname, message in extracted:
                messages.append((os.path.join(dirname, filename), lineno,
                                 funcname, message))
        write_po(outfile, messages,
                 charset=options.charset, no_location=options.no_location,
                 omit_header=options.omit_header)
    finally:
        if options.output:
            outfile.close()

if __name__ == '__main__':
    main()
