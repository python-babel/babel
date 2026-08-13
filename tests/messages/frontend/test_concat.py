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

import io
import pathlib
import sys

import pytest
from freezegun import freeze_time

from babel.messages import Catalog, frontend, pofile
from babel.messages.frontend import OptionError
from tests.messages.consts import TEST_PROJECT_DISTRIBUTION_DATA
from tests.messages.utils import Distribution


@pytest.fixture(autouse=True)
def frozen_time():
    with freeze_time("1994-11-11"):
        yield


@pytest.fixture
def concat_cmd():
    dist = Distribution(TEST_PROJECT_DISTRIBUTION_DATA)
    cmd = frontend.ConcatenateCatalog(dist)
    cmd.initialize_options()
    return cmd


@pytest.fixture
def po_files(tmp_path: pathlib.Path):
    temp1 = tmp_path / 'msgcat_temp1.po'
    temp2 = tmp_path / 'msgcat_temp2.po'

    with open(temp1, 'wb') as file:
        catalog = Catalog()
        catalog.add('other1', string='Other 1', locations=[('simple.py', 1)], flags=['flag1000'])
        catalog.add('other2', string='Other 2', locations=[('simple.py', 10)])
        catalog.add('same', string='Same', locations=[('simple.py', 100)], flags=['flag1', 'flag1.2'])
        catalog.add('almost_same', string='Almost same', locations=[('simple.py', 1000)], flags=['flag2'])
        catalog.add(('plural', 'plurals'), string=('Plural', 'Plurals'), locations=[('simple.py', 2000)])
        pofile.write_po(file, catalog)

    with open(temp2, 'wb') as file:
        catalog = Catalog()
        catalog.add('other3', string='Other 3', locations=[('hard.py', 1)])
        catalog.add('other4', string='Other 4', locations=[('hard.py', 10)])
        catalog.add('almost_same', string='A bit same', locations=[('hard.py', 1000)], flags=['flag3'])
        catalog.add('same', string='Same', locations=[('hard.py', 100)], flags=['flag4'])
        catalog.add(('plural', 'plurals'), string=('Plural', 'Plurals other'), locations=[('hard.py', 2000)])
        pofile.write_po(file, catalog)

    return temp1, temp2


def test_no_input_files(concat_cmd):
    with pytest.raises(OptionError):
        concat_cmd.finalize_options()


def test_no_output_file(concat_cmd):
    concat_cmd.input_files = ['project/i18n/messages.pot']
    concat_cmd.finalize_options()  # output_file not required; defaults to stdout


def test_unique_exclusive_with_less_than(concat_cmd, po_files):
    temp1, temp2 = po_files
    concat_cmd.input_files = [str(temp1), str(temp2)]
    concat_cmd.unique = True
    concat_cmd.less_than = 3
    with pytest.raises(OptionError):
        concat_cmd.finalize_options()


def test_unique_exclusive_with_more_than(concat_cmd, po_files):
    temp1, temp2 = po_files
    concat_cmd.input_files = [str(temp1), str(temp2)]
    concat_cmd.unique = True
    concat_cmd.more_than = 1
    with pytest.raises(OptionError):
        concat_cmd.finalize_options()


def test_default(concat_cmd, po_files, tmp_path):
    temp1, temp2 = po_files
    output_file = tmp_path / 'msgcat.po'
    concat_cmd.input_files = [str(temp1), str(temp2)]
    concat_cmd.output_file = str(output_file)
    concat_cmd.finalize_options()
    concat_cmd.run()

    content = output_file.read_text()

    assert 'msgid "other1"' in content
    assert 'msgstr "Other 1"' in content
    assert 'msgid "other3"' in content

    assert 'msgid "same"' in content
    assert 'msgstr "Same"' in content
    assert content.count('#-#-#-#-# msgcat_temp1.po') == 0 or 'msgid "same"' not in [
        block for block in content.split('\n\n') if '#-#-#-#-#' in block
    ]

    almost_same_block = next(b for b in content.split('\n\n') if 'msgid "almost_same"' in b)
    assert 'fuzzy' in almost_same_block
    assert '#-#-#-#-#' in almost_same_block
    assert 'Almost same' in almost_same_block
    assert 'A bit same' in almost_same_block

    plural_block = next(b for b in content.split('\n\n') if 'msgid "plural"' in b)
    assert 'fuzzy' in plural_block
    assert '#-#-#-#-#' in plural_block


def test_use_first(concat_cmd, po_files, tmp_path):
    temp1, temp2 = po_files
    output_file = tmp_path / 'msgcat.po'
    concat_cmd.input_files = [str(temp1), str(temp2)]
    concat_cmd.output_file = str(output_file)
    concat_cmd.use_first = True
    concat_cmd.finalize_options()
    concat_cmd.run()

    content = output_file.read_text()

    assert '#-#-#-#-#' not in content

    almost_same_block = next(b for b in content.split('\n\n') if 'msgid "almost_same"' in b)
    assert 'fuzzy' not in almost_same_block
    assert 'msgstr "Almost same"' in almost_same_block

    plural_block = next(b for b in content.split('\n\n') if 'msgid "plural"' in b)
    assert 'fuzzy' not in plural_block
    assert 'msgstr[0] "Plural"' in plural_block
    assert 'msgstr[1] "Plurals"' in plural_block


def test_unique(concat_cmd, po_files, tmp_path):
    temp1, temp2 = po_files
    output_file = tmp_path / 'msgcat.po'
    concat_cmd.input_files = [str(temp1), str(temp2)]
    concat_cmd.output_file = str(output_file)
    concat_cmd.unique = True
    concat_cmd.finalize_options()
    concat_cmd.run()

    content = output_file.read_text()

    assert 'msgid "other1"' in content
    assert 'msgid "other2"' in content
    assert 'msgid "other3"' in content
    assert 'msgid "other4"' in content
    assert 'msgid "same"' not in content
    assert 'msgid "almost_same"' not in content


def test_less_than_equivalent_to_unique(concat_cmd, po_files, tmp_path):
    temp1, temp2 = po_files
    output_file = tmp_path / 'msgcat.po'
    concat_cmd.input_files = [str(temp1), str(temp2)]
    concat_cmd.output_file = str(output_file)
    concat_cmd.less_than = 2
    concat_cmd.finalize_options()
    concat_cmd.run()
    less_than_content = output_file.read_text()

    concat_cmd.less_than = None
    concat_cmd.unique = True
    concat_cmd.finalize_options()
    concat_cmd.run()
    unique_content = output_file.read_text()

    assert less_than_content == unique_content


def test_more_than(concat_cmd, po_files, tmp_path):
    temp1, temp2 = po_files
    output_file = tmp_path / 'msgcat.po'
    concat_cmd.input_files = [str(temp1), str(temp2)]
    concat_cmd.output_file = str(output_file)
    concat_cmd.more_than = 1
    concat_cmd.finalize_options()
    concat_cmd.run()

    content = output_file.read_text()

    assert 'msgid "other1"' not in content
    assert 'msgid "other3"' not in content
    assert 'msgid "same"' in content
    assert 'msgid "almost_same"' in content
    assert 'msgid "plural"' in content

    almost_same_block = next(b for b in content.split('\n\n') if 'msgid "almost_same"' in b)
    assert 'fuzzy' in almost_same_block


def test_no_wrap_width_exclusive(concat_cmd, po_files):
    temp1, _ = po_files
    concat_cmd.input_files = [str(temp1)]
    concat_cmd.no_wrap = True
    concat_cmd.width = 80
    with pytest.raises(OptionError):
        concat_cmd.finalize_options()


def test_stdout_output(concat_cmd, po_files, monkeypatch):
    temp1, _ = po_files
    concat_cmd.input_files = [str(temp1)]
    concat_cmd.finalize_options()

    buf = io.BytesIO()
    monkeypatch.setattr(sys, 'stdout', type('FakeStdout', (), {'buffer': buf})())
    concat_cmd.run()

    content = buf.getvalue().decode('utf-8')
    assert 'msgid "other1"' in content
    assert 'msgstr "Other 1"' in content
    assert 'msgid "same"' in content


def test_stdout_dash(concat_cmd, po_files, monkeypatch):
    temp1, _ = po_files
    concat_cmd.input_files = [str(temp1)]
    concat_cmd.output_file = '-'
    concat_cmd.finalize_options()

    buf = io.BytesIO()
    monkeypatch.setattr(sys, 'stdout', type('FakeStdout', (), {'buffer': buf})())
    concat_cmd.run()

    content = buf.getvalue().decode('utf-8')
    assert 'msgid "other1"' in content


def test_same_string_no_conflict(concat_cmd, po_files, tmp_path):
    temp1, temp2 = po_files
    output_file = tmp_path / 'msgcat.po'
    concat_cmd.input_files = [str(temp1), str(temp2)]
    concat_cmd.output_file = str(output_file)
    concat_cmd.finalize_options()
    concat_cmd.run()

    content = output_file.read_text()
    same_block = next(b for b in content.split('\n\n') if 'msgid "same"' in b)
    assert 'fuzzy' not in same_block
    assert '#-#-#-#-#' not in same_block
    assert 'msgstr "Same"' in same_block


def test_no_location(concat_cmd, po_files, tmp_path):
    temp1, temp2 = po_files
    output_file = tmp_path / 'msgcat.po'
    concat_cmd.input_files = [str(temp1), str(temp2)]
    concat_cmd.output_file = str(output_file)
    concat_cmd.no_location = True
    concat_cmd.finalize_options()
    concat_cmd.run()

    content = output_file.read_text()
    assert '#: ' not in content
    assert 'msgid "other1"' in content


def test_sort_output(concat_cmd, po_files, tmp_path):
    temp1, temp2 = po_files
    output_file = tmp_path / 'msgcat.po'
    concat_cmd.input_files = [str(temp1), str(temp2)]
    concat_cmd.output_file = str(output_file)
    concat_cmd.sort_output = True
    concat_cmd.finalize_options()
    concat_cmd.run()

    content = output_file.read_text()
    msgid_positions = {
        'almost_same': content.index('msgid "almost_same"'),
        'other1': content.index('msgid "other1"'),
        'other2': content.index('msgid "other2"'),
        'other3': content.index('msgid "other3"'),
        'other4': content.index('msgid "other4"'),
        'same': content.index('msgid "same"'),
    }
    ordered = sorted(msgid_positions, key=msgid_positions.get)
    assert ordered == ['almost_same', 'other1', 'other2', 'other3', 'other4', 'same']


def test_single_input_file(concat_cmd, po_files, tmp_path):
    temp1, _ = po_files
    output_file = tmp_path / 'msgcat.po'
    concat_cmd.input_files = [str(temp1)]
    concat_cmd.output_file = str(output_file)
    concat_cmd.finalize_options()
    concat_cmd.run()

    content = output_file.read_text()
    assert 'msgid "other1"' in content
    assert 'msgid "other2"' in content
    assert 'msgid "same"' in content
    assert '#-#-#-#-#' not in content
    assert 'fuzzy' not in content


def test_unique_exclusive_with_more_than_nonzero(concat_cmd, po_files):
    temp1, temp2 = po_files
    concat_cmd.input_files = [str(temp1), str(temp2)]
    concat_cmd.unique = True
    concat_cmd.more_than = 0
    concat_cmd.finalize_options()


def test_conflicted_po_raises_on_read(tmp_path):
    from babel.messages.pofile import PoFileError, read_po

    conflicted = tmp_path / 'conflicted.po'
    conflicted.write_text(
        'msgid "hello"\n'
        '#-#-#-#-#  file1.po (PROJECT 1.0)  #-#-#-#-#\n'
        'msgstr "Hello"\n',
    )
    with pytest.raises(PoFileError):
        with open(conflicted) as f:
            read_po(f, abort_invalid=True)


def test_non_utf8_input(concat_cmd, tmp_path):
    input_file = tmp_path / 'latin1.po'
    output_file = tmp_path / 'output.po'
    with open(input_file, 'wb') as file:
        catalog = Catalog(locale='fr', charset='iso-8859-1')
        catalog.add('coffee', string='café')
        pofile.write_po(file, catalog)

    concat_cmd.input_files = [str(input_file)]
    concat_cmd.output_file = str(output_file)
    concat_cmd.finalize_options()
    concat_cmd.run()

    with open(output_file, 'rb') as file:
        assert pofile.read_po(file)['coffee'].string == 'café'
