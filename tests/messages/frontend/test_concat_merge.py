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
from datetime import datetime

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
