"""
babel.messages.catalog_parser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Parsing of gettext PO file header blocks to construct a Babel Catalog instance.
This module provides a function to parse only the header block (first block)
of a pre-split PO file and extract metadata to initialize a Catalog.

:copyright: (c) 2013-2024 by the Babel Team.
:license: BSD, see LICENSE for more details.
"""

from babel.messages import Catalog
from babel.messages.catalog import VERSION
from babel.messages.msg_parser import process_block, parse_header_msgstr, printErrors
from babel.messages.parse_utils import get_char_set

DEFAULT_CAT_STRINGS = {
    'Project-Id-Version': 'Foobar 1.0',
    'Report-Msgid-Bugs-To': 'EMAIL@ADDRESS',
    'POT-Creation-Date': '1990-04-01 15:30+0000',
    'PO-Revision-Date': 'YEAR-MO-DA HO:MI+ZONE',
    'Last-Translator': 'FULL NAME <EMAIL@ADDRESS>',
    'Language-Team': 'LANGUAGE <LL@li.org>',
    'Language': 'en',
    'Language': 'en',
    'Plural-Forms': 'nplurals=1; plural=0;',
    'MIME-Version': '1.0',
    'Content-Type': 'text/plain; charset=utf-8',
    'Content-Transfer-Encoding': '8bit',
    'Generated-By': f'Babel {VERSION}\n',
}
DEFAULT_CAT_STRING_LIST=list(DEFAULT_CAT_STRINGS.keys())
HEADER_SEPARATOR = ':'

def parse_catalog(blocks: list,
                  default_catalog: Catalog,
                  ) -> Catalog:
    """
    Parse only the first block (header) of the given pre-split PO file blocks and return a Babel Catalog instance.

    The header block is expected to have an empty msgid and a msgstr containing header metadata
    (each quoted string below msgstr is concatenated). The header msgstr is then split into key-value pairs,
    and the Catalog is constructed using those values (and default values where necessary).

    :param blocks: A list of tuples (start_line, block_text) representing the pre-split PO file.
    :param default_catalog: A default Catalog instance to be configured with header metadata.
    :return: A Catalog instance populated with header metadata.
    :raises ValueError: If no blocks are found.
    """
    if not blocks:
        raise ValueError("No blocks found in file content.")

    # Use only the first block (the header block).
    first_block_start, first_block = blocks[0]
    header_msg = process_block(first_block,
                               first_block_start,
                               is_catalog_header=True,
                               valid_catalog_string_list=DEFAULT_CAT_STRING_LIST,
                               header_separator = HEADER_SEPARATOR,
                               )
    if not header_msg:
        # print errors if any
        printErrors()
        return default_catalog

    # The header message's string (msgstr) is parsed into key-value pairs.
    header_text = header_msg.string
    header_dict = parse_header_msgstr(header_text)

    # Determine fuzzy flag (if ", fuzzy" appears anywhere in the header block).
    fuzzy = ", fuzzy" in first_block

    # Extract charset from the Content-Type header if available.
    content_type = header_dict.get("Content-Type", "")
    charset = "utf-8"
    if "charset=" in content_type:
        charset = content_type.split("charset=")[-1].strip()

    # Create and configure a Catalog instance.
    catalog = default_catalog
    # catalog._header_comment = '\n'.join(header_msg.user_comments)
    catalog._set_mime_headers(header_dict.items())
    # Set the catalog header comment using the user_comments from the header message.
    catalog.fuzzy = fuzzy
    return catalog
