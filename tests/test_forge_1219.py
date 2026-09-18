"""Regression test for blank PO-Revision-Date header.

When a .po file has a blank PO-Revision-Date field (as produced by some
tools like Poedit), pybabel raises a ValueError from
``_parse_datetime_header`` because it tries to parse an empty string.
The revision date should simply be left unset in that case.
"""

import pytest

from babel.messages.catalog import Catalog


def test_blank_po_revision_date_does_not_raise():
    """A blank PO-Revision-Date should not raise an exception."""
    catalog = Catalog()
    # Simulate the headers that a .po file with a blank PO-Revision-Date
    # would contain.
    headers = [
        ("PO-Revision-Date", ""),
    ]
    # This should not raise; revision_date should remain None.
    catalog._set_mime_headers(headers)
    assert catalog.revision_date is None


def test_blank_pot_creation_date_does_not_raise():
    """A blank POT-Creation-Date should not raise an exception either."""
    catalog = Catalog()
    headers = [
        ("POT-Creation-Date", ""),
    ]
    catalog._set_mime_headers(headers)
    assert catalog.creation_date is None