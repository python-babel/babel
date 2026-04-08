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
import os
import shutil
import sys
from datetime import datetime
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from babel import __version__ as VERSION
from babel.dates import format_datetime
from babel.messages import Catalog, frontend, pofile
from babel.messages.frontend import OptionError
from babel.util import LOCALTZ
from tests.messages.consts import TEST_PROJECT_DISTRIBUTION_DATA, data_dir, i18n_dir
from tests.messages.utils import Distribution


@pytest.fixture(autouse=True)
def frozen_time():
    with freeze_time("1994-11-11"):
        yield


class TestConcatanateCatalog:

    def setup_method(self):
        self.olddir = os.getcwd()
        os.chdir(data_dir)

        self.dist = Distribution(TEST_PROJECT_DISTRIBUTION_DATA)
        self.cmd = frontend.ConcatenateCatalog(self.dist)
        self.cmd.initialize_options()

        self.temp1 = f'{i18n_dir}/msgcat_temp1.po'
        self.temp2 = f'{i18n_dir}/msgcat_temp2.po'
        self.output_file = f'{i18n_dir}/msgcat.po'

        with open(self.temp1, 'wb') as file:
            catalog = Catalog()
            catalog.add('other1', string='Other 1', locations=[('simple.py', 1)], flags=['flag1000'])
            catalog.add('other2', string='Other 2',  locations=[('simple.py', 10)])
            catalog.add('same', string='Same', locations=[('simple.py', 100)], flags=['flag1', 'flag1.2'])
            catalog.add('almost_same', string='Almost same', locations=[('simple.py', 1000)], flags=['flag2'])
            catalog.add(('plural', 'plurals'), string=('Plural', 'Plurals'), locations=[('simple.py', 2000)])
            pofile.write_po(file, catalog)

        with open(self.temp2, 'wb') as file:
            catalog = Catalog()
            catalog.add('other3', string='Other 3', locations=[('hard.py', 1)])
            catalog.add('other4', string='Other 4', locations=[('hard.py', 10)])
            catalog.add('almost_same', string='A bit same',  locations=[('hard.py', 1000)], flags=['flag3'])
            catalog.add('same', string='Same', locations=[('hard.py', 100)], flags=['flag4'])
            catalog.add(('plural', 'plurals'), string=('Plural', 'Plurals other'), locations=[('hard.py', 2000)])
            pofile.write_po(file, catalog)

    def teardown_method(self):
        for file in [self.temp1, self.temp2, self.output_file]:
            if os.path.isfile(file):
                    os.unlink(file)

    def _get_expected(self, messages, fuzzy=False):
        date = format_datetime(datetime(1994, 11, 11, 00, 00), 'yyyy-MM-dd HH:mmZ', tzinfo=LOCALTZ, locale='en')
        fuzzy_header = '\n#, fuzzy' if fuzzy else ''
        return (
            "# Translations template for PROJECT.\n"
            "# Copyright (C) 1994 ORGANIZATION\n"
            "# This file is distributed under the same license as the PROJECT project.\n"
            "# FIRST AUTHOR <EMAIL@ADDRESS>, 1994.\n"
            "#" + fuzzy_header + "\n"
            'msgid ""\n'
            'msgstr ""\n'
            '"Project-Id-Version: PROJECT VERSION\\n"\n'
            '"Report-Msgid-Bugs-To: EMAIL@ADDRESS\\n"\n'
            f'"POT-Creation-Date: {date}\\n"\n'
            '"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"\n'
            '"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"\n'
            '"Language-Team: LANGUAGE <LL@li.org>\\n"\n'
            '"MIME-Version: 1.0\\n"\n'
            '"Content-Type: text/plain; charset=utf-8\\n"\n'
            '"Content-Transfer-Encoding: 8bit\\n"\n'
            f'"Generated-By: Babel {VERSION}\\n"\n'
            "\n"
        ) + messages

    def test_no_input_files(self):
        with pytest.raises(OptionError):
            self.cmd.finalize_options()

    def test_no_output_file(self):
        self.cmd.input_files = ['project/i18n/messages.pot']
        self.cmd.finalize_options()  # output_file not required; defaults to stdout

    def test_unique_exclusive_with_less_than(self):
        self.cmd.input_files = [self.temp1, self.temp2]
        self.cmd.unique = True
        self.cmd.less_than = 3
        with pytest.raises(OptionError):
            self.cmd.finalize_options()

    def test_unique_exclusive_with_more_than(self):
        self.cmd.input_files = [self.temp1, self.temp2]
        self.cmd.unique = True
        self.cmd.more_than = 1
        with pytest.raises(OptionError):
            self.cmd.finalize_options()

    def test_default(self):
        self.cmd.input_files = [self.temp1, self.temp2]
        self.cmd.output_file = self.output_file

        self.cmd.finalize_options()
        self.cmd.run()

        expected_content = self._get_expected(fr"""#: simple.py:1
#, flag1000
msgid "other1"
msgstr "Other 1"

#: simple.py:10
msgid "other2"
msgstr "Other 2"

#: hard.py:100 simple.py:100
#, flag1, flag1.2, flag4
msgid "same"
msgstr "Same"

#: hard.py:1000 simple.py:1000
#, flag2, flag3, fuzzy
msgid "almost_same"
msgstr ""
"#-#-#-#-#  msgcat_temp1.po (PROJECT VERSION)  #-#-#-#-#"
"Almost same"
"#-#-#-#-#  msgcat_temp2.po (PROJECT VERSION)  #-#-#-#-#"
"A bit same"

#: hard.py:2000 simple.py:2000
#, fuzzy
msgid "plural"
msgid_plural "plurals"
msgstr ""
"#-#-#-#-#  msgcat_temp1.po (PROJECT VERSION)  #-#-#-#-#"
msgstr[0] "Plural"
msgstr[1] "Plurals"
"#-#-#-#-#  msgcat_temp2.po (PROJECT VERSION)  #-#-#-#-#"
msgstr[0] "Plural"
msgstr[1] "Plurals other"

#: hard.py:1
msgid "other3"
msgstr "Other 3"

#: hard.py:10
msgid "other4"
msgstr "Other 4"

""", fuzzy=True)

        with open(self.output_file, 'r') as f:
            actual_content = f.read()
        assert expected_content == actual_content

    def test_use_first(self):
        self.cmd.input_files = [self.temp1, self.temp2]
        self.cmd.output_file = self.output_file
        self.cmd.use_first = True

        self.cmd.finalize_options()
        self.cmd.run()

        expected_content = self._get_expected(fr"""#: simple.py:1
#, flag1000
msgid "other1"
msgstr "Other 1"

#: simple.py:10
msgid "other2"
msgstr "Other 2"

#: hard.py:100 simple.py:100
#, flag1, flag1.2, flag4
msgid "same"
msgstr "Same"

#: hard.py:1000 simple.py:1000
#, flag2, flag3
msgid "almost_same"
msgstr "Almost same"

#: hard.py:2000 simple.py:2000
msgid "plural"
msgid_plural "plurals"
msgstr[0] "Plural"
msgstr[1] "Plurals"

#: hard.py:1
msgid "other3"
msgstr "Other 3"

#: hard.py:10
msgid "other4"
msgstr "Other 4"

""")

        with open(self.output_file, 'r') as f:
            actual_content = f.read()
        assert expected_content == actual_content

    def test_unique(self):
        self.cmd.input_files = [self.temp1, self.temp2]
        self.cmd.output_file = self.output_file
        self.cmd.unique = True

        self.cmd.finalize_options()
        self.cmd.run()

        expected_content = self._get_expected(fr"""#: simple.py:1
#, flag1000
msgid "other1"
msgstr "Other 1"

#: simple.py:10
msgid "other2"
msgstr "Other 2"

#: hard.py:1
msgid "other3"
msgstr "Other 3"

#: hard.py:10
msgid "other4"
msgstr "Other 4"

""")

        with open(self.output_file, 'r') as f:
                actual_content = f.read()
        assert expected_content == actual_content

        self.cmd.unique = False
        self.cmd.less_than = 2
        self.cmd.finalize_options()
        self.cmd.run()

        with open(self.output_file, 'r') as f:
                actual_content = f.read()
        assert expected_content == actual_content

    def test_more_than(self):
        self.cmd.input_files = [self.temp1, self.temp2]
        self.cmd.output_file = self.output_file
        self.cmd.more_than = 1

        self.cmd.finalize_options()
        self.cmd.run()

        expected_content = self._get_expected(fr"""#: hard.py:100 simple.py:100
#, flag1, flag1.2, flag4
msgid "same"
msgstr "Same"

#: hard.py:1000 simple.py:1000
#, flag2, flag3, fuzzy
msgid "almost_same"
msgstr ""
"#-#-#-#-#  msgcat_temp1.po (PROJECT VERSION)  #-#-#-#-#"
"Almost same"
"#-#-#-#-#  msgcat_temp2.po (PROJECT VERSION)  #-#-#-#-#"
"A bit same"

#: hard.py:2000 simple.py:2000
#, fuzzy
msgid "plural"
msgid_plural "plurals"
msgstr ""
"#-#-#-#-#  msgcat_temp1.po (PROJECT VERSION)  #-#-#-#-#"
msgstr[0] "Plural"
msgstr[1] "Plurals"
"#-#-#-#-#  msgcat_temp2.po (PROJECT VERSION)  #-#-#-#-#"
msgstr[0] "Plural"
msgstr[1] "Plurals other"

""", fuzzy=True)

        with open(self.output_file, 'r') as f:
            actual_content = f.read()
        assert expected_content == actual_content

    def test_no_wrap_width_exclusive(self):
        self.cmd.input_files = [self.temp1]
        self.cmd.no_wrap = True
        self.cmd.width = 80
        with pytest.raises(OptionError):
            self.cmd.finalize_options()

    def _capture_stdout(self):
        buf = io.BytesIO()

        class FakeStdout:
            buffer = buf

        return FakeStdout(), buf

    def test_stdout_output(self):
        self.cmd.input_files = [self.temp1]
        self.cmd.finalize_options()

        fake_stdout, buf = self._capture_stdout()
        with patch('sys.stdout', fake_stdout):
            self.cmd.run()

        content = buf.getvalue().decode('utf-8')
        assert 'msgid "other1"' in content
        assert 'msgstr "Other 1"' in content
        assert 'msgid "same"' in content

    def test_stdout_dash(self):
        self.cmd.input_files = [self.temp1]
        self.cmd.output_file = '-'
        self.cmd.finalize_options()

        fake_stdout, buf = self._capture_stdout()
        with patch('sys.stdout', fake_stdout):
            self.cmd.run()

        content = buf.getvalue().decode('utf-8')
        assert 'msgid "other1"' in content

    def test_same_string_no_conflict(self):
        self.cmd.input_files = [self.temp1, self.temp2]
        self.cmd.output_file = self.output_file
        self.cmd.finalize_options()
        self.cmd.run()

        with open(self.output_file, 'r') as f:
            content = f.read()

        same_block = [line for line in content.split('\n\n') if 'msgid "same"' in line]
        assert same_block
        block = same_block[0]
        assert 'fuzzy' not in block
        assert '#-#-#-#-#' not in block
        assert 'msgstr "Same"' in block

    def test_no_location(self):
        self.cmd.input_files = [self.temp1, self.temp2]
        self.cmd.output_file = self.output_file
        self.cmd.no_location = True
        self.cmd.finalize_options()
        self.cmd.run()

        with open(self.output_file, 'r') as f:
            content = f.read()

        assert '#: ' not in content
        assert 'msgid "other1"' in content

    def test_sort_output(self):
        self.cmd.input_files = [self.temp1, self.temp2]
        self.cmd.output_file = self.output_file
        self.cmd.sort_output = True
        self.cmd.finalize_options()
        self.cmd.run()

        with open(self.output_file, 'r') as f:
            content = f.read()

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

    def test_single_input_file(self):
        self.cmd.input_files = [self.temp1]
        self.cmd.output_file = self.output_file
        self.cmd.finalize_options()
        self.cmd.run()

        with open(self.output_file, 'r') as f:
            content = f.read()

        assert 'msgid "other1"' in content
        assert 'msgid "other2"' in content
        assert 'msgid "same"' in content
        assert '#-#-#-#-#' not in content
        assert 'fuzzy' not in content

    def test_unique_exclusive_with_more_than_nonzero(self):
        self.cmd.input_files = [self.temp1, self.temp2]
        self.cmd.unique = True
        self.cmd.more_than = 0
        self.cmd.finalize_options()

    def test_less_than_equivalent_to_unique(self):
        self.cmd.input_files = [self.temp1, self.temp2]
        self.cmd.output_file = self.output_file
        self.cmd.less_than = 2
        self.cmd.finalize_options()
        self.cmd.run()

        with open(self.output_file, 'r') as f:
            less_than_content = f.read()

        self.cmd.less_than = None
        self.cmd.unique = True
        self.cmd.finalize_options()
        self.cmd.run()

        with open(self.output_file, 'r') as f:
            unique_content = f.read()

        assert less_than_content == unique_content


class TestMergeCatalog:

    def setup_method(self):
        self.olddir = os.getcwd()
        os.chdir(data_dir)

        self.dist = Distribution(TEST_PROJECT_DISTRIBUTION_DATA)
        self.cmd = frontend.MergeCatalog(self.dist)
        self.cmd.initialize_options()

        self.temp_def = f'{i18n_dir}/msgmerge_def.po'
        self.temp_ref = f'{i18n_dir}/msgmerge_ref.pot'
        self.compendium = f'{i18n_dir}/compenidum.po'
        self.output_file = f'{i18n_dir}/msgmerge.po'

        with open(self.temp_ref, 'wb') as file:
            catalog = Catalog()
            for word in ['word1', 'word2', 'word3', 'word4']:
                catalog.add(word)
            pofile.write_po(file, catalog)

        with open(self.temp_def, 'wb') as file:
            catalog = Catalog()
            catalog.add('word1', string='Word 1')
            catalog.add('word2', string='Word 2')
            catalog.add('word3')
            pofile.write_po(file, catalog)

        with open(self.compendium, 'wb') as file:
            catalog = Catalog()
            catalog.add('word1', string='Comp Word 1')
            catalog.add('word2', string='Comp Word 2')
            catalog.add('word4', string='Word 4')
            catalog.add('word5', string='Word 5')
            pofile.write_po(file, catalog)

    def teardown_method(self):
        for file in [
            self.temp_def,
            self.temp_def + '~',
            self.temp_def + '.bac',
            self.temp_ref,
            self.compendium,
            self.output_file
        ]:
            if os.path.exists(file) and os.path.isfile(file):
                    os.unlink(file)

    def _get_expected(self, messages):
        date = format_datetime(datetime(1994, 11, 11, 00, 00), 'yyyy-MM-dd HH:mmZ', tzinfo=LOCALTZ, locale='en')
        return fr"""# Translations template for PROJECT.
# Copyright (C) 1994 ORGANIZATION
# This file is distributed under the same license as the PROJECT project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 1994.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: PROJECT VERSION\n"
"Report-Msgid-Bugs-To: EMAIL@ADDRESS\n"
"POT-Creation-Date: {date}\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel {VERSION}\n"

""" + messages

    def test_no_input_files(self):
        with pytest.raises(OptionError):
            self.cmd.finalize_options()

        with pytest.raises(OptionError):
            self.cmd.input_files = ['1']
            self.cmd.finalize_options()

        with pytest.raises(OptionError):
            self.cmd.input_files = ['1', '2', '3']
            self.cmd.finalize_options()

    def test_no_output_file(self):
        self.cmd.input_files = ['1', '2']
        with pytest.raises(OptionError):
            self.cmd.finalize_options()

        self.cmd.output_file = '2'
        self.cmd.finalize_options()

        self.cmd.output_file = None
        self.cmd.update = True
        self.cmd.finalize_options()

    def test_default(self):
        self.cmd.input_files = [self.temp_def, self.temp_ref]
        self.cmd.output_file = self.output_file
        self.cmd.no_fuzzy_matching = True
        self.cmd.finalize_options()
        self.cmd.run()

        expected_content = self._get_expected(fr"""msgid "word1"
msgstr "Word 1"

msgid "word2"
msgstr "Word 2"

msgid "word3"
msgstr ""

msgid "word4"
msgstr ""

""")

        with open(self.output_file, 'r') as f:
            actual_content = f.read()
        assert expected_content == actual_content

    def test_compenidum(self):
        self.cmd.input_files = [self.temp_def, self.temp_ref]
        self.cmd.output_file = self.output_file
        self.cmd.compendium = [self.compendium,]
        self.cmd.no_fuzzy_matching = True
        self.cmd.no_compendium_comment = True
        self.cmd.finalize_options()
        self.cmd.run()

        expected_content = self._get_expected(fr"""msgid "word1"
msgstr "Word 1"

msgid "word2"
msgstr "Word 2"

msgid "word3"
msgstr ""

msgid "word4"
msgstr "Word 4"

""")

        with open(self.output_file, 'r') as f:
            actual_content = f.read()
        assert expected_content == actual_content

    def test_compenidum_overwrite(self):
        self.cmd.input_files = [self.temp_def, self.temp_ref]
        self.cmd.output_file = self.output_file
        self.cmd.compendium = [self.compendium,]
        self.cmd.no_fuzzy_matching = True
        self.cmd.no_compendium_comment = True
        self.cmd.compendium_overwrite = True
        self.cmd.finalize_options()
        self.cmd.run()

        expected_content = self._get_expected(fr"""msgid "word1"
msgstr "Comp Word 1"

msgid "word2"
msgstr "Comp Word 2"

msgid "word3"
msgstr ""

msgid "word4"
msgstr "Word 4"

#~ msgid "word1"
#~ msgstr "Word 1"

#~ msgid "word2"
#~ msgstr "Word 2"

""")

        with open(self.output_file, 'r') as f:
            actual_content = f.read()
        assert expected_content == actual_content

    def test_update(self):
        self.cmd.input_files = [self.temp_def, self.temp_ref]
        self.cmd.update = True
        self.cmd.no_fuzzy_matching = True
        self.cmd.finalize_options()
        self.cmd.run()

        expected_content = self._get_expected(fr"""msgid "word1"
msgstr "Word 1"

msgid "word2"
msgstr "Word 2"

msgid "word3"
msgstr ""

msgid "word4"
msgstr ""

""")

        with open(self.temp_def, 'r') as f:
            actual_content = f.read()
        assert expected_content == actual_content

    def test_update_backup(self):
        with open(self.temp_def, 'r') as f:
            before_content = f.read()

        self.cmd.input_files = [self.temp_def, self.temp_ref]
        self.cmd.update = True
        self.cmd.backup = True
        self.cmd.no_fuzzy_matching = True
        self.cmd.finalize_options()
        self.cmd.run()

        assert os.path.exists(self.temp_def + '~')
        with open(self.temp_def + '~', 'r') as f:
            actual_content = f.read()
        assert before_content == actual_content

        os.unlink(self.temp_def)
        shutil.move(self.temp_def + '~', self.temp_def)
        self.cmd.suffix = '.bac'
        self.cmd.run()

        assert os.path.exists(self.temp_def + '.bac')
        with open(self.temp_def + '.bac', 'r') as f:
            actual_content = f.read()
        assert before_content == actual_content

    def test_no_wrap_width_exclusive(self):
        self.cmd.input_files = [self.temp_def, self.temp_ref]
        self.cmd.output_file = self.output_file
        self.cmd.no_wrap = True
        self.cmd.width = 80
        with pytest.raises(OptionError):
            self.cmd.finalize_options()

    def test_compendium_with_comment(self):
        self.cmd.input_files = [self.temp_def, self.temp_ref]
        self.cmd.output_file = self.output_file
        self.cmd.compendium = [self.compendium]
        self.cmd.no_fuzzy_matching = True
        self.cmd.finalize_options()
        self.cmd.run()

        with open(self.output_file, 'r') as f:
            content = f.read()

        assert f'#. {self.compendium}' in content
        assert 'msgid "word4"' in content
        assert 'msgstr "Word 4"' in content

    def test_compendium_does_not_overwrite_existing(self):
        self.cmd.input_files = [self.temp_def, self.temp_ref]
        self.cmd.output_file = self.output_file
        self.cmd.compendium = [self.compendium]
        self.cmd.no_fuzzy_matching = True
        self.cmd.no_compendium_comment = True
        self.cmd.finalize_options()
        self.cmd.run()

        with open(self.output_file, 'r') as f:
            content = f.read()

        blocks = content.split('\n\n')
        word1_block = next((b for b in blocks if 'msgid "word1"' in b), None)
        assert word1_block is not None
        assert 'msgstr "Word 1"' in word1_block
        assert 'Comp Word 1' not in word1_block

    def test_multiple_compendiums(self):
        compendium2 = f'{i18n_dir}/compendium2.po'
        try:
            with open(compendium2, 'wb') as f:
                cat = Catalog()
                cat.add('word3', string='Word 3 from comp2')
                pofile.write_po(f, cat)

            self.cmd.input_files = [self.temp_def, self.temp_ref]
            self.cmd.output_file = self.output_file
            self.cmd.compendium = [self.compendium, compendium2]
            self.cmd.no_fuzzy_matching = True
            self.cmd.no_compendium_comment = True
            self.cmd.finalize_options()
            self.cmd.run()

            with open(self.output_file, 'r') as f:
                content = f.read()

            assert 'msgstr "Word 4"' in content
            assert 'msgstr "Word 3 from comp2"' in content
        finally:
            if os.path.exists(compendium2):
                os.unlink(compendium2)

    def test_compendium_fills_empty_translation(self):
        compendium_with_word3 = f'{i18n_dir}/comp_word3.po'
        try:
            with open(compendium_with_word3, 'wb') as f:
                cat = Catalog()
                cat.add('word3', string='Word 3 comp')
                pofile.write_po(f, cat)

            self.cmd.input_files = [self.temp_def, self.temp_ref]
            self.cmd.output_file = self.output_file
            self.cmd.compendium = [compendium_with_word3]
            self.cmd.no_fuzzy_matching = True
            self.cmd.no_compendium_comment = True
            self.cmd.finalize_options()
            self.cmd.run()

            with open(self.output_file, 'r') as f:
                content = f.read()

            assert 'msgstr "Word 3 comp"' in content
        finally:
            if os.path.exists(compendium_with_word3):
                os.unlink(compendium_with_word3)

    def test_obsolete_messages(self):
        self.cmd.input_files = [self.temp_def, self.temp_ref]
        self.cmd.output_file = self.output_file
        self.cmd.no_fuzzy_matching = True
        self.cmd.finalize_options()
        self.cmd.run()

        with open(self.output_file, 'r') as f:
            content = f.read()

        assert '#~ msgid' not in content

        extra_def = f'{i18n_dir}/extra_def.po'
        try:
            with open(extra_def, 'wb') as f:
                cat = Catalog()
                cat.add('word1', string='Word 1')
                cat.add('old_word', string='Old Word')
                pofile.write_po(f, cat)

            self.cmd.input_files = [extra_def, self.temp_ref]
            self.cmd.finalize_options()
            self.cmd.run()

            with open(self.output_file, 'r') as f:
                content = f.read()

            assert '#~ msgid "old_word"' in content
            assert '#~ msgstr "Old Word"' in content
        finally:
            if os.path.exists(extra_def):
                os.unlink(extra_def)

    def test_compendium_not_applied_for_absent_messages(self):
        self.cmd.input_files = [self.temp_def, self.temp_ref]
        self.cmd.output_file = self.output_file
        self.cmd.compendium = [self.compendium]
        self.cmd.no_fuzzy_matching = True
        self.cmd.no_compendium_comment = True
        self.cmd.finalize_options()
        self.cmd.run()

        with open(self.output_file, 'r') as f:
            content = f.read()

        active_blocks = content.split('#~')[0]
        assert 'word5' not in active_blocks
