from __future__ import annotations

import io

import pytest

from babel.messages import Catalog
from babel.messages.extract import DEFAULT_KEYWORDS, extract, extract_python
from babel.messages.mofile import read_mo
from babel.messages.pofile import read_po
from tests.benchmarks.helpers import build_catalog, dump_mo, dump_po

MESSAGE_COUNT = 100


@pytest.fixture()
def catalog() -> Catalog:
    return build_catalog(MESSAGE_COUNT)


@pytest.fixture()
def po_source(catalog) -> str:
    return dump_po(catalog)


@pytest.fixture()
def mo_bytes(catalog) -> bytes:
    return dump_mo(catalog)


_VIEW_TEMPLATE = '''
def view_{i}(request, count):
    title = _("Page title {i}")
    body = gettext("Body text for page {i}")
    # NOTE: shown next to the item counter
    footer = ngettext("%(num)d item", "%(num)d items", count) % {{"num": count}}
    return render(request, title=title, body=body, footer=footer)
'''

PYTHON_SOURCE = (
    "from gettext import gettext, ngettext\n\n_ = gettext\n"
    + "".join(_VIEW_TEMPLATE.format(i=i) for i in range(7))
).encode("utf-8")


def test_catalog_add(benchmark):
    # Constructed inside the callable, since adding messages mutates the catalog.
    assert benchmark(lambda: len(build_catalog(MESSAGE_COUNT))) == MESSAGE_COUNT


def test_catalog_iter(benchmark, catalog):
    # Iteration also yields the header message, hence the + 1.
    assert benchmark(lambda: len(list(catalog))) == MESSAGE_COUNT + 1


def test_catalog_get(benchmark, catalog):
    # A plural ID exercises the tuple branch of the key lookup.
    assert benchmark(lambda: catalog.get(("5 apple", "5 apples")).string) == (
        "5 omena",
        "5 omenaa",
    )


def test_read_po(benchmark, po_source):
    benchmark(lambda: read_po(io.StringIO(po_source), locale="fi"))


def test_write_po(benchmark, catalog):
    benchmark(lambda: dump_po(catalog))


def test_write_mo(benchmark, catalog):
    benchmark(lambda: dump_mo(catalog))


def test_read_mo(benchmark, mo_bytes):
    # Fuzzy messages are not written to the MO, so this catalog is smaller.
    catalog = benchmark(lambda: read_mo(io.BytesIO(mo_bytes)))
    assert catalog.get("Message number 42").string == "Viesti numero 42"


def test_extract_python(benchmark):
    def run():
        return list(extract_python(io.BytesIO(PYTHON_SOURCE), DEFAULT_KEYWORDS, ["NOTE:"], {}))

    assert len(benchmark(run)) == 21


def test_extract_method_python(benchmark):
    # Same work as above, plus the extraction method lookup/dispatch in extract().
    def run():
        return list(extract("python", io.BytesIO(PYTHON_SOURCE), DEFAULT_KEYWORDS, ["NOTE:"]))

    assert len(benchmark(run)) == 21
