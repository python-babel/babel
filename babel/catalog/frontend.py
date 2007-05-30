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
         'space-separated list of keywords to look for in addition to the '
         'defaults'),
        ('no-default-keywords', None,
         'do not include the default keywords defined by Babel'),
        ('no-location', None,
         'do not include location comments with filename and line number'),
        ('omit-header', None,
         'do not include msgid "" entry in header'),
        ('output-file=', 'o',
         'name of the output file'),
    ]
    boolean_options = ['no-location', 'omit-header', 'no-default-keywords']

    def initialize_options(self):
        self.charset = 'utf-8'
        self.keywords = KEYWORDS
        self.no_location = False
        self.omit_header = False
        self.output_file = None
        self.input_dirs = None
        self.no_default_keywords = False

    def finalize_options(self):
        if not self.input_dirs:
            self.input_dirs = dict.fromkeys([k.split('.',1)[0]
                for k in self.distribution.packages
            ]).keys()
        if isinstance(self.keywords, basestring):
            new_keywords = [k.strip() for k in self.keywords.split()]
            self.keywords = build_gettext_functions(
                                    new_keywords,
                                    dont_include_default=self.no_default_keywords
            )

    def run(self):
        outfile = open(self.output_file, 'w')
        try:
            messages = []
            for dirname in self.input_dirs:
                log.info('extracting messages from %r' % dirname)
                extracted = extract_from_dir(dirname, keywords=self.keywords)
                for filename, lineno, funcname, message in extracted:
                    messages.append((os.path.join(dirname, filename), lineno,
                                     funcname, message, None))
            write_po(outfile, messages, project=self.distribution.get_name(),
                     version=self.distribution.get_version(),
                     charset=self.charset, no_location=self.no_location,
                     omit_header=self.omit_header)
            log.info('writing PO file to %s' % self.output_file)
        finally:
            outfile.close()

def build_gettext_functions(func_list=[], dont_include_default=False):
    """Build the gettext function to parse."""
    if dont_include_default:
        func_dict = {}
    else:
        func_dict = KEYWORDS
    for func in func_list:
        if func.find(':') != -1:
            func_name, func_args = func.split(':')
        else:
            func_name, func_args = func, None
        if not func_dict.has_key(func_name):
            if func_args:
                str_indexes = [(int(x) -1 ) for x in func_args.split(',')]
            else:
                str_indexes = None
            func_dict[func_name] = str_indexes
    return func_dict
                
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
                      default=[], action='append',
                      help='keywords to look for in addition to the defaults. '
                           'You can specify multiple -k flags on the command '
                           'line.')
    parser.add_option('--no-default-keywords', dest='no_default_keywords',
                      action='store_true', default=False,
                      help="do not include the default keywords defined by "
                           "Babel")
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
        
    if options.no_default_keywords and not options.keywords:
        parser.error("you must pass keywords to disable the default ones")
    elif options.no_default_keywords and options.keywords:
        keywords = build_gettext_functions(options.keywords,
                            dont_include_default=options.no_default_keywords)
    else:
        keywords = build_gettext_functions()

    try:
        messages = []
        for dirname in args:
            if not os.path.isdir(dirname):
                parser.error('%r is not a directory' % dirname)
            extracted = extract_from_dir(dirname, keywords=keywords)
            for filename, lineno, funcname, message in extracted:
                messages.append((os.path.join(dirname, filename), lineno,
                                 funcname, message, None))
        write_po(outfile, messages,
                 charset=options.charset, no_location=options.no_location,
                 omit_header=options.omit_header)
    finally:
        if options.output:
            outfile.close()

if __name__ == '__main__':
    main()
