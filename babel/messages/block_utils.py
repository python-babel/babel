"""
babel.messages.block_utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Utility functions for splitting PO file content into blocks.
This module provides a function to split the content of a PO file into individual
blocks representing separate message entries. Each block is separated by one or more
blank lines and is returned as a tuple containing the starting line number and the block text.

:copyright: (c) 2025 by the Babel Team.
:license: BSD, see LICENSE for more details.
"""


def split_into_blocks(content: str):
    """
    Splits the given content into blocks separated by blank lines.

    Each block is returned as a tuple (start_line, block_text), where:
      - start_line: The line number in the original content where the block begins.
      - block_text: The complete text of the block, with original line breaks preserved.

    The function processes the content line by line:
      1. It splits the content into individual lines.
      2. It accumulates consecutive non-blank lines into a current block.
      3. When a blank line is encountered (or at the end of the content), the current block
         is finished and stored along with its starting line number.
      4. The starting line number for the next block is updated.

    This function is shared between the Catalog parser and the Messages parser.

    :param content: The complete text content of a PO file.
    :return: A list of tuples, each tuple containing (start_line, block_text) for a block.
    """
    lines = content.splitlines()  # Split the content into individual lines.
    blocks = []  # List to store the resulting blocks.
    current_block = []  # List to accumulate lines for the current block.
    current_start_line = 1  # Line number where the current block starts.
    line_number = 1  # Counter for the current line number.

    for line in lines:
        if line.strip() == "":  # Check if the line is blank.
            if current_block:
                # If the current block has content, join it into a single string and add to blocks.
                blocks.append((current_start_line, "\n".join(current_block)))
                current_block = []  # Reset the current block.
            # Update the start line for the next block (line after the blank line).
            current_start_line = line_number + 1
        else:
            # Add non-blank lines to the current block.
            current_block.append(line)
        line_number += 1

    # If there is any remaining content in the current block, add it as the final block.
    if current_block:
        blocks.append((current_start_line, "\n".join(current_block)))
    return blocks
