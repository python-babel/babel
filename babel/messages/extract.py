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
try:
    set
except NameError:
    from sets import Set as set
import sys
from tokenize import generate_tokens, COMMENT, NAME, OP, STRING

from babel.util import pathmatch, relpath

__all__ = ['extract', 'extract_from_dir', 'extract_from_file']
__docformat__ = 'restructuredtext en'

GROUP_NAME = 'babel.extractors'

DEFAULT_KEYWORDS = {
    '_': None,
    'gettext': None,
    'ngettext': (1, 2),
    'ugettext': None,
    'ungettext': (1, 2),
    'dgettext': (2,),
    'dngettext': (2, 3),
}

DEFAULT_MAPPING = [('**.py', 'python')]

def extract_from_dir(dirname=os.getcwd(), method_map=DEFAULT_MAPPING,
                     options_map=None, keywords=DEFAULT_KEYWORDS,
                     comment_tags=(), callback=None):
    """Extract messages from any source files found in the given directory.
    
    This function generates tuples of the form:
    
        ``(filename, lineno, message, comments)``
    
    Which extraction method is used per file is determined by the `method_map`
    parameter, which maps extended glob patterns to extraction method names.
    For example, the following is the default mapping:
    
    >>> method_map = [
    ...     ('**.py', 'python')
    ... ]
    
    This basically says that files with the filename extension ".py" at any
    level inside the directory should be processed by the "python" extraction
    method. Files that don't match any of the mapping patterns are ignored. See
    the documentation of the `pathmatch` function for details on the pattern
    syntax.
    
    The following extended mapping would also use the "genshi" extraction
    method on any file in "templates" subdirectory:
    
    >>> method_map = [
    ...     ('**/templates/**.*', 'genshi'),
    ...     ('**.py', 'python')
    ... ]
    
    The dictionary provided by the optional `options_map` parameter augments
    these mappings. It uses extended glob patterns as keys, and the values are
    dictionaries mapping options names to option values (both strings).
    
    The glob patterns of the `options_map` do not necessarily need to be the
    same as those used in the method mapping. For example, while all files in
    the ``templates`` folders in an application may be Genshi applications, the
    options for those files may differ based on extension:
    
    >>> options_map = {
    ...     '**/templates/**.txt': {
    ...         'template_class': 'genshi.template:TextTemplate',
    ...         'encoding': 'latin-1'
    ...     },
    ...     '**/templates/**.html': {
    ...         'include_attrs': ''
    ...     }
    ... }
    
    :param dirname: the path to the directory to extract messages from
    :param method_map: a list of ``(pattern, method)`` tuples that maps of
                       extraction method names to extended glob patterns
    :param options_map: a dictionary of additional options (optional)
    :param keywords: a dictionary mapping keywords (i.e. names of functions
                     that should be recognized as translation functions) to
                     tuples that specify which of their arguments contain
                     localizable strings
    :param comment_tags: a list of tags of translator comments to search for
                         and include in the results
    :param callback: a function that is called for every file that message are
                     extracted from, just before the extraction itself is
                     performed; the function is passed the filename, the name
                     of the extraction method and and the options dictionary as
                     positional arguments, in that order
    :return: an iterator over ``(filename, lineno, funcname, message)`` tuples
    :rtype: ``iterator``
    :see: `pathmatch`
    """
    if options_map is None:
        options_map = {}

    absname = os.path.abspath(dirname)
    for root, dirnames, filenames in os.walk(absname):
        for subdir in dirnames:
            if subdir.startswith('.') or subdir.startswith('_'):
                dirnames.remove(subdir)
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            filename = relpath(
                os.path.join(root, filename).replace(os.sep, '/'),
                dirname
            )
            for pattern, method in method_map:
                if pathmatch(pattern, filename):
                    filepath = os.path.join(absname, filename)
                    options = {}
                    for opattern, odict in options_map.items():
                        if pathmatch(opattern, filename):
                            options = odict
                    if callback:
                        callback(filename, method, options)
                    for lineno, message, comments in \
                                  extract_from_file(method, filepath,
                                                    keywords=keywords,
                                                    comment_tags=comment_tags,
                                                    options=options):
                        yield filename, lineno, message, comments
                    break

def extract_from_file(method, filename, keywords=DEFAULT_KEYWORDS,
                      comment_tags=(), options=None):
    """Extract messages from a specific file.
    
    This function returns a list of tuples of the form:
    
        ``(lineno, funcname, message)``
    
    :param filename: the path to the file to extract messages from
    :param method: a string specifying the extraction method (.e.g. "python")
    :param keywords: a dictionary mapping keywords (i.e. names of functions
                     that should be recognized as translation functions) to
                     tuples that specify which of their arguments contain
                     localizable strings
    :param comment_tags: a list of translator tags to search for and include
                         in the results
    :param options: a dictionary of additional options (optional)
    :return: the list of extracted messages
    :rtype: `list`
    """
    fileobj = open(filename, 'U')
    try:
        return list(extract(method, fileobj, keywords, comment_tags, options))
    finally:
        fileobj.close()

def extract(method, fileobj, keywords=DEFAULT_KEYWORDS, comment_tags=(),
            options=None):
    """Extract messages from the given file-like object using the specified
    extraction method.
    
    This function returns a list of tuples of the form:
    
        ``(lineno, message, comments)``
    
    The implementation dispatches the actual extraction to plugins, based on the
    value of the ``method`` parameter.
    
    >>> source = '''# foo module
    ... def run(argv):
    ...    print _('Hello, world!')
    ... '''
    
    >>> from StringIO import StringIO
    >>> for message in extract('python', StringIO(source)):
    ...     print message
    (3, 'Hello, world!', [])
    
    :param method: a string specifying the extraction method (.e.g. "python")
    :param fileobj: the file-like object the messages should be extracted from
    :param keywords: a dictionary mapping keywords (i.e. names of functions
                     that should be recognized as translation functions) to
                     tuples that specify which of their arguments contain
                     localizable strings
    :param comment_tags: a list of translator tags to search for and include
                         in the results
    :param options: a dictionary of additional options (optional)
    :return: the list of extracted messages
    :rtype: `list`
    :raise ValueError: if the extraction method is not registered
    """
    from pkg_resources import working_set

    for entry_point in working_set.iter_entry_points(GROUP_NAME, method):
        func = entry_point.load(require=True)
        results = func(fileobj, keywords.keys(), comment_tags,
                       options=options or {})
        for lineno, funcname, messages, comments in results:
            if isinstance(messages, (list, tuple)):
                msgs = []
                for index in keywords[funcname]:
                    msgs.append(messages[index - 1])
                messages = tuple(msgs)
                if len(messages) == 1:
                    messages = messages[0]
            yield lineno, messages, comments
        return

    raise ValueError('Unknown extraction method %r' % method)

def extract_nothing(fileobj, keywords, comment_tags, options):
    """Pseudo extractor that does not actually extract anything, but simply
    returns an empty list.
    """
    return []

def extract_python(fileobj, keywords, comment_tags, options):
    """Extract messages from Python source code.
    
    :param fileobj: the file-like object the messages should be extracted from
    :param keywords: a list of keywords (i.e. function names) that should be
                     recognized as translation functions
    :param comment_tags: a list of translator tags to search for and include
                         in the results
    :param options: a dictionary of additional options (optional)
    :return: an iterator over ``(lineno, funcname, message, comments)`` tuples
    :rtype: ``iterator``
    """
    funcname = None
    lineno = None
    buf = []
    messages = []
    translator_comments = []
    in_args = False
    in_translator_comments = False

    tokens = generate_tokens(fileobj.readline)
    for tok, value, (lineno, _), _, _ in tokens:
        if funcname and tok == OP and value == '(':
            in_args = True
        elif tok == COMMENT:
            # Strip the comment token from the line
            value = value[1:].strip()
            if in_translator_comments and \
                    translator_comments[-1][0] == lineno - 1:
                # We're already inside a translator comment, continue appending
                # XXX: Should we check if the programmer keeps adding the
                # comment_tag for every comment line??? probably not!
                translator_comments.append((lineno, value))
                continue
            # If execution reaches this point, let's see if comment line
            # starts with one of the comment tags
            for comment_tag in comment_tags:
                if value.startswith(comment_tag):
                    in_translator_comments = True
                    comment = value[len(comment_tag):].strip()
                    translator_comments.append((lineno, comment))
                    break
        elif funcname and in_args:
            if tok == OP and value == ')':
                in_args = in_translator_comments = False
                if buf:
                    messages.append(''.join(buf))
                    del buf[:]
                if filter(None, messages):
                    if len(messages) > 1:
                        messages = tuple(messages)
                    else:
                        messages = messages[0]
                    # Comments don't apply unless they immediately preceed the
                    # message
                    if translator_comments and \
                            translator_comments[-1][0] < lineno - 1:
                        translator_comments = []

                    yield (lineno, funcname, messages,
                           [comment[1] for comment in translator_comments])
                funcname = lineno = None
                messages = []
                translator_comments = []
            elif tok == STRING:
                # Unwrap quotes in a safe manner
                buf.append(eval(value, {'__builtins__':{}}, {}))
            elif tok == OP and value == ',':
                messages.append(''.join(buf))
                del buf[:]
        elif funcname:
            funcname = None
        elif tok == NAME and value in keywords:
            funcname = value
