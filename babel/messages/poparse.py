"""
babel.messages.poparse
~~~~~~~~~~~~~~~~~~~~~

Reading and writing of files in the ``gettext`` PO (portable object)
format.

:copyright: (c) 2025 by the Babel Team.
:license: BSD, see LICENSE for more details.
"""

import argparse
import os
import re
import sys
from local_logging import benchmark
from sphinx_intl import catalog as c
from babel import __version__ as VERSION
import locale
from babel.messages import Catalog
from babel.messages.catalog_parser import parse_catalog, printErrors
from babel.messages.block_utils import split_into_blocks
from babel.messages.parse_utils import get_char_set

import babel.messages.msg_parser as ps


machine_language, machine_encoding = locale.getdefaultlocale()

def load_po(filename: str,
            debug: bool = False,
            multiprocessing: bool = False,
            hookexcept: bool = False,
            batch_size_division: int = 2,
            ignore_obsolete: bool = False,
            abort_invalid: bool = True,
            version=VERSION,
            locale=machine_language,
            charset=machine_encoding,
            domain: str = 'message',
            ):
    """
    Load and parse a PO (Portable Object) file into a Babel Catalog object.

    The function performs the following steps:
      1. Creates a default catalog using the provided locale, domain, charset, and version.
      2. Determines the charset of the PO file via the get_char_set function.
      3. Opens and decodes the file content using the detected charset.
      4. Splits the file content into blocks for parsing.
      5. Initializes the message parser with the pre-split blocks and the specified configuration options.
      6. Parses the catalog header from the blocks.
      7. Sets the catalog version to the provided generator version if it is not already set.
      8. Assigns the catalog to the parser’s global state.
      9. Parses the individual messages and classifies obsolete messages separately.
     10. Prints any encountered parsing errors to stderr.
     11. Returns the populated Catalog object.

    Parameters:
        filename (str): Path to the PO file to be loaded.
        debug (bool, optional): Enable debug mode. Defaults to False.
        multiprocessing (bool, optional): Enable multiprocessing support. Dividing message blocks into batches and run each batch in CPU cores concurrently. Defaults to False.
        hookexcept (bool, optional): Enable hook exception handling to print out frame stacks or not. Defaults to False.
        batch_size_division (int, optional): Division factor for batch processing. Reduce the amount of batches to reduce the process switching. Defaults to 2.
        ignore_obsolete (bool, optional): Whether to ignore obsolete messages. Defaults to False.
        abort_invalid (bool, optional): Abort parsing on encountering invalid entries. Defaults to True.
        version (str, optional): Generator version to be used if the catalog version is not set. Defaults to VERSION.
        locale (str, optional): Locale to be used for the catalog. Defaults to machine_language, ie. LANG=en_GB.UTF-8 in environment variables.
        charset (str, optional): Charset for the catalog (used in Catalog creation). Defaults to machine_encoding, ie. using UTF-8 above.
        domain (str, optional): Domain for the catalog. Defaults to 'message'.

    Returns:
        Catalog: A Babel Catalog object containing the parsed messages and metadata.

    Raises:
        Exception: Any exception raised by the underlying parsing functions if the PO file content is invalid
                   or if parameter conversion fails.
    """
    # Create a default catalog using the provided parameters.
    default_catalog = Catalog(locale=locale, domain=domain, charset=charset, version=version)

    # Determine the charset of the PO file content.
    charset = get_char_set(filename)

    # Open the file in binary mode and decode its content using the detected charset.
    with open(filename, "rb") as f:
        file_content = f.read().decode(charset, errors="replace")

    # Split the file content into blocks for parsing.
    blocks = split_into_blocks(file_content)

    # Initialize the parser with the blocks and configuration options.
    ps.init_parser(
        blocks,
        is_debug=debug,
        is_multi_processing=multiprocessing,
        batch_size_division=batch_size_division,
        is_hook_except=hookexcept,
        abort_on_invalid=abort_invalid,
        ignore_obsolete=ignore_obsolete,
    )

    # Parse the catalog header from the blocks.
    catalog = parse_catalog(blocks, default_catalog)

    # Set the catalog version to the generator version if it is not already set.
    if (catalog.version is None) or (len(catalog.version) == 0):
        catalog.version = version

    # Set the global catalog for the message parser.
    ps.CATALOG = catalog

    # Parse the individual messages and collect errors.
    messages, errors = ps.parse()

    # Store parsed messages in the catalog; classify obsolete messages separately.
    for msg in messages:
        is_obsolete = getattr(msg, 'obsolete', False)
        if is_obsolete:
            catalog.obsolete[msg.id] = msg
        else:
            catalog[msg.id] = msg

    # If any errors were encountered, print them to stderr.
    printErrors()

    return catalog


