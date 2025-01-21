"""
    babel.messages.extract
    ~~~~~~~~~~~~~~~~~~~~~~

    Basic infrastructure for extracting localizable messages from source files.

    This module defines an extensible system for collecting localizable message
    strings from a variety of sources. A native extractor for Python source
    files is builtin, extractors for other sources can be added using very
    simple plugins.

    The main entry points into the extraction functionality are the functions
    `extract_from_dir` and `extract_from_file`.

    :copyright: (c) 2013-2024 by the Babel Team.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

import ast
import io
import os
import sys
import tokenize
from collections.abc import (
    Callable,
    Collection,
    Generator,
    Iterable,
    Mapping,
    MutableSequence,
)
from dataclasses import dataclass
from functools import lru_cache
from os.path import relpath
from textwrap import dedent
from tokenize import COMMENT, NAME, OP, STRING, generate_tokens
from typing import TYPE_CHECKING, Any

from babel.messages._compat import find_entrypoints
from babel.util import parse_encoding, parse_future_flags, pathmatch

if TYPE_CHECKING:
    from typing import IO, Final, Protocol

    from _typeshed import SupportsItems, SupportsRead, SupportsReadline
    from typing_extensions import TypeAlias, TypedDict

    class _PyOptions(TypedDict, total=False):
        encoding: str

    class _JSOptions(TypedDict, total=False):
        encoding: str
        jsx: bool
        template_string: bool
        parse_template_string: bool

    class _FileObj(SupportsRead[bytes], SupportsReadline[bytes], Protocol):
        def seek(self, __offset: int, __whence: int = ...) -> int: ...
        def tell(self) -> int: ...

    _SimpleKeyword: TypeAlias = tuple[int | tuple[int, int] | tuple[int, str], ...] | None
    _Keyword: TypeAlias = dict[int | None, _SimpleKeyword] | _SimpleKeyword

    # 5-tuple of (filename, lineno, messages, comments, context)
    _FileExtractionResult: TypeAlias = tuple[str, int, str | tuple[str, ...], list[str], str | None]

    # 4-tuple of (lineno, message, comments, context)
    _ExtractionResult: TypeAlias = tuple[int, str | tuple[str, ...], list[str], str | None]

    # Required arguments: fileobj, keywords, comment_tags, options
    # Return value: Iterable of (lineno, message, comments, context)
    _CallableExtractionMethod: TypeAlias = Callable[
        [_FileObj | IO[bytes], Mapping[str, _Keyword], Collection[str], Mapping[str, Any]],
        Iterable[_ExtractionResult],
    ]

    _ExtractionMethod: TypeAlias = _CallableExtractionMethod | str

GROUP_NAME: Final[str] = 'babel.extractors'

DEFAULT_KEYWORDS: dict[str, _Keyword] = {
    '_': None,
    'gettext': None,
    'ngettext': (1, 2),
    'ugettext': None,
    'ungettext': (1, 2),
    'dgettext': (2,),
    'dngettext': (2, 3),
    'N_': None,
    'pgettext': ((1, 'c'), 2),
    'npgettext': ((1, 'c'), 2, 3),
}

DEFAULT_MAPPING: list[tuple[str, str]] = [('**.py', 'python')]

# New tokens in Python 3.12, or None on older versions
FSTRING_START = getattr(tokenize, "FSTRING_START", None)
FSTRING_MIDDLE = getattr(tokenize, "FSTRING_MIDDLE", None)
FSTRING_END = getattr(tokenize, "FSTRING_END", None)


@dataclass
class FunctionStackItem:
    function_lineno: int
    function_name: str
    message_lineno: int | None
    messages: list[str | None]
    translator_comments: list[tuple[int, str]]


def _strip_comment_tags(comments: MutableSequence[str], tags: Iterable[str]):
    """Helper function for `extract` that strips comment tags from strings
    in a list of comment lines.  This functions operates in-place.
    """
    def _strip(line: str):
        for tag in tags:
            if line.startswith(tag):
                return line[len(tag):].strip()
        return line
    comments[:] = map(_strip, comments)


def default_directory_filter(dirpath: str | os.PathLike[str]) -> bool:
    subdir = os.path.basename(dirpath)
    # Legacy default behavior: ignore dot and underscore directories
    return not (subdir.startswith('.') or subdir.startswith('_'))


def extract_from_dir(
    dirname: str | os.PathLike[str] | None = None,
    method_map: Iterable[tuple[str, str]] = DEFAULT_MAPPING,
    options_map: SupportsItems[str, dict[str, Any]] | None = None,
    keywords: Mapping[str, _Keyword] = DEFAULT_KEYWORDS,
    comment_tags: Collection[str] = (),
    callback: Callable[[str, str, dict[str, Any]], object] | None = None,
    strip_comment_tags: bool = False,
    directory_filter: Callable[[str], bool] | None = None,
) -> Generator[_FileExtractionResult, None, None]:
    """Extract messages from any source files found in the given directory.

    This function generates tuples of the form ``(filename, lineno, message,
    comments, context)``.

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

    :param dirname: the path to the directory to extract messages from.  If
                    not given the current working directory is used.
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
    :param strip_comment_tags: a flag that if set to `True` causes all comment
                               tags to be removed from the collected comments.
    :param directory_filter: a callback to determine whether a directory should
                             be recursed into. Receives the full directory path;
                             should return True if the directory is valid.
    :see: `pathmatch`
    """
    if dirname is None:
        dirname = os.getcwd()
    if options_map is None:
        options_map = {}
    if directory_filter is None:
        directory_filter = default_directory_filter

    absname = os.path.abspath(dirname)
    for root, dirnames, filenames in os.walk(absname):
        dirnames[:] = [
            subdir for subdir in dirnames
            if directory_filter(os.path.join(root, subdir))
        ]
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            filepath = os.path.join(root, filename).replace(os.sep, '/')

            yield from check_and_call_extract_file(
                filepath,
                method_map,
                options_map,
                callback,
                keywords,
                comment_tags,
                strip_comment_tags,
                dirpath=absname,
            )


def check_and_call_extract_file(
    filepath: str | os.PathLike[str],
    method_map: Iterable[tuple[str, str]],
    options_map: SupportsItems[str, dict[str, Any]],
    callback: Callable[[str, str, dict[str, Any]], object] | None,
    keywords: Mapping[str, _Keyword],
    comment_tags: Collection[str],
    strip_comment_tags: bool,
    dirpath: str | os.PathLike[str] | None = None,
) -> Generator[_FileExtractionResult, None, None]:
    """Checks if the given file matches an extraction method mapping, and if so, calls extract_from_file.

    Note that the extraction method mappings are based relative to dirpath.
    So, given an absolute path to a file `filepath`, we want to check using
    just the relative path from `dirpath` to `filepath`.

    Yields 5-tuples (filename, lineno, messages, comments, context).

    :param filepath: An absolute path to a file that exists.
    :param method_map: a list of ``(pattern, method)`` tuples that maps of
                       extraction method names to extended glob patterns
    :param options_map: a dictionary of additional options (optional)
    :param callback: a function that is called for every file that message are
                     extracted from, just before the extraction itself is
                     performed; the function is passed the filename, the name
                     of the extraction method and and the options dictionary as
                     positional arguments, in that order
    :param keywords: a dictionary mapping keywords (i.e. names of functions
                     that should be recognized as translation functions) to
                     tuples that specify which of their arguments contain
                     localizable strings
    :param comment_tags: a list of tags of translator comments to search for
                         and include in the results
    :param strip_comment_tags: a flag that if set to `True` causes all comment
                               tags to be removed from the collected comments.
    :param dirpath: the path to the directory to extract messages from.
    :return: iterable of 5-tuples (filename, lineno, messages, comments, context)
    :rtype: Iterable[tuple[str, int, str|tuple[str], list[str], str|None]
    """
    # filename is the relative path from dirpath to the actual file
    filename = relpath(filepath, dirpath)

    for pattern, method in method_map:
        if not pathmatch(pattern, filename):
            continue

        options = {}
        for opattern, odict in options_map.items():
            if pathmatch(opattern, filename):
                options = odict
                break
        if callback:
            callback(filename, method, options)
        for message_tuple in extract_from_file(
            method, filepath,
            keywords=keywords,
            comment_tags=comment_tags,
            options=options,
            strip_comment_tags=strip_comment_tags,
        ):
            yield (filename, *message_tuple)

        break


def extract_from_file(
    method: _ExtractionMethod,
    filename: str | os.PathLike[str],
    keywords: Mapping[str, _Keyword] = DEFAULT_KEYWORDS,
    comment_tags: Collection[str] = (),
    options: Mapping[str, Any] | None = None,
    strip_comment_tags: bool = False,
) -> list[_ExtractionResult]:
    """Extract messages from a specific file.

    This function returns a list of tuples of the form ``(lineno, message, comments, context)``.

    :param filename: the path to the file to extract messages from
    :param method: a string specifying the extraction method (.e.g. "python")
    :param keywords: a dictionary mapping keywords (i.e. names of functions
                     that should be recognized as translation functions) to
                     tuples that specify which of their arguments contain
                     localizable strings
    :param comment_tags: a list of translator tags to search for and include
                         in the results
    :param strip_comment_tags: a flag that if set to `True` causes all comment
                               tags to be removed from the collected comments.
    :param options: a dictionary of additional options (optional)
    :returns: list of tuples of the form ``(lineno, message, comments, context)``
    :rtype: list[tuple[int, str|tuple[str], list[str], str|None]
    """
    if method == 'ignore':
        return []

    with open(filename, 'rb') as fileobj:
        return list(extract(method, fileobj, keywords, comment_tags,
                            options, strip_comment_tags))


def _match_messages_against_spec(
    lineno: int,
    messages: list[str | None],
    comments: list[str],
    fileobj: _FileObj,
    spec: tuple[int | tuple[int, str], ...],
):
    translatable = []
    context = None

    # last_index is 1 based like the keyword spec
    last_index = len(messages)
    for index in spec:
        if isinstance(index, tuple):  # (n, 'c')
            context = messages[index[0] - 1]
            continue
        if last_index < index:
            # Not enough arguments
            return
        message = messages[index - 1]
        if message is None:
            return
        translatable.append(message)

    # keyword spec indexes are 1 based, therefore '-1'
    if isinstance(spec[0], tuple):
        # context-aware *gettext method
        first_msg_index = spec[1] - 1
    else:
        first_msg_index = spec[0] - 1
    # An empty string msgid isn't valid, emit a warning
    if not messages[first_msg_index]:
        filename = (getattr(fileobj, "name", None) or "(unknown)")
        sys.stderr.write(
            f"{filename}:{lineno}: warning: Empty msgid.  It is reserved by GNU gettext: gettext(\"\") "
            f"returns the header entry with meta information, not the empty string.\n",
        )
        return

    translatable = tuple(translatable)
    if len(translatable) == 1:
        translatable = translatable[0]

    return lineno, translatable, comments, context


@lru_cache(maxsize=None)
def _find_extractor(name: str):
    for ep_name, load in find_entrypoints(GROUP_NAME):
        if ep_name == name:
            return load()
    return None


def extract(
    method: _ExtractionMethod,
    fileobj: _FileObj,
    keywords: Mapping[str, _Keyword] = DEFAULT_KEYWORDS,
    comment_tags: Collection[str] = (),
    options: Mapping[str, Any] | None = None,
    strip_comment_tags: bool = False,
) -> Generator[_ExtractionResult, None, None]:
    """Extract messages from the given file-like object using the specified
    extraction method.

    This function returns tuples of the form ``(lineno, message, comments, context)``.

    The implementation dispatches the actual extraction to plugins, based on the
    value of the ``method`` parameter.

    >>> source = b'''# foo module
    ... def run(argv):
    ...    print(_('Hello, world!'))
    ... '''

    >>> from io import BytesIO
    >>> for message in extract('python', BytesIO(source)):
    ...     print(message)
    (3, u'Hello, world!', [], None)

    :param method: an extraction method (a callable), or
                   a string specifying the extraction method (.e.g. "python");
                   if this is a simple name, the extraction function will be
                   looked up by entry point; if it is an explicit reference
                   to a function (of the form ``package.module:funcname`` or
                   ``package.module.funcname``), the corresponding function
                   will be imported and used
    :param fileobj: the file-like object the messages should be extracted from
    :param keywords: a dictionary mapping keywords (i.e. names of functions
                     that should be recognized as translation functions) to
                     tuples that specify which of their arguments contain
                     localizable strings
    :param comment_tags: a list of translator tags to search for and include
                         in the results
    :param options: a dictionary of additional options (optional)
    :param strip_comment_tags: a flag that if set to `True` causes all comment
                               tags to be removed from the collected comments.
    :raise ValueError: if the extraction method is not registered
    :returns: iterable of tuples of the form ``(lineno, message, comments, context)``
    :rtype: Iterable[tuple[int, str|tuple[str], list[str], str|None]
    """
    if callable(method):
        func = method
    elif ':' in method or '.' in method:
        if ':' not in method:
            lastdot = method.rfind('.')
            module, attrname = method[:lastdot], method[lastdot + 1:]
        else:
            module, attrname = method.split(':', 1)
        func = getattr(__import__(module, {}, {}, [attrname]), attrname)
    else:
        func = _find_extractor(method)
        if func is None:
            # if no named entry point was found,
            # we resort to looking up a builtin extractor
            func = _BUILTIN_EXTRACTORS.get(method)

    if func is None:
        raise ValueError(f"Unknown extraction method {method!r}")

    results = func(fileobj, keywords.keys(), comment_tags,
                   options=options or {})

    for lineno, funcname, messages, comments in results:
        if not isinstance(messages, (list, tuple)):
            messages = [messages]
        if not messages:
            continue

        specs = keywords[funcname] or None if funcname else None
        # {None: x} may be collapsed into x for backwards compatibility.
        if not isinstance(specs, dict):
            specs = {None: specs}

        if strip_comment_tags:
            _strip_comment_tags(comments, comment_tags)

        # None matches all arities.
        for arity in (None, len(messages)):
            try:
                spec = specs[arity]
            except KeyError:
                continue
            if spec is None:
                spec = (1,)
            result = _match_messages_against_spec(lineno, messages, comments, fileobj, spec)
            if result is not None:
                yield result


def extract_nothing(
    fileobj: _FileObj,
    keywords: Mapping[str, _Keyword],
    comment_tags: Collection[str],
    options: Mapping[str, Any],
) -> list[_ExtractionResult]:
    """Pseudo extractor that does not actually extract anything, but simply
    returns an empty list.
    """
    return []


def extract_python(
    fileobj: IO[bytes],
    keywords: Mapping[str, _Keyword],
    comment_tags: Collection[str],
    options: _PyOptions,
) -> Generator[_ExtractionResult, None, None]:
    """Extract messages from Python source code.

    It returns an iterator yielding tuples in the following form ``(lineno,
    funcname, message, comments)``.

    :param fileobj: the seekable, file-like object the messages should be
                    extracted from
    :param keywords: a list of keywords (i.e. function names) that should be
                     recognized as translation functions
    :param comment_tags: a list of translator tags to search for and include
                         in the results
    :param options: a dictionary of additional options (optional)
    :rtype: ``iterator``
    """
    encoding = parse_encoding(fileobj) or options.get('encoding', 'UTF-8')
    future_flags = parse_future_flags(fileobj, encoding)
    next_line = lambda: fileobj.readline().decode(encoding)

    tokens = generate_tokens(next_line)

    # Current prefix of a Python 3.12 (PEP 701) f-string, or None if we're not
    # currently parsing one.
    current_fstring_start = None

    # Keep the stack of all function calls and its related contextual variables,
    # so we can handle nested gettext calls.
    function_stack: list[FunctionStackItem] = []
    # Keep the last encountered function/variable name for when we encounter
    # an opening parenthesis
    last_name = None
    # Keep track of whether we're in a class or function definition
    in_def = False
    # Keep track of whether we're in a block of translator comments
    in_translator_comments = False
    # Keep track of the last encountered translator comments
    translator_comments = []
    # Keep track of the (split) strings encountered
    message_buffer = []

    for tok, value, (lineno, _), _, _ in tokens:
        if tok == NAME and value in ('def', 'class'):
            # We're entering a class or function definition
            in_def = True
            continue

        elif in_def and tok == OP and value in ('(', ':'):
            # We're in a class or function definition and should not do anything
            in_def = False
            continue

        elif tok == OP and value == '(' and last_name:
            # We're entering a function call
            cur_translator_comments = translator_comments
            if function_stack and function_stack[-1].function_lineno == lineno:
                # If our current function call is on the same line as the previous one,
                # copy their translator comments, since they also apply to us.
                cur_translator_comments = function_stack[-1].translator_comments

            # We add all information needed later for the current function call
            function_stack.append(FunctionStackItem(
                function_lineno=lineno,
                function_name=last_name,
                message_lineno=None,
                messages=[],
                translator_comments=cur_translator_comments,
            ))
            translator_comments = []
            message_buffer.clear()

        elif tok == COMMENT:
            # Strip the comment token from the line
            value = value[1:].strip()
            if in_translator_comments and translator_comments[-1][0] == lineno - 1:
                # We're already inside a translator comment, continue appending
                translator_comments.append((lineno, value))
                continue

            for comment_tag in comment_tags:
                if value.startswith(comment_tag):
                    # Comment starts with one of the comment tags,
                    # so let's start capturing it
                    in_translator_comments = True
                    translator_comments.append((lineno, value))
                    break

        elif function_stack and function_stack[-1].function_name in keywords:
            # We're inside a translation function call
            if tok == OP and value == ')':
                # The call has ended, so we yield the translatable term(s)
                messages = function_stack[-1].messages
                lineno = (
                    function_stack[-1].message_lineno
                    or function_stack[-1].function_lineno
                )
                cur_translator_comments = function_stack[-1].translator_comments

                if message_buffer:
                    messages.append(''.join(message_buffer))
                    message_buffer.clear()
                else:
                    messages.append(None)

                messages = tuple(messages) if len(messages) > 1 else messages[0]
                if (
                    cur_translator_comments
                    and cur_translator_comments[-1][0] < lineno - 1
                ):
                    # The translator comments are not immediately preceding the current
                    # term, so we skip them.
                    cur_translator_comments = []

                yield (
                    lineno,
                    function_stack[-1].function_name,
                    messages,
                    [comment[1] for comment in cur_translator_comments],
                )

                function_stack.pop()

            elif tok == STRING:
                # We've encountered a string inside a translation function call
                string_value = _parse_python_string(value, encoding, future_flags)
                if not function_stack[-1].message_lineno:
                    function_stack[-1].message_lineno = lineno
                if string_value is not None:
                    message_buffer.append(string_value)

            # Python 3.12+, see https://peps.python.org/pep-0701/#new-tokens
            elif tok == FSTRING_START:
                current_fstring_start = value
            elif tok == FSTRING_MIDDLE:
                if current_fstring_start is not None:
                    current_fstring_start += value
            elif tok == FSTRING_END:
                if current_fstring_start is not None:
                    fstring = current_fstring_start + value
                    string_value = _parse_python_string(fstring, encoding, future_flags)
                    if string_value is not None:
                        message_buffer.append(string_value)

            elif tok == OP and value == ',':
                # End of a function call argument
                if message_buffer:
                    function_stack[-1].messages.append(''.join(message_buffer))
                    message_buffer.clear()
                else:
                    function_stack[-1].messages.append(None)

        elif function_stack and tok == OP and value == ')':
            function_stack.pop()

        if in_translator_comments and translator_comments[-1][0] < lineno:
            # We have a newline in between the comments, so they don't belong
            # together anymore
            in_translator_comments = False

        if tok == NAME:
            last_name = value
            if function_stack and not function_stack[-1].message_lineno:
                function_stack[-1].message_lineno = lineno

        if (
            current_fstring_start is not None
            and tok not in {FSTRING_START, FSTRING_MIDDLE}
        ):
            # In Python 3.12, tokens other than FSTRING_* mean the
            # f-string is dynamic, so we don't wan't to extract it.
            # And if it's FSTRING_END, we've already handled it above.
            # Let's forget that we're in an f-string.
            current_fstring_start = None


def _parse_python_string(value: str, encoding: str, future_flags: int) -> str | None:
    # Unwrap quotes in a safe manner, maintaining the string's encoding
    # https://sourceforge.net/tracker/?func=detail&atid=355470&aid=617979&group_id=5470
    code = compile(
        f'# coding={str(encoding)}\n{value}',
        '<string>',
        'eval',
        ast.PyCF_ONLY_AST | future_flags,
    )
    if isinstance(code, ast.Expression):
        body = code.body
        if isinstance(body, ast.Constant):
            return body.value
        if isinstance(body, ast.JoinedStr):  # f-string
            if all(isinstance(node, ast.Constant) for node in body.values):
                return ''.join(node.value for node in body.values)
            # TODO: we could raise an error or warning when not all nodes are constants
    return None


def extract_javascript(
    fileobj: _FileObj,
    keywords: Mapping[str, _Keyword],
    comment_tags: Collection[str],
    options: _JSOptions,
    lineno: int = 1,
) -> Generator[_ExtractionResult, None, None]:
    """Extract messages from JavaScript source code.

    :param fileobj: the seekable, file-like object the messages should be
                    extracted from
    :param keywords: a list of keywords (i.e. function names) that should be
                     recognized as translation functions
    :param comment_tags: a list of translator tags to search for and include
                         in the results
    :param options: a dictionary of additional options (optional)
                    Supported options are:
                    * `jsx` -- set to false to disable JSX/E4X support.
                    * `template_string` -- if `True`, supports gettext(`key`)
                    * `parse_template_string` -- if `True` will parse the
                                                 contents of javascript
                                                 template strings.
    :param lineno: line number offset (for parsing embedded fragments)
    """
    from babel.messages.jslexer import Token, tokenize, unquote_string

    encoding = options.get('encoding', 'utf-8')
    dotted = any('.' in kw for kw in keywords)
    last_token = None
    # Keep the stack of all function calls and its related contextual variables,
    # so we can handle nested gettext calls.
    function_stack: list[FunctionStackItem] = []
    # Keep track of whether we're in a class or function definition
    in_def = False
    # Keep track of whether we're in a block of translator comments
    in_translator_comments = False
    # Keep track of the last encountered translator comments
    translator_comments = []
    # Keep track of the (split) strings encountered
    message_buffer = []

    for token in tokenize(
        fileobj.read().decode(encoding),
        jsx=options.get("jsx", True),
        template_string=options.get("template_string", True),
        dotted=dotted,
        lineno=lineno,
    ):
        if token.type == 'name' and token.value in ('class', 'function'):
            # We're entering a class or function definition
            in_def = True

        elif in_def and token.type == 'operator' and token.value in ('(', '{'):
            # We're in a class or function definition and should not do anything
            in_def = False
            continue

        elif (
            last_token
            and last_token.type == 'name'
            and last_token.value in keywords
            and token.type == 'template_string'
        ):
            # Turn keyword`foo` expressions into keyword("foo") function calls
            string_value = unquote_string(token.value)
            cur_translator_comments = translator_comments
            if function_stack and function_stack[-1].function_lineno == last_token.lineno:
                # If our current function call is on the same line as the previous one,
                # copy their translator comments, since they also apply to us.
                cur_translator_comments = function_stack[-1].translator_comments

            # We add all information needed later for the current function call
            function_stack.append(FunctionStackItem(
                function_lineno=last_token.lineno,
                function_name=last_token.value,
                message_lineno=token.lineno,
                messages=[string_value],
                translator_comments=cur_translator_comments,
            ))
            translator_comments = []

            # We act as if we are closing the function call now
            token = Token('operator', ')', token.lineno)

        if (
            options.get('parse_template_string')
            and (not last_token or last_token.type != 'name' or last_token.value not in keywords)
            and token.type == 'template_string'
        ):
            yield from parse_template_string(token.value, keywords, comment_tags, options, token.lineno)

        elif token.type == 'operator' and token.value == '(':
            if last_token.type == 'name':
                # We're entering a function call
                cur_translator_comments = translator_comments
                if function_stack and function_stack[-1].function_lineno == token.lineno:
                    # If our current function call is on the same line as the previous one,
                    # copy their translator comments, since they also apply to us.
                    cur_translator_comments = function_stack[-1].translator_comments

                # We add all information needed later for the current function call
                function_stack.append(FunctionStackItem(
                    function_lineno=token.lineno,
                    function_name=last_token.value,
                    message_lineno=None,
                    messages=[],
                    translator_comments=cur_translator_comments,
                ))
                translator_comments = []

        elif token.type == 'linecomment':
            # Strip the comment token from the line
            value = token.value[2:].strip()
            if in_translator_comments and translator_comments[-1][0] == token.lineno - 1:
                # We're already inside a translator comment, continue appending
                translator_comments.append((token.lineno, value))
                continue

            for comment_tag in comment_tags:
                if value.startswith(comment_tag):
                    # Comment starts with one of the comment tags,
                    # so let's start capturing it
                    in_translator_comments = True
                    translator_comments.append((token.lineno, value))
                    break

        elif token.type == 'multilinecomment':
            # Only one multi-line comment may precede a translation
            translator_comments = []
            value = token.value[2:-2].strip()
            for comment_tag in comment_tags:
                if value.startswith(comment_tag):
                    lines = value.splitlines()
                    if lines:
                        lines[0] = lines[0].strip()
                        lines[1:] = dedent('\n'.join(lines[1:])).splitlines()
                        for offset, line in enumerate(lines):
                            translator_comments.append((token.lineno + offset, line))
                    break

        elif function_stack and function_stack[-1].function_name in keywords:
            # We're inside a translation function call
            if token.type == 'operator' and token.value == ')':
                # The call has ended, so we yield the translatable term(s)
                messages = function_stack[-1].messages
                lineno = (
                    function_stack[-1].message_lineno
                    or function_stack[-1].function_lineno
                )
                cur_translator_comments = function_stack[-1].translator_comments

                if message_buffer:
                    messages.append(''.join(message_buffer))
                    message_buffer.clear()
                else:
                    messages.append(None)

                messages = tuple(messages) if len(messages) > 1 else messages[0]
                if (
                    cur_translator_comments
                    and cur_translator_comments[-1][0] < lineno - 1
                ):
                    # The translator comments are not immediately preceding the current
                    # term, so we skip them.
                    cur_translator_comments = []

                yield (
                    lineno,
                    function_stack[-1].function_name,
                    messages,
                    [comment[1] for comment in cur_translator_comments],
                )

                function_stack.pop()

            elif token.type in ('string', 'template_string'):
                # We've encountered a string inside a translation function call
                string_value = unquote_string(token.value)
                if not function_stack[-1].message_lineno:
                    function_stack[-1].message_lineno = token.lineno
                if string_value is not None:
                    message_buffer.append(string_value)

            elif token.type == 'operator' and token.value == ',':
                # End of a function call argument
                if message_buffer:
                    function_stack[-1].messages.append(''.join(message_buffer))
                    message_buffer.clear()
                else:
                    function_stack[-1].messages.append(None)

        elif function_stack and token.type == 'operator' and token.value == ')':
            function_stack.pop()

        if in_translator_comments and translator_comments[-1][0] < token.lineno:
            # We have a newline in between the comments, so they don't belong
            # together anymore
            in_translator_comments = False

        last_token = token


def parse_template_string(
    template_string: str,
    keywords: Mapping[str, _Keyword],
    comment_tags: Collection[str],
    options: _JSOptions,
    lineno: int = 1,
) -> Generator[_ExtractionResult, None, None]:
    """Parse JavaScript template string.

    :param template_string: the template string to be parsed
    :param keywords: a list of keywords (i.e. function names) that should be
                     recognized as translation functions
    :param comment_tags: a list of translator tags to search for and include
                         in the results
    :param options: a dictionary of additional options (optional)
    :param lineno: starting line number (optional)
    """
    from babel.messages.jslexer import line_re
    prev_character = None
    level = 0
    inside_str = False
    expression_contents = ''
    for character in template_string[1:-1]:
        if not inside_str and character in ('"', "'", '`'):
            inside_str = character
        elif inside_str == character and prev_character != r'\\':
            inside_str = False
        if level:
            expression_contents += character
        if not inside_str:
            if character == '{' and prev_character == '$':
                level += 1
            elif level and character == '}':
                level -= 1
                if level == 0 and expression_contents:
                    expression_contents = expression_contents[0:-1]
                    fake_file_obj = io.BytesIO(expression_contents.encode())
                    yield from extract_javascript(fake_file_obj, keywords, comment_tags, options, lineno)
                    lineno += len(line_re.findall(expression_contents))
                    expression_contents = ''
        prev_character = character


_BUILTIN_EXTRACTORS = {
    'ignore': extract_nothing,
    'python': extract_python,
    'javascript': extract_javascript,
}
