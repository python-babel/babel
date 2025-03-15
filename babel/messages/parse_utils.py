"""
babel.messages.parse_utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utility functions for parsing PO file data, including charset detection and conversion
of keyword arguments to various types.

:copyright: (c) 2025 by the Babel Team.
:license: BSD, see LICENSE for more details.
"""

import re

# Compile a regular expression pattern to match a "Content-Type" header with a charset specification.
# The pattern looks for lines like:
#   Content-Type: text/html; charset=UTF-8
# and captures the charset value.
CONTENT_TYPE_CHARSET_PATTERN = re.compile(b"Content-Type: [^;]+; charset=([^\r\n]+)")
true_set = {"true", "1", "yes", "y", "t", "on"}
# false_set = {"false", "0", "no", "n", "f", "off"}

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
    return "utf-8"


def get_int_kwarg(kwargs, keys, default=0):
    """
    Extract an integer value from a dictionary of keyword arguments using a list of possible keys.

    Parameters:
        kwargs (dict): A dictionary containing keyword arguments.
        keys (iterable): An iterable of keys to look for in the dictionary.
        default (int, optional): The value to return if none of the keys are found. Defaults to 0.

    Returns:
        int: The integer value corresponding to the first key found in the kwargs.

    Raises:
        ValueError: If the value found cannot be converted to an integer.

    Workflow:
      1. Iterate over the provided keys.
      2. For the first key present in kwargs, attempt to convert its value to an integer.
      3. If conversion fails, raise a ValueError with an informative message.
      4. If no key is found, return the default value.
    """
    for key in keys:
        val = kwargs.get(key)
        if val is not None:
            try:
                return int(val)
            except ValueError as e:
                raise ValueError(f"Invalid integer value for {key}: {val}") from e
    return default


def get_boolean_kwarg(kwargs, keys: list, default=False):
    """
    Extract a boolean value from a kwargs dictionary using a list of keys.

    This function iterates over the specified keys and retrieves the corresponding
    value from the kwargs dictionary. It then converts the value to lowercase and checks
    if it belongs to a predefined set of truthy strings (e.g., {"true", "1", "yes", "y", "t", "on"}).
    If any key's value is found in this truth set, the function returns True.
    Otherwise, if no key is found or if an error occurs during processing, the function
    returns the specified default value.

    Parameters:
        kwargs (dict): The dictionary containing keyword arguments.
        keys (list): A list of keys to search for in the dictionary.
        default (bool, optional): The value to return if none of the keys are found or
                                  if an error occurs. Defaults to False.

    Returns:
        bool: True if any key's value (after conversion to lowercase) is in the truth set;
              otherwise, returns the default value.

    Conversion Logic:
      - For each key in the provided list, attempt to retrieve its value from kwargs.
      - If the value exists and is a string, strip leading/trailing whitespace and convert
        it to lowercase.
      - Check whether the resulting string is in a predefined set of truthy strings.
      - If any such value is found, return True.
      - If none match or an error occurs (for example, if the value does not support the
        lower() method), return the default value.

    Example:
        >>> kwargs = {'is_debug': 'false', 'verbose': 'yes'}
        >>> get_boolean_kwarg(kwargs, ['is_debug', 'debug'])
        False
        >>> get_boolean_kwarg(kwargs, ['verbose', 'log'])
        True
        >>> get_boolean_kwarg(kwargs, ['not_found'], default=True)
        True
    """
    try:
        val_list = [kwargs.get(k) for k in keys]
        # Check if any non-empty value, after being lowercased, is in the truth set.
        val = any([True for v in val_list if (v and v.lower() in true_set)])
        return val
    except Exception:
        return default


def get_str_kwargs(kwargs, keys, default=None):
    """
    Extract a string value from a kwargs dictionary using a list of possible keys.

    Parameters:
        kwargs (dict): A dictionary containing keyword arguments.
        keys (iterable): An iterable of keys to search for in the dictionary.
        default: The default value to return if none of the keys are found or if the value is None.

    Returns:
        str: The string representation of the value corresponding to the first found key,
             or the default if no key is found.

    Note:
        The function converts the value to a string using the built-in str() function.

    Example:
        >>> kwargs = {'name': 'Alice', 'username': None}
        >>> get_str_kwargs(kwargs, ['username', 'name'], default='Unknown')
        'Alice'
    """
    for key in keys:
        if key in kwargs and kwargs[key] is not None:
            return str(kwargs[key])
    return default
