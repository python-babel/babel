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

import pathlib
import shutil

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
def merge_cmd():
    dist = Distribution(TEST_PROJECT_DISTRIBUTION_DATA)
    cmd = frontend.MergeCatalog(dist)
    cmd.initialize_options()
    return cmd


@pytest.fixture
def merge_files(tmp_path: pathlib.Path):
    temp_def = tmp_path / 'msgmerge_def.po'
    temp_ref = tmp_path / 'msgmerge_ref.pot'
    compendium = tmp_path / 'compendium.po'

    with open(temp_ref, 'wb') as file:
        catalog = Catalog()
        for word in ['word1', 'word2', 'word3', 'word4']:
            catalog.add(word)
        pofile.write_po(file, catalog)

    with open(temp_def, 'wb') as file:
        catalog = Catalog()
        catalog.add('word1', string='Word 1')
        catalog.add('word2', string='Word 2')
        catalog.add('word3')
        pofile.write_po(file, catalog)

    with open(compendium, 'wb') as file:
        catalog = Catalog()
        catalog.add('word1', string='Comp Word 1')
        catalog.add('word2', string='Comp Word 2')
        catalog.add('word4', string='Word 4')
        catalog.add('word5', string='Word 5')
        pofile.write_po(file, catalog)

    return temp_def, temp_ref, compendium


def test_no_input_files(merge_cmd):
    with pytest.raises(OptionError):
        merge_cmd.finalize_options()

    with pytest.raises(OptionError):
        merge_cmd.input_files = ['1']
        merge_cmd.finalize_options()

    with pytest.raises(OptionError):
        merge_cmd.input_files = ['1', '2', '3']
        merge_cmd.finalize_options()


def test_no_output_file(merge_cmd, merge_files):
    temp_def, temp_ref, _ = merge_files
    merge_cmd.input_files = [str(temp_def), str(temp_ref)]
    with pytest.raises(OptionError):
        merge_cmd.finalize_options()

    merge_cmd.output_file = str(temp_ref)
    merge_cmd.finalize_options()

    merge_cmd.output_file = None
    merge_cmd.update = True
    merge_cmd.finalize_options()


def test_default(merge_cmd, merge_files, tmp_path):
    temp_def, temp_ref, _ = merge_files
    output_file = tmp_path / 'msgmerge.po'
    merge_cmd.input_files = [str(temp_def), str(temp_ref)]
    merge_cmd.output_file = str(output_file)
    merge_cmd.no_fuzzy_matching = True
    merge_cmd.finalize_options()
    merge_cmd.run()

    content = output_file.read_text()

    assert 'msgid "word1"' in content
    assert 'msgstr "Word 1"' in content
    assert 'msgid "word2"' in content
    assert 'msgstr "Word 2"' in content

    assert 'msgid "word4"' in content
    word4_block = next(b for b in content.split('\n\n') if 'msgid "word4"' in b)
    assert 'msgstr ""' in word4_block


def test_compendium(merge_cmd, merge_files, tmp_path):
    temp_def, temp_ref, compendium = merge_files
    output_file = tmp_path / 'msgmerge.po'
    merge_cmd.input_files = [str(temp_def), str(temp_ref)]
    merge_cmd.output_file = str(output_file)
    merge_cmd.compendium = [str(compendium)]
    merge_cmd.no_fuzzy_matching = True
    merge_cmd.no_compendium_comment = True
    merge_cmd.finalize_options()
    merge_cmd.run()

    content = output_file.read_text()

    assert 'msgstr "Word 4"' in content

    word1_block = next(b for b in content.split('\n\n') if 'msgid "word1"' in b)
    assert 'msgstr "Word 1"' in word1_block
    assert 'Comp Word 1' not in word1_block


def test_compendium_overwrite(merge_cmd, merge_files, tmp_path):
    temp_def, temp_ref, compendium = merge_files
    output_file = tmp_path / 'msgmerge.po'
    merge_cmd.input_files = [str(temp_def), str(temp_ref)]
    merge_cmd.output_file = str(output_file)
    merge_cmd.compendium = [str(compendium)]
    merge_cmd.no_fuzzy_matching = True
    merge_cmd.no_compendium_comment = True
    merge_cmd.compendium_overwrite = True
    merge_cmd.finalize_options()
    merge_cmd.run()

    content = output_file.read_text()

    word1_block = next(b for b in content.split('\n\n') if 'msgid "word1"' in b and '#~' not in b)
    assert 'msgstr "Comp Word 1"' in word1_block

    assert '#~ msgid "word1"' in content
    assert '#~ msgstr "Word 1"' in content


def test_update(merge_cmd, merge_files):
    temp_def, temp_ref, _ = merge_files
    merge_cmd.input_files = [str(temp_def), str(temp_ref)]
    merge_cmd.update = True
    merge_cmd.no_fuzzy_matching = True
    merge_cmd.finalize_options()
    merge_cmd.run()

    content = temp_def.read_text()
    assert 'msgstr "Word 1"' in content
    assert 'msgid "word4"' in content


def test_update_backup(merge_cmd, merge_files, tmp_path):
    temp_def, temp_ref, _ = merge_files
    before_content = temp_def.read_text()

    merge_cmd.input_files = [str(temp_def), str(temp_ref)]
    merge_cmd.update = True
    merge_cmd.backup = True
    merge_cmd.no_fuzzy_matching = True
    merge_cmd.finalize_options()
    merge_cmd.run()

    backup = pathlib.Path(str(temp_def) + '~')
    assert backup.exists()
    assert backup.read_text() == before_content

    temp_def.unlink()
    shutil.move(str(backup), str(temp_def))
    merge_cmd.suffix = '.bac'
    merge_cmd.run()

    bac = pathlib.Path(str(temp_def) + '.bac')
    assert bac.exists()
    assert bac.read_text() == before_content


def test_no_wrap_width_exclusive(merge_cmd, merge_files, tmp_path):
    temp_def, temp_ref, _ = merge_files
    output_file = tmp_path / 'msgmerge.po'
    merge_cmd.input_files = [str(temp_def), str(temp_ref)]
    merge_cmd.output_file = str(output_file)
    merge_cmd.no_wrap = True
    merge_cmd.width = 80
    with pytest.raises(OptionError):
        merge_cmd.finalize_options()


def test_compendium_with_comment(merge_cmd, merge_files, tmp_path):
    temp_def, temp_ref, compendium = merge_files
    output_file = tmp_path / 'msgmerge.po'
    merge_cmd.input_files = [str(temp_def), str(temp_ref)]
    merge_cmd.output_file = str(output_file)
    merge_cmd.compendium = [str(compendium)]
    merge_cmd.no_fuzzy_matching = True
    merge_cmd.finalize_options()
    merge_cmd.run()

    content = output_file.read_text()
    assert f'#. {compendium}' in content
    assert 'msgid "word4"' in content
    assert 'msgstr "Word 4"' in content


def test_compendium_does_not_overwrite_existing(merge_cmd, merge_files, tmp_path):
    temp_def, temp_ref, compendium = merge_files
    output_file = tmp_path / 'msgmerge.po'
    merge_cmd.input_files = [str(temp_def), str(temp_ref)]
    merge_cmd.output_file = str(output_file)
    merge_cmd.compendium = [str(compendium)]
    merge_cmd.no_fuzzy_matching = True
    merge_cmd.no_compendium_comment = True
    merge_cmd.finalize_options()
    merge_cmd.run()

    content = output_file.read_text()
    word1_block = next(b for b in content.split('\n\n') if 'msgid "word1"' in b)
    assert 'msgstr "Word 1"' in word1_block
    assert 'Comp Word 1' not in word1_block


def test_multiple_compendiums(merge_cmd, merge_files, tmp_path):
    temp_def, temp_ref, compendium = merge_files
    compendium2 = tmp_path / 'compendium2.po'
    output_file = tmp_path / 'msgmerge.po'

    with open(compendium2, 'wb') as f:
        cat = Catalog()
        cat.add('word3', string='Word 3 from comp2')
        pofile.write_po(f, cat)

    merge_cmd.input_files = [str(temp_def), str(temp_ref)]
    merge_cmd.output_file = str(output_file)
    merge_cmd.compendium = [str(compendium), str(compendium2)]
    merge_cmd.no_fuzzy_matching = True
    merge_cmd.no_compendium_comment = True
    merge_cmd.finalize_options()
    merge_cmd.run()

    content = output_file.read_text()
    assert 'msgstr "Word 4"' in content
    assert 'msgstr "Word 3 from comp2"' in content


def test_compendium_fills_empty_translation(merge_cmd, merge_files, tmp_path):
    temp_def, temp_ref, _ = merge_files
    compendium_with_word3 = tmp_path / 'comp_word3.po'
    output_file = tmp_path / 'msgmerge.po'

    with open(compendium_with_word3, 'wb') as f:
        cat = Catalog()
        cat.add('word3', string='Word 3 comp')
        pofile.write_po(f, cat)

    merge_cmd.input_files = [str(temp_def), str(temp_ref)]
    merge_cmd.output_file = str(output_file)
    merge_cmd.compendium = [str(compendium_with_word3)]
    merge_cmd.no_fuzzy_matching = True
    merge_cmd.no_compendium_comment = True
    merge_cmd.finalize_options()
    merge_cmd.run()

    content = output_file.read_text()
    assert 'msgstr "Word 3 comp"' in content


def test_obsolete_messages(merge_cmd, merge_files, tmp_path):
    temp_def, temp_ref, _ = merge_files
    output_file = tmp_path / 'msgmerge.po'

    merge_cmd.input_files = [str(temp_def), str(temp_ref)]
    merge_cmd.output_file = str(output_file)
    merge_cmd.no_fuzzy_matching = True
    merge_cmd.finalize_options()
    merge_cmd.run()

    content = output_file.read_text()
    assert '#~ msgid' not in content

    extra_def = tmp_path / 'extra_def.po'
    with open(extra_def, 'wb') as f:
        cat = Catalog()
        cat.add('word1', string='Word 1')
        cat.add('old_word', string='Old Word')
        pofile.write_po(f, cat)

    merge_cmd.input_files = [str(extra_def), str(temp_ref)]
    merge_cmd.finalize_options()
    merge_cmd.run()

    content = output_file.read_text()
    assert '#~ msgid "old_word"' in content
    assert '#~ msgstr "Old Word"' in content


def test_compendium_not_applied_for_absent_messages(merge_cmd, merge_files, tmp_path):
    temp_def, temp_ref, compendium = merge_files
    output_file = tmp_path / 'msgmerge.po'
    merge_cmd.input_files = [str(temp_def), str(temp_ref)]
    merge_cmd.output_file = str(output_file)
    merge_cmd.compendium = [str(compendium)]
    merge_cmd.no_fuzzy_matching = True
    merge_cmd.no_compendium_comment = True
    merge_cmd.finalize_options()
    merge_cmd.run()

    content = output_file.read_text()
    active_section = content.split('#~')[0]
    assert 'word5' not in active_section


def test_compendium_matches_message_context(merge_cmd, tmp_path):
    def_file = tmp_path / 'def.po'
    ref_file = tmp_path / 'ref.pot'
    compendium = tmp_path / 'compendium.po'
    output_file = tmp_path / 'output.po'

    for path in (def_file, ref_file):
        with open(path, 'wb') as file:
            catalog = Catalog(locale='es' if path == def_file else None)
            catalog.add('save')
            catalog.add('save', context='menu')
            pofile.write_po(file, catalog)
    with open(compendium, 'wb') as file:
        catalog = Catalog(locale='es')
        catalog.add('save', string='Guardar', context='menu')
        pofile.write_po(file, catalog)

    merge_cmd.input_files = [str(def_file), str(ref_file)]
    merge_cmd.output_file = str(output_file)
    merge_cmd.compendium = [str(compendium)]
    merge_cmd.no_fuzzy_matching = True
    merge_cmd.finalize_options()
    merge_cmd.run()

    with open(output_file, 'rb') as file:
        catalog = pofile.read_po(file)
    assert catalog.get('save').string == ''
    assert catalog.get('save', 'menu').string == 'Guardar'


def test_compendium_overwrite_obsoletes_contextual_message(merge_cmd, tmp_path):
    def_file = tmp_path / 'def.po'
    ref_file = tmp_path / 'ref.pot'
    compendium = tmp_path / 'compendium.po'
    output_file = tmp_path / 'output.po'

    with open(def_file, 'wb') as file:
        catalog = Catalog(locale='es')
        catalog.add('save', string='Old translation', context='menu')
        pofile.write_po(file, catalog)
    with open(ref_file, 'wb') as file:
        catalog = Catalog()
        catalog.add('save', context='menu')
        pofile.write_po(file, catalog)
    with open(compendium, 'wb') as file:
        catalog = Catalog(locale='es')
        catalog.add('save', string='Guardar', context='menu')
        pofile.write_po(file, catalog)

    merge_cmd.input_files = [str(def_file), str(ref_file)]
    merge_cmd.output_file = str(output_file)
    merge_cmd.compendium = [str(compendium)]
    merge_cmd.compendium_overwrite = True
    merge_cmd.no_fuzzy_matching = True
    merge_cmd.finalize_options()
    merge_cmd.run()

    with open(output_file, 'rb') as file:
        catalog = pofile.read_po(file)
    assert catalog.get('save', 'menu').string == 'Guardar'
    assert catalog.obsolete[('save', 'menu')].string == 'Old translation'


def test_compendium_preserves_fuzzy_flag(merge_cmd, tmp_path):
    def_file = tmp_path / 'def.po'
    ref_file = tmp_path / 'ref.pot'
    compendium = tmp_path / 'compendium.po'
    output_file = tmp_path / 'output.po'

    for path in (def_file, ref_file):
        with open(path, 'wb') as file:
            catalog = Catalog(locale='es' if path == def_file else None)
            catalog.add('review')
            pofile.write_po(file, catalog)
    with open(compendium, 'wb') as file:
        catalog = Catalog(locale='es')
        catalog.add('review', string='Revisar', flags=['fuzzy'])
        pofile.write_po(file, catalog)

    merge_cmd.input_files = [str(def_file), str(ref_file)]
    merge_cmd.output_file = str(output_file)
    merge_cmd.compendium = [str(compendium)]
    merge_cmd.no_fuzzy_matching = True
    merge_cmd.finalize_options()
    merge_cmd.run()

    with open(output_file, 'rb') as file:
        message = pofile.read_po(file)['review']
    assert message.string == 'Revisar'
    assert message.fuzzy


def test_non_utf8_definition_and_compendium(merge_cmd, tmp_path):
    def_file = tmp_path / 'def.po'
    ref_file = tmp_path / 'ref.pot'
    compendium = tmp_path / 'compendium.po'
    output_file = tmp_path / 'output.po'

    with open(def_file, 'wb') as file:
        catalog = Catalog(locale='fr', charset='iso-8859-1')
        catalog.add('tea', string='thé')
        catalog.add('coffee')
        pofile.write_po(file, catalog)
    with open(ref_file, 'wb') as file:
        catalog = Catalog()
        catalog.add('tea')
        catalog.add('coffee')
        pofile.write_po(file, catalog)
    with open(compendium, 'wb') as file:
        catalog = Catalog(locale='fr', charset='iso-8859-1')
        catalog.add('coffee', string='café')
        pofile.write_po(file, catalog)

    merge_cmd.input_files = [str(def_file), str(ref_file)]
    merge_cmd.output_file = str(output_file)
    merge_cmd.compendium = [str(compendium)]
    merge_cmd.no_fuzzy_matching = True
    merge_cmd.finalize_options()
    merge_cmd.run()

    with open(output_file, 'rb') as file:
        catalog = pofile.read_po(file)
    assert catalog['tea'].string == 'thé'
    assert catalog['coffee'].string == 'café'
