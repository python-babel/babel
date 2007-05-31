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
from distutils.errors import DistutilsOptionError
from optparse import OptionParser
import os
import sys

from babel import __version__ as VERSION
from babel.catalog.extract import extract_from_dir, DEFAULT_KEYWORDS
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
         'do not include the default keywords'),
        ('no-location', None,
         'do not include location comments with filename and line number'),
        ('omit-header', None,
         'do not include msgid "" entry in header'),
        ('output-file=', 'o',
         'name of the output file'),
        ('width=', 'w',
         'set output line width. Default: 76'),
        ('no-wrap', None,
         'do not break long message lines, longer than the output '
         'line width, into several lines.')
    ]
    boolean_options = [
        'no-default-keywords', 'no-location', 'omit-header', 'no-wrap'
    ]

    def initialize_options(self):
        self.charset = 'utf-8'
        self.keywords = self._keywords = DEFAULT_KEYWORDS.copy()
        self.no_default_keywords = False
        self.no_location = False
        self.omit_header = False
        self.output_file = None
        self.input_dirs = None
        self.width = None
        self.no_wrap = False

    def finalize_options(self):
        if not self.input_dirs:
            self.input_dirs = dict.fromkeys([k.split('.',1)[0]
                for k in self.distribution.packages
            ]).keys()
        if self.no_default_keywords and not self.keywords:
            raise DistutilsOptionError, \
                'you must specify new keywords if you disable the default ones'
        if self.no_default_keywords:
            self._keywords = {}
        if isinstance(self.keywords, basestring):
            self._keywords.update(parse_keywords(self.keywords.split()))
        self.keywords = self._keywords
        if self.no_wrap and self.width:
            raise DistutilsOptionError, \
                "'--no-wrap' and '--width' are mutually exclusive."
        elif self.no_wrap and not self.width:
            self.width = 0
        elif not self.no_wrap and not self.width:
            self.width = 76
        elif self.width and not self.no_wrap:
            self.width = int(self.width)

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
                     omit_header=self.omit_header, width=self.width)
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
    parser.add_option('-w', '--width', dest='width', type='int',
                      help="set output line width. Default: 76")
    parser.add_option('--no-wrap', dest='no_wrap', default=False,
                      action = 'store_true', help='do not break long message '
                      'lines, longer than the output line width, into several '
                      'lines.')
    options, args = parser.parse_args(argv[1:])
    if not args:
        parser.error('incorrect number of arguments')

    if options.output not in (None, '-'):
        outfile = open(options.output, 'w')
    else:
        outfile = sys.stdout

    keywords = DEFAULT_KEYWORDS.copy()
    if options.no_default_keywords:
        if not options.keywords:
            parser.error('you must specify new keywords if you disable the '
                         'default ones')
        keywords = {}
    if options.keywords:
        keywords.update(parse_keywords(options.keywords))
        
    if options.width and options.no_wrap:
        parser.error("'--no-wrap' and '--width' are mutually exclusive.")
    elif not options.width and not options.no_wrap:
        options.width = 76
    elif not options.width and options.no_wrap:
        options.width = 0

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
                 omit_header=options.omit_header, width=options.width)
    finally:
        if options.output:
            outfile.close()

def parse_keywords(strings=[]):
    """Parse keywords specifications from the given list of strings.
    
    >>> kw = parse_keywords(['_', 'dgettext:2', 'dngettext:2,3'])
    >>> for keyword, indices in sorted(kw.items()):
    ...     print (keyword, indices)
    ('_', None)
    ('dgettext', (2,))
    ('dngettext', (2, 3))
    """
    keywords = {}
    for string in strings:
        if ':' in string:
            funcname, indices = string.split(':')
        else:
            funcname, indices = string, None
        if funcname not in keywords:
            if indices:
                indices = tuple([(int(x)) for x in indices.split(',')])
            keywords[funcname] = indices
    return keywords

if __name__ == '__main__':
    main()
