"""
babel.messages.poparse
~~~~~~~~~~~~~~~~~~~~~

Reading and writing of files in the ``gettext`` PO (portable object)
format.

:copyright: (c) 2013-2024 by the Babel Team.
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
from babel.messages.catalog_parser import parse_catalog
from babel.messages.block_utils import split_into_blocks
import babel.messages.msg_parser as ps
from babel.messages.parse_utils import get_str_kwargs, get_boolean_kwarg, get_int_kwarg, get_char_set

def load_po(filename, **kwargs):
    """
    Load and parse a PO (Portable Object) file into a Babel Catalog object.

    This function performs the following steps:
      1. Retrieves the machine's default locale and encoding.
      2. Extracts various configuration options from the provided kwargs:
         - Debug mode flag.
         - Multiprocessing flag.
         - Hook exception flag.
         - Batch size division for processing.
         - Flags for ignoring obsolete messages and aborting on invalid entries.
         - Generator version, locale, charset, and domain for the catalog.
      3. Creates a default catalog using these parameters.
      4. Determines the charset of the PO file via the get_char_set function.
      5. Reads and decodes the file content based on the detected charset.
      6. Splits the file content into blocks for parsing.
      7. Initializes the message parser with the pre-split blocks and configuration options.
      8. Parses the catalog header from the blocks.
      9. Sets the catalog version if not provided.
     10. Assigns the catalog to the parser's global state.
     11. Parses the individual messages, classifying obsolete messages separately.
     12. Prints any encountered parsing errors to stderr.
     13. Returns the populated Catalog object.

    Parameters:
        filename (str): Path to the PO file to be loaded.
        **kwargs: Additional keyword arguments for configuration.
            Recognized keys include:
              - '-d' or 'debug': Enable debug mode (bool).
              - '-m' or 'multiprocessing': Enable multiprocessing (bool).
              - '-hk' or 'hookexcept': Enable hook exception handling (bool).
              - '-bd' or 'batch_size_division': Set the batch size division (int).
              - '-igob' or 'ignore_obsolete': Ignore obsolete messages (bool).
              - '-abrt' or 'abort_invalid': Abort on invalid entries (bool).
              - '-v' or 'version': Specify the generator version (str).
              - '-l' or 'locale': Specify the catalog locale (str).
              - '-chs' or 'charset': Specify the catalog charset (str).
              - '-dom' or 'domain': Specify the catalog domain (str).

    Returns:
        Catalog: A Babel Catalog object containing the parsed messages and metadata.

    Raises:
        Exceptions from underlying parsing functions if the PO file content is invalid
        or if keyword argument conversions fail.
    """
    # Retrieve the machine's default language and encoding.
    machine_language, machine_encoding = locale.getdefaultlocale()

    # Extract boolean and integer configuration options from kwargs.
    is_debug = get_boolean_kwarg(kwargs, ['-d', 'debug'], default=False)
    is_multi_processing = get_boolean_kwarg(kwargs, ['-m', 'multiprocessing'], default=False)
    is_hook_except = get_boolean_kwarg(kwargs, ['-hk', 'hookexcept'], default=False)
    batch_size_division = get_int_kwarg(kwargs, ['-bd', 'batch_size_division'], default=2)
    is_ignore_obsolete = get_boolean_kwarg(kwargs, ['-igob', 'ignore_obsolete'], default=True)
    is_abort_on_invalid = get_boolean_kwarg(kwargs, ['-abrt', 'abort_invalid'], default=True)

    # Extract string-based configuration options.
    generator_version = get_str_kwargs(kwargs, ['-v', 'version'], default=VERSION)
    cat_locale = get_str_kwargs(kwargs, ['-l', 'locale'], default=machine_language)
    cat_charset = get_str_kwargs(kwargs, ['-chs', 'charset'], default=machine_encoding)
    cat_domain = get_str_kwargs(kwargs, ['-dom', 'domain'], default='messages')

    # Create a default catalog using the provided or default parameters.
    default_catalog = Catalog(locale=cat_locale, domain=cat_domain, charset=cat_charset, version=generator_version)

    # Determine the charset of the PO file content.
    charset = get_char_set(filename)

    # Open the file in binary mode and decode its content using the detected charset.
    with open(filename, "rb") as f:
        file_content = f.read().decode(charset, errors="replace")

    # Split the file content into blocks, which are used as units for parsing.
    blocks = split_into_blocks(file_content)

    # Initialize the parser with the pre-split blocks and configuration options.
    ps.init_parser(
        blocks,
        is_debug=is_debug,
        is_multi_processing=is_multi_processing,
        batch_size_division=batch_size_division,
        is_hook_except=is_hook_except,
        abort_on_invalid=is_abort_on_invalid,
        ignore_obsolete=is_ignore_obsolete,
    )

    # Parse the catalog header from the blocks using the default catalog.
    catalog = parse_catalog(blocks, default_catalog)

    # If the catalog version is not set or is empty, use the generator version.
    is_using_custom_generated_catalog_version = (catalog.version is None) or (len(catalog.version) == 0)
    if is_using_custom_generated_catalog_version:
        catalog.version = generator_version

    # Set the global catalog for the message parser.
    ps.CATALOG = catalog

    # Parse the individual messages from the blocks and collect any errors.
    messages, errors = ps.parse()

    # Store parsed messages in the catalog. Obsolete messages are kept separately.
    for msg in messages[1:]:
        is_obsolete = getattr(msg, 'obsolete', False)
        if is_obsolete:
            catalog.obsolete[msg.id] = msg
        else:
            catalog[msg.id] = msg

    # If there are errors, remove duplicates and print them to stderr.
    if errors:
        errors = list(set(errors))
        print("Errors encountered:", file=sys.stderr)
        for err in errors:
            print(err, file=sys.stderr)

    # Return the populated catalog.
    return catalog

