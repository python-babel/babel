from __future__ import annotations

import datetime
import io

from babel.messages import Catalog
from babel.messages.mofile import write_mo
from babel.messages.pofile import write_po


def build_catalog(message_count: int) -> Catalog:
    # Fixed dates keep the serialized headers (and thus PO/MO bytes) stable.
    catalog = Catalog(
        locale="fi",
        creation_date=datetime.datetime(2025, 10, 15, 12, 0, 0),
        revision_date=datetime.datetime(2025, 10, 16, 12, 0, 0),
    )
    for i in range(message_count):
        locations = [(f"module_{i % 7}.py", i * 3 + 1)]
        if i % 5 == 0:
            catalog.add(
                (f"{i} apple", f"{i} apples"),
                (f"{i} omena", f"{i} omenaa"),
                locations=locations,
                auto_comments=[f"Auto comment for message {i}"],
            )
        else:
            catalog.add(
                f"Message number {i}",
                f"Viesti numero {i}",
                locations=locations,
                flags=["fuzzy"] if i % 11 == 0 else (),
                user_comments=[f"Translator note {i}"] if i % 3 == 0 else (),
            )
    return catalog


def dump_po(catalog: Catalog) -> str:
    buf = io.BytesIO()
    write_po(buf, catalog)
    return buf.getvalue().decode("utf-8")


def dump_mo(catalog: Catalog) -> bytes:
    buf = io.BytesIO()
    write_mo(buf, catalog)
    return buf.getvalue()
