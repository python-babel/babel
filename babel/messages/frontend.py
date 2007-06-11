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

"""Frontends for the message extraction functionality."""

from ConfigParser import RawConfigParser
from distutils import log
from distutils.cmd import Command
from distutils.errors import DistutilsOptionError, DistutilsSetupError
from optparse import OptionParser
import os
import re
from StringIO import StringIO
import sys

from babel import __version__ as VERSION
from babel import Locale
from babel.core import UnknownLocaleError
from babel.messages.catalog import Catalog
from babel.messages.extract import extract_from_dir, DEFAULT_KEYWORDS, \
                                   DEFAULT_MAPPING
from babel.messages.pofile import write_po, write_pot
from babel.messages.plurals import PLURALS
from babel.util import odict

__all__ = ['CommandLineInterface', 'extract_messages',
           'check_message_extractors', 'main']
__docformat__ = 'restructuredtext en'


class extract_messages(Command):
    """Message extraction command for use in ``setup.py`` scripts.

    If correctly installed, this command is available to Setuptools-using
    setup scripts automatically. For projects using plain old ``distutils``,
    the command needs to be registered explicitly in ``setup.py``::

        from babel.messages.frontend import extract_messages

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
        ('mapping-file=', 'F',
         'path to the mapping configuration file'),
        ('no-location', None,
         'do not include location comments with filename and line number'),
        ('omit-header', None,
         'do not include msgid "" entry in header'),
        ('output-file=', 'o',
         'name of the output file'),
        ('width=', 'w',
         'set output line width (default 76)'),
        ('no-wrap', None,
         'do not break long message lines, longer than the output line width, '
         'into several lines'),
        ('sort-output', None,
         'generate sorted output (default False)'),
        ('sort-by-file', None,
         'sort output by file location (default False)'),
        ('msgid-bugs-address=', None,
         'set report address for msgid'),
        ('copyright-holder=', None,
         'set copyright holder in output'),
        ('add-comments=', 'c',
         'place comment block with TAG (or those preceding keyword lines) in '
         'output file. Seperate multiple TAGs with commas(,)'),
        ('input-dirs=', None,
         'directories that should be scanned for messages'),
    ]
    boolean_options = [
        'no-default-keywords', 'no-location', 'omit-header', 'no-wrap',
        'sort-output', 'sort-by-file'
    ]

    def initialize_options(self):
        self.charset = 'utf-8'
        self.keywords = self._keywords = DEFAULT_KEYWORDS.copy()
        self.no_default_keywords = False
        self.mapping_file = None
        self.no_location = False
        self.omit_header = False
        self.output_file = None
        self.input_dirs = None
        self.width = 76
        self.no_wrap = False
        self.sort_output = False
        self.sort_by_file = False
        self.msgid_bugs_address = None
        self.copyright_holder = None
        self.add_comments = None
        self._add_comments = None

    def finalize_options(self):
        if self.no_default_keywords and not self.keywords:
            raise DistutilsOptionError('you must specify new keywords if you '
                                       'disable the default ones')
        if self.no_default_keywords:
            self._keywords = {}
        if isinstance(self.keywords, basestring):
            self._keywords.update(parse_keywords(self.keywords.split()))
        self.keywords = self._keywords

        if self.no_wrap and self.width:
            raise DistutilsOptionError("'--no-wrap' and '--width' are mutually "
                                       "exclusive")
        if self.no_wrap:
            self.width = None
        else:
            self.width = int(self.width)
            
        if self.sort_output and self.sort_by_file:
            raise DistutilsOptionError("'--sort-output' and '--sort-by-file' "
                                       "are mutually exclusive")

        if not self.input_dirs:
            self.input_dirs = dict.fromkeys([k.split('.',1)[0] 
                for k in self.distribution.packages 
            ]).keys()
            
        if self.add_comments:
            self._add_comments = self.add_comments.split(',')

    def run(self):
        mappings = self._get_mappings()
        outfile = open(self.output_file, 'w')
        try:
            catalog = Catalog(msgid_bugs_address=self.msgid_bugs_address)
            for dirname, (method_map, options_map) in mappings.items():
                def callback(filename, method, options):
                    if method == 'ignore':
                        return
                    filepath = os.path.normpath(os.path.join(dirname, filename))
                    optstr = ''
                    if options:
                        optstr = ' (%s)' % ', '.join(['%s="%s"' % (k, v) for
                                                      k, v in options.items()])
                    log.info('extracting messages from %s%s'
                             % (filepath, optstr))

                extracted = extract_from_dir(dirname, method_map, options_map,
                                             keywords=self.keywords,
                                             comment_tags=self._add_comments,
                                             callback=callback)
                for filename, lineno, message, comments in extracted:
                    filepath = os.path.normpath(os.path.join(dirname, filename))
                    catalog.add(message, None, [(filepath, lineno)],
                                comments=comments)

            log.info('writing PO template file to %s' % self.output_file)
            write_pot(outfile, catalog, project=self.distribution.get_name(),
                     version=self.distribution.get_version(), width=self.width,
                     charset=self.charset, no_location=self.no_location,
                     omit_header=self.omit_header, sort_output=self.sort_output,
                     sort_by_file=self.sort_by_file,
                     copyright_holder=self.copyright_holder)
        finally:
            outfile.close()

    def _get_mappings(self):
        mappings = {}

        if self.mapping_file:
            fileobj = open(self.mapping_file, 'U')
            try:
                method_map, options_map = parse_mapping(fileobj)
                for dirname in self.input_dirs:
                    mappings[dirname] = method_map, options_map
            finally:
                fileobj.close()

        elif self.distribution.message_extractors:
            message_extractors = self.distribution.message_extractors
            for dirname, mapping in message_extractors.items():
                if isinstance(mapping, basestring):
                    method_map, options_map = parse_mapping(StringIO(mapping))
                else:
                    method_map, options_map = [], {}
                    for pattern, method, options in mapping:
                        method_map.append((pattern, method))
                        options_map[pattern] = options or {}
                mappings[dirname] = method_map, options_map

        else:
            for dirname in self.input_dirs:
                mappings[dirname] = DEFAULT_MAPPING, {}

        return mappings


def check_message_extractors(dist, name, value):
    """Validate the ``message_extractors`` keyword argument to ``setup()``.

    :param dist: the distutils/setuptools ``Distribution`` object
    :param name: the name of the keyword argument (should always be
                 "message_extractors")
    :param value: the value of the keyword argument
    :raise `DistutilsSetupError`: if the value is not valid
    :see: `Adding setup() arguments
           <http://peak.telecommunity.com/DevCenter/setuptools#adding-setup-arguments>`_
    """
    assert name == 'message_extractors'
    if not isinstance(value, dict):
        raise DistutilsSetupError('the value of the "message_extractors" '
                                  'parameter must be a dictionary')


class new_catalog(Command):
    """New catalog command for use in ``setup.py`` scripts.

    If correctly installed, this command is available to Setuptools-using
    setup scripts automatically. For projects using plain old ``distutils``,
    the command needs to be registered explicitly in ``setup.py``::

        from babel.messages.frontend import new_catalog

        setup(
            ...
            cmdclass = {'new_catalog': new_catalog}
        )

    :see: `Integrating new distutils commands <http://docs.python.org/dist/node32.html>`_
    :see: `setuptools <http://peak.telecommunity.com/DevCenter/setuptools>`_
    """

    description = 'create new catalogs based on a catalog template'
    user_options = [
        ('domain=', 'D',
         "domain of PO file (defaults to lower-cased project name)"),
        ('input-file=', 'i',
         'name of the input file'),
        ('output-dir=', 'd',
         'path to output directory'),
        ('output-file=', 'o',
         "name of the output file (default "
         "'<output_dir>/<locale>/LC_MESSAGES/<domain>.po')"),
        ('locale=', 'l',
         'locale for the new localized catalog'),
        ('first-author=', None,
         'name of first author'),
        ('first-author-email=', None,
         'email of first author')
    ]

    def initialize_options(self):
        self.output_dir = None
        self.output_file = None
        self.input_file = None
        self.locale = None
        self.domain = None
        self.first_author = None
        self.first_author_email = None

    def finalize_options(self):
        if not self.input_file:
            raise DistutilsOptionError('you must specify the input file')

        if not self.domain:
            self.domain = self.distribution.get_name().lower()

        if not self.locale:
            raise DistutilsOptionError('you must provide a locale for the '
                                       'new catalog')
        else:
            try:
                self._locale = Locale.parse(self.locale)
            except UnknownLocaleError, error:
                log.error(error)
                sys.exit(1)

        if self._locale.territory.lower() == self._locale.language:
            # Remove country part if equal to language
            # XXX: This might not be the best behaviour, investigate
            self.locale = self._locale.language

        if not self.output_file and not self.output_dir:
            raise DistutilsOptionError('you must specify the output directory')

        if not self.output_file and self.output_dir:
            self.output_file = os.path.join(self.output_dir,
                                            self.locale,
                                            'LC_MESSAGES',
                                            self.domain + '.po')

        if not os.path.exists(os.path.dirname(self.output_file)):
            os.makedirs(os.path.dirname(self.output_file))

    def run(self):
        outfile = open(self.output_file, 'w')
        infile = open(self.input_file, 'r')

        if PLURALS.has_key(str(self._locale)):
            # Try <language>_<COUNTRY> if passed by user
            plurals = PLURALS[str(self._locale)]
        elif PLURALS.has_key(self._locale.language):
            # Try <language>
            plurals = PLURALS[self._locale.language]
        else:
            plurals = ('INTEGER', 'EXPRESSION')

        log.info('Creating %s %r PO from %r PO template',
                 self._locale.english_name,
                 self.output_file,
                 self.input_file)

        write_po(outfile, infile, self._locale,
                 project=self.distribution.get_name(),
                 version=self.distribution.get_version(),
                 plurals=plurals,
                 first_author=self.first_author,
                 first_author_email=self.first_author_email)

        infile.close()
        outfile.close()


class CommandLineInterface(object):
    """Command-line interface.

    This class provides a simple command-line interface to the message
    extraction and PO file generation functionality.
    """

    usage = '%%prog %s [options] %s'
    version = '%%prog %s' % VERSION
    commands = ['extract', 'init']
    command_descriptions = {
        'extract': 'extract messages from source files and generate a POT file',
        'init': 'create new message catalogs from a template'
    }

    def run(self, argv=sys.argv):
        """Main entry point of the command-line interface.

        :param argv: list of arguments passed on the command-line
        """
        self.parser = OptionParser(usage=self.usage % ('subcommand', '[args]'),
                              version=self.version)
        self.parser.disable_interspersed_args()
        self.parser.print_help = self._help
        options, args = self.parser.parse_args(argv[1:])
        if not args:
            self.parser.error('incorrect number of arguments')

        cmdname = args[0]
        if cmdname not in self.commands:
            self.parser.error('unknown subcommand "%s"' % cmdname)

        getattr(self, cmdname)(args[1:])

    def _help(self):
        print self.parser.format_help()
        print "Subcommands:"
        longest = max([len(command) for command in self.commands])
        format = "    %" + str(longest) + "s  %s"
        self.commands.sort()
        for command in self.commands:
            print format % (command, self.command_descriptions[command])

    def extract(self, argv):
        """Subcommand for extracting messages from source files and generating
        a POT file.

        :param argv: the command arguments
        """
        parser = OptionParser(usage=self.usage % ('extract', 'dir1 <dir2> ...'),
                              description=self.command_descriptions['extract'])
        parser.add_option('--charset', dest='charset',
                          help='charset to use in the output')
        parser.add_option('-k', '--keyword', dest='keywords', action='append',
                          help='keywords to look for in addition to the '
                               'defaults. You can specify multiple -k flags on '
                               'the command line.')
        parser.add_option('--no-default-keywords', dest='no_default_keywords',
                          action='store_true',
                          help="do not include the default keywords")
        parser.add_option('--mapping', '-F', dest='mapping_file',
                          help='path to the extraction mapping file')
        parser.add_option('--no-location', dest='no_location',
                          action='store_true',
                          help='do not include location comments with filename '
                               'and line number')
        parser.add_option('--omit-header', dest='omit_header',
                          action='store_true',
                          help='do not include msgid "" entry in header')
        parser.add_option('-o', '--output', dest='output',
                          help='path to the output POT file')
        parser.add_option('-w', '--width', dest='width', type='int',
                          help="set output line width (default %default)")
        parser.add_option('--no-wrap', dest='no_wrap', action = 'store_true',
                          help='do not break long message lines, longer than '
                               'the output line width, into several lines')
        parser.add_option('--sort-output', dest='sort_output',
                          action='store_true',
                          help='generate sorted output (default False)')
        parser.add_option('--sort-by-file', dest='sort_by_file',
                          action='store_true',
                          help='sort output by file location (default False)')
        parser.add_option('--msgid-bugs-address', dest='msgid_bugs_address',
                          metavar='EMAIL@ADDRESS',
                          help='set report address for msgid')
        parser.add_option('--copyright-holder', dest='copyright_holder',
                          help='set copyright holder in output')
        parser.add_option('--add-comments', '-c', dest='add_comments',
                          metavar='TAG', action='append',
                          help='place comment block with TAG (or those '
                               'preceding keyword lines) in output file. One '
                               'TAG per argument call')

        parser.set_defaults(charset='utf-8', keywords=[],
                            no_default_keywords=False, no_location=False,
                            omit_header = False, width=76, no_wrap=False,
                            sort_output=False, sort_by_file=False,
                            add_comments=[])
        options, args = parser.parse_args(argv)
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

        if options.mapping_file:
            fileobj = open(options.mapping_file, 'U')
            try:
                method_map, options_map = parse_mapping(fileobj)
            finally:
                fileobj.close()
        else:
            method_map = DEFAULT_MAPPING
            options_map = {}

        if options.width and options.no_wrap:
            parser.error("'--no-wrap' and '--width' are mutually exclusive.")
        elif not options.width and not options.no_wrap:
            options.width = 76
        elif not options.width and options.no_wrap:
            options.width = 0

        if options.sort_output and options.sort_by_file:
            parser.error("'--sort-output' and '--sort-by-file' are mutually "
                         "exclusive")

        try:
            catalog = Catalog(msgid_bugs_address=options.msgid_bugs_address)
            for dirname in args:
                if not os.path.isdir(dirname):
                    parser.error('%r is not a directory' % dirname)
                extracted = extract_from_dir(dirname, method_map,
                                             options_map, keywords,
                                             comment_tags=options.comments)
                for filename, lineno, message, comments in extracted:
                    filepath = os.path.normpath(os.path.join(dirname, filename))
                    catalog.add(message, None, [(filepath, lineno)], 
                                comments=comments)

            write_pot(outfile, catalog, width=options.width,
                      charset=options.charset, no_location=options.no_location,
                      omit_header=options.omit_header,
                      sort_output=options.sort_output,
                      sort_by_file=options.sort_by_file,
                      copyright_holder=options.copyright_holder)
        finally:
            if options.output:
                outfile.close()

    def init(self, argv):
        """Subcommand for creating new message catalogs from a template.

        :param argv: the command arguments
        """
        parser = OptionParser(usage=self.usage % ('init',''),
                              description=self.command_descriptions['init'])
        parser.add_option('--domain', '-D', dest='domain',
                          help="domain of PO file (defaults to lower-cased "
                               "project name)")
        parser.add_option('--input-file', '-i', dest='input_file',
                          help='name of the input file')
        parser.add_option('--output-dir', '-d', dest='output_dir',
                          help='path to output directory')
        parser.add_option('--output-file', '-o', dest='output_file',
                          help="name of the output file (default "
                               "'<output_dir>/<locale>/LC_MESSAGES/"
                               "<domain>.po')")
        parser.add_option('--locale', '-l', dest='locale',
                          help='locale for the new localized catalog')
        parser.add_option('--first-author', dest='first_author',
                          metavar='FIRST_AUTHOR_NAME',
                          help='name of first author')
        parser.add_option('--first-author-email', dest='first_author_email',
                          help='email of first author')
        parser.add_option('--project-name', dest='project_name', metavar='NAME',
                          default='PROJECT', help='the project name')
        parser.add_option('--project-version', dest='project_version',
                          metavar='VERSION', help='the project version')

        options, args = parser.parse_args(argv)

        if not options.project_name:
            parser.error('please provide the project name')

        if not options.project_version:
            parser.error('please provide the project version')

        if not options.input_file:
            parser.error('you must specify the input file')

        if not options.domain:
            options.domain = options.project_name.lower()

        if not options.locale:
            parser.error('you must provide a locale for the new catalog')
        else:
            try:
                _locale = Locale.parse(options.locale)
            except UnknownLocaleError, error:
                parser.error(error)

        if _locale.territory.lower() == _locale.language:
            # Remove country part if equal to language
            # XXX: This might not be the best behaviour, investigate
            options.locale = _locale.language

        if not options.output_file and not options.output_dir:
            parser.error('you must specify the output directory')

        if not options.output_file and options.output_dir:
            options.output_file = os.path.join(options.output_dir,
                                               options.locale,
                                               'LC_MESSAGES',
                                               options.domain + '.po')
        if not os.path.exists(os.path.dirname(options.output_file)):
            os.makedirs(os.path.dirname(options.output_file))

        outfile = open(options.output_file, 'w')
        infile = open(options.input_file, 'r')

        if PLURALS.has_key(str(_locale)):
            # Try <language>_<COUNTRY> if passed by user
            plurals = PLURALS[str(_locale)]
        elif PLURALS.has_key(_locale.language):
            # Try <language>
            plurals = PLURALS[_locale.language]
        else:
            plurals = ('INTEGER', 'EXPRESSION')

        print 'Creating %s %r PO from %r PO template' % (_locale.english_name,
                                                         options.output_file,
                                                         options.input_file)

        write_po(outfile, infile, _locale,
                 project=options.project_name,
                 version=options.project_version,
                 plurals=plurals,
                 first_author=options.first_author,
                 first_author_email=options.first_author_email)

        infile.close()
        outfile.close()

def main():
    CommandLineInterface().run(sys.argv)

def parse_mapping(fileobj, filename=None):
    """Parse an extraction method mapping from a file-like object.

    >>> buf = StringIO('''
    ... # Python source files
    ... [python: **.py]
    ...
    ... # Genshi templates
    ... [genshi: **/templates/**.html]
    ... include_attrs =
    ... [genshi: **/templates/**.txt]
    ... template_class = genshi.template.text.TextTemplate
    ... encoding = latin-1
    ... ''')

    >>> method_map, options_map = parse_mapping(buf)

    >>> method_map[0]
    ('**.py', 'python')
    >>> options_map['**.py']
    {}
    >>> method_map[1]
    ('**/templates/**.html', 'genshi')
    >>> options_map['**/templates/**.html']['include_attrs']
    ''
    >>> method_map[2]
    ('**/templates/**.txt', 'genshi')
    >>> options_map['**/templates/**.txt']['template_class']
    'genshi.template.text.TextTemplate'
    >>> options_map['**/templates/**.txt']['encoding']
    'latin-1'

    :param fileobj: a readable file-like object containing the configuration
                    text to parse
    :return: a `(method_map, options_map)` tuple
    :rtype: `tuple`
    :see: `extract_from_directory`
    """
    method_map = []
    options_map = {}

    parser = RawConfigParser()
    parser._sections = odict(parser._sections) # We need ordered sections
    parser.readfp(fileobj, filename)
    for section in parser.sections():
        method, pattern = [part.strip() for part in section.split(':', 1)]
        method_map.append((pattern, method))
        options_map[pattern] = dict(parser.items(section))

    return (method_map, options_map)

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
