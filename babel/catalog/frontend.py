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
from babel.catalog.extract import extract_from_dir, DEFAULT_KEYWORDS, \
                                  DEFAULT_MAPPING
from babel.catalog.pofile import write_po, write_pot
from babel.catalog.plurals import PLURALS

__all__ = ['CommandLineInterface', 'extract_messages',
           'check_message_extractors', 'main']
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
         'into several lines')
    ]
    boolean_options = [
        'no-default-keywords', 'no-location', 'omit-header', 'no-wrap'
    ]

    def initialize_options(self):
        self.charset = 'utf-8'
        self.keywords = self._keywords = DEFAULT_KEYWORDS.copy()
        self.no_default_keywords = False
        self.mapping_file = None
        self.no_location = False
        self.omit_header = False
        self.output_file = None
        self.width = 76
        self.no_wrap = False

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
            raise DistutilsOptionError("'--no-wrap' and '--width' are mutually"
                                       "exclusive")
        if self.no_wrap:
            self.width = None
        else:
            self.width = int(self.width)

    def run(self):
        if self.mapping_file:
            fileobj = open(self.mapping_file, 'U')
            try:
                method_map, options_map = parse_mapping(fileobj)
            finally:
                fileobj.close()
        elif self.distribution.message_extractors:
            message_extractors = self.distribution.message_extractors
            if isinstance(message_extractors, basestring):
                method_map, options_map = parse_mapping(StringIO(
                    message_extractors
                ))
            else:
                method_map = {}
                options_map = {}
                for pattern, (method, options) in message_extractors.items():
                    method_map[pattern] = method
                    options_map[pattern] = options
        else:
            method_map = DEFAULT_MAPPING
            options_map = {}

        outfile = open(self.output_file, 'w')
        try:
            def callback(filename, options):
                optstr = ''
                if options:
                    optstr = ' (%s)' % ', '.join(['%s="%s"' % (k, v) for k, v
                                                  in options.items()])
                log.info('extracting messages from %s%s' % (filename, optstr))

            messages = []
            extracted = extract_from_dir(method_map=method_map,
                                         options_map=options_map,
                                         keywords=self.keywords,
                                         callback=callback)
            for filename, lineno, funcname, message in extracted:
                filepath = os.path.normpath(filename)
                messages.append((filepath, lineno, funcname, message, None))

            log.info('writing PO template file to %s' % self.output_file)
            write_pot(outfile, messages, project=self.distribution.get_name(),
                     version=self.distribution.get_version(), width=self.width,
                     charset=self.charset, no_location=self.no_location,
                     omit_header=self.omit_header)
        finally:
            outfile.close()


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
    if not isinstance(value, (basestring, dict)):
        raise DistutilsSetupError('the value of the "extract_messages" '
                                  'parameter must be a string or dictionary')


class new_catalog(Command):
    """New catalog command for use in ``setup.py`` scripts.

    If correctly installed, this command is available to Setuptools-using
    setup scripts automatically. For projects using plain old ``distutils``,
    the command needs to be registered explicitly in ``setup.py``::

        from babel.catalog.frontend import new_catalog

        setup(
            ...
            cmdclass = {'new_catalog': new_catalog}
        )

    :see: `Integrating new distutils commands <http://docs.python.org/dist/node32.html>`_
    :see: `setuptools <http://peak.telecommunity.com/DevCenter/setuptools>`_
    """

    description = 'create new catalogs based on a catalog template'
    user_options = [
        ('input-file=', 'i',
         'name of the input file'),
        ('output-dir=', 'd',
         'path to output directory'),
        ('output-file=', 'o',
         "name of the output file (default "
         "'<output_dir>/<locale>.po')"),
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
        self.first_author = None
        self.first_author_email = None

    def finalize_options(self):
        if not self.input_file:
            raise DistutilsOptionError('you must specify the input file')

        if not self.locale:
            raise DistutilsOptionError('you must provide a locale for the '
                                       'new catalog')
        else:
            try:
                locale = Locale.parse(self.locale)
            except UnknownLocaleError, error:
                log.error(error)
                sys.exit(1)

        self._locale_parts = self.locale.split('_')
        self._language = None
        self._country = None
        _locale = Locale('en')
        if len(self._locale_parts) == 2:
            if self._locale_parts[0] == self._locale_parts[1].lower():
                # Remove country part if equal to language
                locale = self._locale_parts[0]
            else:
                locale = self.locale
            self._language = _locale.languages[self._locale_parts[0]]
            self._country = _locale.territories[self._locale_parts[1]]
        else:
            locale = self._locale_parts[0]
            self._language = _locale.languages[locale]

        if not self.output_file and not self.output_dir:
            raise DistutilsOptionError('you must specify the output directory')

        if not self.output_file and self.output_dir:
            self.output_file = os.path.join(self.output_dir, locale + '.po')

    def run(self):
        outfile = open(self.output_file, 'w')
        infile = open(self.input_file, 'r')

        if PLURALS.has_key(self.locale):
            # Try <language>_<COUNTRY>
            plurals = PLURALS[self.locale]
        elif PLURALS.has_key(self._locale_parts[0]):
            # Try <language>
            plurals = PLURALS[self._locale_parts[0]]
        else:
            plurals = ('INTEGER', 'EXPRESSION')

        if self._country:
            logline = 'Creating %%s (%s) %%r PO from %%r' % self._country + \
                      ' PO template'
        else:
            logline = 'Creating %s %r PO from %r PO template'
        log.info(logline, self._language, self.output_file, self.input_file)

        write_po(outfile, infile, self._language, country=self._country,
                 project=self.distribution.get_name(),
                 version=self.distribution.get_version(),
                 charset=self.charset, plurals=plurals,
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

    def run(self, argv=sys.argv):
        """Main entry point of the command-line interface.

        :param argv: list of arguments passed on the command-line
        """
        parser = OptionParser(usage=self.usage % ('subcommand', '[args]'),
                              version=self.version)
        parser.disable_interspersed_args()
        options, args = parser.parse_args(argv[1:])
        if not args:
            parser.error('incorrect number of arguments')

        cmdname = args[0]
        if cmdname not in self.commands:
            parser.error('unknown subcommand "%s"' % cmdname)

        getattr(self, cmdname)(args[1:])

    def extract(self, argv):
        """Subcommand for extracting messages from source files and generating
        a POT file.

        :param argv: the command arguments
        """
        parser = OptionParser(usage=self.usage % ('extract', 'dir1 <dir2> ...'))
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

        parser.set_defaults(charset='utf-8', keywords=[],
                            no_default_keywords=False, no_location=False,
                            omit_header = False, width=76, no_wrap=False)
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

        try:
            messages = []
            for dirname in args:
                if not os.path.isdir(dirname):
                    parser.error('%r is not a directory' % dirname)
                extracted = extract_from_dir(dirname, method_map, options_map,
                                             keywords)
                for filename, lineno, funcname, message in extracted:
                    filepath = os.path.normpath(os.path.join(dirname, filename))
                    messages.append((filepath, lineno, funcname, message, None))
            write_po(outfile, messages, width=options.width,
                     charset=options.charset, no_location=options.no_location,
                     omit_header=options.omit_header)
        finally:
            if options.output:
                outfile.close()

    def init(self, argv):
        """Subcommand for creating new message catalogs from a template.

        :param argv: the command arguments
        """
        raise NotImplementedError

def main():
    CommandLineInterface().run(sys.argv)

def parse_mapping(fileobj, filename=None):
    """Parse an extraction method mapping from a file-like object.

    >>> buf = StringIO('''
    ... # Python source files
    ... [python: foobar/**.py]
    ...
    ... # Genshi templates
    ... [genshi: foobar/**/templates/**.html]
    ... include_attrs =
    ... [genshi: foobar/**/templates/**.txt]
    ... template_class = genshi.template.text.TextTemplate
    ... encoding = latin-1
    ... ''')

    >>> method_map, options_map = parse_mapping(buf)

    >>> method_map['foobar/**.py']
    'python'
    >>> options_map['foobar/**.py']
    {}
    >>> method_map['foobar/**/templates/**.html']
    'genshi'
    >>> options_map['foobar/**/templates/**.html']['include_attrs']
    ''
    >>> method_map['foobar/**/templates/**.txt']
    'genshi'
    >>> options_map['foobar/**/templates/**.txt']['template_class']
    'genshi.template.text.TextTemplate'
    >>> options_map['foobar/**/templates/**.txt']['encoding']
    'latin-1'

    :param fileobj: a readable file-like object containing the configuration
                    text to parse
    :return: a `(method_map, options_map)` tuple
    :rtype: `tuple`
    :see: `extract_from_directory`
    """
    method_map = {}
    options_map = {}

    parser = RawConfigParser()
    parser.readfp(fileobj, filename)
    for section in parser.sections():
        method, pattern = [part.strip() for part in section.split(':', 1)]
        method_map[pattern] = method
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
    extract_cmdline()
