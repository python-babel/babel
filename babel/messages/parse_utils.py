"""
babel.messages.parse_utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utility functions for parsing PO file data, including charset detection and conversion
of keyword arguments to various types.

:copyright: (c) 2025 by the Babel Team.
:license: BSD, see LICENSE for more details.
"""

import re


# ------------------------------------------------------------------------------
# Global Variables and Utility Constants
# ------------------------------------------------------------------------------

#: Regular expression pattern to match Python format specifiers in messages.
PYTHON_FORMAT = re.compile(
    r'''
    \%
        (?:\(([\w]*)\))?                # Optional mapping key in parentheses
        ([-#0\ +]?(?:\*|[\d]+)?         # Optional flags and width specifier
         (?:\.(?:\*|[\d]+))?[hlL]?)       # Optional precision and length modifier
        ((?<!\s)[diouxXeEfFgGcrs%])       # Type specifier
        (?=([\s\'\)\.\,\:\"\!\]\>\?]|$))  # Lookahead for separator or end-of-string
    ''',
    re.VERBOSE
)


WORD_SEP = re.compile('('
                      r'\s+|'                                 # any whitespace
                      r'[^\s\w]*\w+[a-zA-Z]-(?=\w+[a-zA-Z])|'  # hyphenated words
                      r'(?<=[\w\!\"\'\&\.\,\?])-{2,}(?=\w)'   # em-dash
                      ')')

# Compile a regular expression pattern to match a "Content-Type" header with a charset specification.
# The pattern looks for lines like:
#   Content-Type: text/html; charset=UTF-8
# and captures the charset value.
CONTENT_TYPE_CHARSET_PATTERN = re.compile(b"Content-Type: [^;]+; charset=([^\r\n]+)")
true_set = {"true", "1", "yes", "y", "t", "on"}
# false_set = {"false", "0", "no", "n", "f", "off"}

# Precompute the translation table once for efficiency.
_ESCAPE_TABLE = str.maketrans({
    '\\': '\\\\',
    '\t': '\\t',
    '\r': '\\r',
    '\n': '\\n',
    '"': '\\"',
})

# Precompile the regex pattern and create a replacement mapping.
_UNESCAPE_PATTERN = re.compile(r'\\([\\trn"])')
_UNESCAPE_MAP = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"'}

def unescape(string: str) -> str:
    r"""Reverse escape the given string.

    >>> print(unescape('"Say:\\n  \\"hello, world!\\"\\n"'))
    Say:
      "hello, world!"
    <BLANKLINE>

    :param string: the string to unescape (expected to be wrapped in quotes)
    """
    # Assumes the string starts and ends with a double-quote.
    return _UNESCAPE_PATTERN.sub(lambda m: _UNESCAPE_MAP[m.group(1)], string[1:-1])

def denormalize(string: str) -> str:
    r"""Reverse the normalization done by the `normalize` function.

    >>> print(denormalize(r'''""
    ... "Say:\n"
    ... "  \"hello, world!\"\n"'''))
    Say:
      "hello, world!"
    <BLANKLINE>

    >>> print(denormalize(r'''""
    ... "Say:\n"
    ... "  \"Lorem ipsum dolor sit "
    ... "amet, consectetur adipisicing"
    ... " elit, \"\n"'''))
    Say:
      "Lorem ipsum dolor sit amet, consectetur adipisicing elit, "
    <BLANKLINE>

    :param string: the string to denormalize
    """
    # If the string contains newline characters, process line by line.
    if '\n' in string:
        lines = string.splitlines()
        if lines and lines[0] == '""':
            lines = lines[1:]
        return ''.join(unescape(line) for line in lines)
    else:
        return unescape(string)
    
def escape(string: str, is_quoted = True) -> str:
    r"""Escape the given string so that it can be included in double-quoted
    strings in ``PO`` files.

    >>> escape('''Say:
    ...   "hello, world!"
    ... ''')
    '"Say:\\n  \\"hello, world!\\"\\n"'

    :param string: the string to escape
    """
    esp_string = string.translate(_ESCAPE_TABLE)
    return f'"{esp_string}"' if is_quoted else esp_string

def normalize(string: str, prefix: str = '', width: int = 76, is_quoted: bool = True) -> str:
    """
    Convert a string into a format appropriate for .po files.

    If the resulting escaped line (plus a prefix) exceeds the given width,
    the line is split using the WORD_SEP regex and reassembled so that no line is too long.

    Args:
        string (str): The input string to normalize.
        prefix (str): A string to prepend to every output line.
        width (int): The maximum line width. Use None, 0, or a negative number to disable wrapping.
        is_quoted (bool): Whether the output should be wrapped in quotes.

    Returns:
        str: A string containing the normalized, escaped output.
    """
    # If wrapping is disabled, simply split the string into lines.
    if not (width and width > 0):
        lines = string.splitlines(True)
    else:
        prefix_len = len(prefix)
        lines = []
        for line in string.splitlines(True):
            escaped_line = escape(line, is_quoted=is_quoted)
            if len(escaped_line) + prefix_len > width:
                # Wrap the line by splitting into chunks.
                chunks = WORD_SEP.split(line)
                # Reverse chunks for efficient pop() from the end.
                chunks.reverse()
                # Precompute escapes for each chunk.
                chunk_escapes = [escape(chunk, is_quoted=is_quoted) for chunk in chunks]
                wrapped = []
                while chunks:
                    buf = []
                    # Start with a base size of 2 to account for the surrounding quotes in escaped output.
                    current_size = 2
                    while chunks:
                        current_chunk_esc = chunk_escapes[-1]
                        # Calculate effective length: remove 2 from the escaped length and add prefix length.
                        effective_length = len(current_chunk_esc) - 2 + prefix_len
                        if current_size + effective_length < width:
                            buf.append(chunks.pop())
                            chunk_escapes.pop()
                            current_size += effective_length
                        else:
                            if not buf:
                                # Force one chunk on its own line if none fits.
                                buf.append(chunks.pop())
                                chunk_escapes.pop()
                            break
                    wrapped.append(''.join(buf))
                lines.extend(wrapped)
            else:
                lines.append(line)

    # If only one line results, return the fully escaped string.
    if len(lines) <= 1:
        return escape(string, is_quoted=is_quoted)

    # Remove trailing empty line if present, ensuring the final non-empty line ends with a newline.
    if lines and not lines[-1]:
        lines.pop()
        if lines:
            lines[-1] += '\n'

    # Prepend each line with the prefix and escape it; then add the header "" line.
    return '""\n' + "\n".join(prefix + escape(line, is_quoted=is_quoted) for line in lines)


def get_char_set(filename: str) -> str:
    """
    Open a file in binary mode, search its content for a Content-Type header that specifies the charset,
    and return the corresponding encoding. If no charset is found, it defaults to 'utf-8'.

    Parameters:
        filename (str): The path to the file to be read.

    Returns:
        str: The charset found in the file or 'utf-8' if not present.

    Workflow:
      1. Open the file in binary mode to correctly handle non-UTF8 encoded files.
      2. Read the entire file content.
      3. Search for the Content-Type header using the precompiled regex pattern.
      4. If found, decode the captured charset value from ASCII (replacing errors) and strip
         any extraneous newline characters or quotes.
      5. If not found, return 'utf-8' as the default encoding.
    """
    with open(filename, "rb") as f:
        content = f.read()
    m = re.search(CONTENT_TYPE_CHARSET_PATTERN, content)
    if m:
        # Decode the captured charset value using ASCII decoding.
        match_part = m.group(1).decode("ascii", errors="replace")
        # Strip potential newline and quote characters from the decoded string.
        char_code = match_part.strip('\\n"').strip()
        return char_code
    else:
        return "utf-8"
