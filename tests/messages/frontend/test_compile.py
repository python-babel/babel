#
# Copyright (C) 2007-2011 Edgewall Software, 2013-2025 the Babel team
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution. The terms
# are also available at https://github.com/python-babel/babel/blob/master/LICENSE.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at https://github.com/python-babel/babel/commits/master/.

from __future__ import annotations

import os
import shutil

import pytest

from babel.messages import frontend
from babel.messages.catalog import Catalog
from babel.messages.frontend import OptionError, compile_message_catalog
from babel.messages.mofile import read_mo
from babel.messages.pofile import write_po
from tests.messages.consts import TEST_PROJECT_DISTRIBUTION_DATA, data_dir, i18n_dir
from tests.messages.utils import Distribution


@pytest.fixture
def compile_catalog_cmd(monkeypatch):
    monkeypatch.chdir(data_dir)
    dist = Distribution(TEST_PROJECT_DISTRIBUTION_DATA)
    cmd = frontend.CompileCatalog(dist)
    cmd.initialize_options()
    return cmd


def test_no_directory_or_output_file_specified(compile_catalog_cmd):
    compile_catalog_cmd.locale = 'en_US'
    compile_catalog_cmd.input_file = 'dummy'
    with pytest.raises(OptionError):
        compile_catalog_cmd.finalize_options()


def test_no_directory_or_input_file_specified(compile_catalog_cmd):
    compile_catalog_cmd.locale = 'en_US'
    compile_catalog_cmd.output_file = 'dummy'
    with pytest.raises(OptionError):
        compile_catalog_cmd.finalize_options()


def test_compile_message_catalog_input_output_file(tmp_path):
    po_file = os.path.join(i18n_dir, 'de_DE', 'LC_MESSAGES', 'messages.po')
    mo_file = tmp_path / 'messages.mo'
    n_errors = compile_message_catalog(
        input_file=po_file,
        output_file=str(mo_file),
        locale='de_DE',
        use_fuzzy=True,
    )
    assert n_errors == 0
    assert mo_file.is_file()
    with open(mo_file, 'rb') as fp:
        catalog = read_mo(fp)
    assert catalog.locale is not None


def test_compile_message_catalog_skips_fuzzy_by_default(tmp_path):
    # The German catalog is marked as fuzzy, so nothing should be written
    # unless use_fuzzy is set.
    po_file = os.path.join(i18n_dir, 'de_DE', 'LC_MESSAGES', 'messages.po')
    mo_file = tmp_path / 'messages.mo'
    n_errors = compile_message_catalog(
        input_file=po_file,
        output_file=str(mo_file),
        locale='de_DE',
    )
    assert n_errors == 0
    assert not mo_file.exists()


def test_compile_message_catalog_directory(tmp_path):
    src = os.path.join(i18n_dir, 'de_DE')
    shutil.copytree(src, tmp_path / 'de_DE')
    n_errors = compile_message_catalog(
        directory=str(tmp_path),
        locale='de_DE',
        use_fuzzy=True,
    )
    assert n_errors == 0
    assert (tmp_path / 'de_DE' / 'LC_MESSAGES' / 'messages.mo').is_file()


def test_compile_message_catalog_multiple_domains(tmp_path):
    src = os.path.join(i18n_dir, 'de_DE')
    shutil.copytree(src, tmp_path / 'de_DE')
    compile_message_catalog(
        directory=str(tmp_path),
        locale='de_DE',
        domain=['foo', 'bar'],
        use_fuzzy=True,
    )
    lc_messages = tmp_path / 'de_DE' / 'LC_MESSAGES'
    assert (lc_messages / 'foo.mo').is_file()
    assert (lc_messages / 'bar.mo').is_file()


def test_compile_message_catalog_no_catalogs(tmp_path):
    with pytest.raises(OptionError):
        compile_message_catalog(directory=str(tmp_path))


def test_compile_message_catalog_counts_errors(tmp_path):
    catalog = Catalog(locale='en_US')
    catalog.fuzzy = False
    catalog.add('%(first)s', '%(second)s', flags=['python-format'])
    po_file = tmp_path / 'broken.po'
    with open(po_file, 'wb') as fp:
        write_po(fp, catalog)
    mo_file = tmp_path / 'broken.mo'
    n_errors = compile_message_catalog(
        input_file=str(po_file),
        output_file=str(mo_file),
        locale='en_US',
    )
    assert n_errors == 1
    assert mo_file.is_file()
