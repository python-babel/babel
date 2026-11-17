from __future__ import annotations

import pathlib

from babel.messages.catalog import Catalog
from babel.messages.pofile import read_po, write_po

CUSTOM_EXTRACTOR_COOKIE = "custom extractor was here"


def custom_extractor(fileobj, keywords, comment_tags, options):
    if "treat" not in options:
        raise RuntimeError(f"The custom extractor refuses to run without a delicious treat; got {options!r}")
    return [(1, next(iter(keywords)), (CUSTOM_EXTRACTOR_COOKIE,), [])]


class Distribution:  # subset of distutils.dist.Distribution
    def __init__(self, attrs: dict) -> None:
        self.attrs = attrs

    def get_name(self) -> str:
        return self.attrs['name']

    def get_version(self) -> str:
        return self.attrs['version']

    @property
    def packages(self) -> list[str]:
        return self.attrs['packages']


def write_po_file(path: pathlib.Path, messages, **catalog_kwargs) -> pathlib.Path:
    """Write `(id, string[, add_kwargs])` tuples to `path` as a PO file."""
    catalog = Catalog(**catalog_kwargs)
    for id, string, *extra in messages:
        catalog.add(id, string=string, **(extra[0] if extra else {}))
    with open(path, 'wb') as file:
        write_po(file, catalog)
    return path


def run_command(cmd, input_files, output_file: pathlib.Path, **options) -> Catalog:
    """Run a concat/merge command object and read back the catalog it wrote."""
    cmd.input_files = [str(path) for path in input_files]
    cmd.output_file = str(output_file)
    for name, value in options.items():
        setattr(cmd, name, value)
    cmd.finalize_options()
    cmd.run()
    with open(output_file, 'rb') as file:
        return read_po(file)
