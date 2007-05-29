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

"""Basic infrastructure for extracting localizable messages from source files.

This module defines an extensible system for collecting localizable message
strings from a variety of sources. A native extractor for Python source files
is builtin, extractors for other sources can be added using very simple plugins.

The main entry points into the extraction functionality are the functions
`extract_from_dir` and `extract_from_file`.
"""

import os
from pkg_resources import working_set
import sys
from tokenize import generate_tokens, NAME, OP, STRING

from babel.util import extended_glob

__all__ = ['extract', 'extract_from_dir', 'extract_from_file']
__docformat__ = 'restructuredtext en'

GROUP_NAME = 'babel.extractors'

KEYWORDS = (
    '_', 'gettext', 'ngettext',
    'dgettext', 'dngettext',
    'ugettext', 'ungettext'
)

DEFAULT_MAPPING = {
    'genshi': ['*.html', '**/*.html'],
    'python': ['*.py', '**/*.py']
}

def extract_from_dir(dirname, mapping=DEFAULT_MAPPING, keywords=KEYWORDS,
                     options=None):
    """Extract messages from any source files found in the given directory.
    
    This function generates tuples of the form:
    
        ``(filename, lineno, funcname, message)``
    
    Which extraction method used is per file is determined by the `mapping`
    parameter, which maps extraction method names to lists of extended glob
    patterns. For example, the following is the default mapping:
    
    >>> mapping = {
    ...     'python': ['*.py', '**/*.py']
    ... }
    
    This basically says that files with the filename extension ".py" at any
    level inside the directory should be processed by the "python" extraction
    method. Files that don't match any of the patterns are ignored.
    
    The following extended mapping would also use the "genshi" extraction method
    on any file in "templates" subdirectory:
    
    >>> mapping = {
    ...     'genshi': ['**/templates/*.*', '**/templates/**/*.*'],
    ...     'python': ['*.py', '**/*.py']
    ... }
    
    :param dirname: the path to the directory to extract messages from
    :param mapping: a mapping of extraction method names to extended glob
                    patterns
    :param keywords: a list of keywords (i.e. function names) that should be
                     recognized as translation functions
    :param options: a dictionary of additional options (optional)
    :return: an iterator over ``(filename, lineno, funcname, message)`` tuples
    :rtype: ``iterator``
    """
    extracted_files = {}
    for method, patterns in mapping.items():
        for pattern in patterns:
            for filename in extended_glob(pattern, dirname):
                if filename in extracted_files:
                    continue
                filepath = os.path.join(dirname, filename)
                for line, func, key in extract_from_file(method, filepath,
                                                         keywords=keywords,
                                                         options=options):
                    yield filename, line, func, key
                extracted_files[filename] = True

def extract_from_file(method, filename, keywords=KEYWORDS, options=None):
    """Extract messages from a specific file.
    
    This function returns a list of tuples of the form:
    
        ``(lineno, funcname, message)``
    
    :param filename: the path to the file to extract messages from
    :param method: a string specifying the extraction method (.e.g. "python")
    :param keywords: a list of keywords (i.e. function names) that should be
                     recognized as translation functions
    :param options: a dictionary of additional options (optional)
    :return: the list of extracted messages
    :rtype: `list`
    """
    fileobj = open(filename, 'U')
    try:
        return list(extract(method, fileobj, keywords, options=options))
    finally:
        fileobj.close()

def extract(method, fileobj, keywords=KEYWORDS, options=None):
    """Extract messages from the given file-like object using the specified
    extraction method.
    
    This function returns a list of tuples of the form:
    
        ``(lineno, funcname, message)``
    
    The implementation dispatches the actual extraction to plugins, based on the
    value of the ``method`` parameter.
    
    >>> source = '''# foo module
    ... def run(argv):
    ...    print _('Hello, world!')
    ... '''

    >>> from StringIO import StringIO
    >>> for message in extract('python', StringIO(source)):
    ...     print message
    (3, '_', 'Hello, world!')
    
    :param method: a string specifying the extraction method (.e.g. "python")
    :param fileobj: the file-like object the messages should be extracted from
    :param keywords: a list of keywords (i.e. function names) that should be
                     recognized as translation functions
    :param options: a dictionary of additional options (optional)
    :return: the list of extracted messages
    :rtype: `list`
    :raise ValueError: if the extraction method is not registered
    """
    for entry_point in working_set.iter_entry_points(GROUP_NAME, method):
        func = entry_point.load(require=True)
        return list(func(fileobj, keywords, options=options or {}))
    raise ValueError('Unknown extraction method %r' % method)

def extract_genshi(fileobj, keywords, options):
    """Extract messages from Genshi templates.
    
    :param fileobj: the file-like object the messages should be extracted from
    :param keywords: a list of keywords (i.e. function names) that should be
                     recognized as translation functions
    :param options: a dictionary of additional options (optional)
    :return: an iterator over ``(lineno, funcname, message)`` tuples
    :rtype: ``iterator``
    """
    from genshi.filters.i18n import Translator
    from genshi.template import MarkupTemplate
    tmpl = MarkupTemplate(fileobj, filename=getattr(fileobj, 'name'))
    translator = Translator(None)
    for message in translator.extract(tmpl.stream, gettext_functions=keywords):
        yield message

def extract_python(fileobj, keywords, options):
    """Extract messages from Python source code.
    
    :param fileobj: the file-like object the messages should be extracted from
    :param keywords: a list of keywords (i.e. function names) that should be
                     recognized as translation functions
    :param options: a dictionary of additional options (optional)
    :return: an iterator over ``(lineno, funcname, message)`` tuples
    :rtype: ``iterator``
    """
    funcname = None
    lineno = None
    buf = []
    messages = []
    in_args = False

    tokens = generate_tokens(fileobj.readline)
    for tok, value, (lineno, _), _, _ in tokens:
        if funcname and tok == OP and value == '(':
            in_args = True
        elif funcname and in_args:
            if tok == OP and value == ')':
                in_args = False
                if buf:
                    messages.append(''.join(buf))
                    del buf[:]
                if filter(None, messages):
                    if len(messages) > 1:
                        messages = tuple(messages)
                    else:
                        messages = messages[0]
                    yield lineno, funcname, messages
                funcname = lineno = None
                messages = []
            elif tok == STRING:
                if lineno is None:
                    lineno = stup[0]
                buf.append(value[1:-1])
            elif tok == OP and value == ',':
                messages.append(''.join(buf))
                del buf[:]
        elif funcname:
            funcname = None
        elif tok == NAME and value in keywords:
            funcname = value
