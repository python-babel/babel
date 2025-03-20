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
from babel.messages.msg_parser import process_block, parse_header_msgstr, printErrors
from babel.messages.gvar import gv  # Import the global variables class (named gv)

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
    header_msg = process_block(
        first_block,
        first_block_start,
        is_catalog_header=True,
        valid_catalog_string_list=gv.DEFAULT_CAT_STRING_LIST,
        header_separator=gv.HEADER_SEPARATOR,
    )
    if not header_msg:
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
    catalog._set_mime_headers(header_dict.items())
    catalog.fuzzy = fuzzy
    return catalog
