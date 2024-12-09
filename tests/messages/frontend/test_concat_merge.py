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
import unittest
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


class ConcatanationMessagesTestCase(unittest.TestCase):

    def setUp(self):
        self.olddir = os.getcwd()
        os.chdir(data_dir)

        self.dist = Distribution(TEST_PROJECT_DISTRIBUTION_DATA)
        self.cmd = frontend.MessageConcatenation(self.dist)
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
            pofile.write_po(file, catalog)

        with open(self.temp2, 'wb') as file:
            catalog = Catalog()
            catalog.add('other3', string='Other 3', locations=[('hard.py', 1)])
            catalog.add('other4', string='Other 4', locations=[('hard.py', 10)])
            catalog.add('almost_same', string='A bit same',  locations=[('hard.py', 1000)], flags=['flag3'])
            catalog.add('same', string='Same', locations=[('hard.py', 100)], flags=['flag4'])
            pofile.write_po(file, catalog)

    def tearDown(self):
        for file in [self.temp1, self.temp2, self.output_file]:
            if os.path.isfile(file):
                    os.unlink(file)

    def test_no_input_files(self):
        with pytest.raises(OptionError):
            self.cmd.finalize_options()

    def test_no_output_file(self):
        self.cmd.input_files = ['project/i18n/messages.pot']
        with pytest.raises(OptionError):
            self.cmd.finalize_options()

    @freeze_time("1994-11-11")
    def test_default(self):
        self.cmd.input_files = [self.temp1, self.temp2]
        self.cmd.output_file = self.output_file

        self.cmd.finalize_options()
        self.cmd.run()

        date = format_datetime(datetime(1994, 11, 11, 00, 00), 'yyyy-MM-dd HH:mmZ', tzinfo=LOCALTZ, locale='en')
        expected_content = fr"""# Translations template for PROJECT.
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

#: simple.py:1
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

#: hard.py:1
msgid "other3"
msgstr "Other 3"

#: hard.py:10
msgid "other4"
msgstr "Other 4"

"""

        with open(self.output_file, 'r') as f:
                actual_content = f.read()
        assert expected_content == actual_content

    @freeze_time("1994-11-11")
    def test_unique(self):
        self.cmd.input_files = [self.temp1, self.temp2]
        self.cmd.output_file = self.output_file
        self.cmd.unique = True

        self.cmd.finalize_options()
        self.cmd.run()

        date = format_datetime(datetime(1994, 11, 11, 00, 00), 'yyyy-MM-dd HH:mmZ', tzinfo=LOCALTZ, locale='en')
        expected_content = fr"""# Translations template for PROJECT.
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

#: simple.py:1
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

"""

        with open(self.output_file, 'r') as f:
                actual_content = f.read()
        assert expected_content == actual_content

        self.cmd.less_than = 2
        self.cmd.finalize_options()
        self.cmd.run()

        with open(self.output_file, 'r') as f:
                actual_content = f.read()
        assert expected_content == actual_content

    @freeze_time("1994-11-11")
    def test_more_than(self):
        self.cmd.input_files = [self.temp1, self.temp2]
        self.cmd.output_file = self.output_file
        self.cmd.more_than = 1

        self.cmd.finalize_options()
        self.cmd.run()

        date = format_datetime(datetime(1994, 11, 11, 00, 00), 'yyyy-MM-dd HH:mmZ', tzinfo=LOCALTZ, locale='en')
        expected_content = fr"""# Translations template for PROJECT.
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

#: hard.py:100 simple.py:100
#, flag1, flag1.2, flag4
msgid "same"
msgstr "Same"

#: hard.py:1000 simple.py:1000
#, flag2, flag3
msgid "almost_same"
msgstr "Almost same"

"""

        with open(self.output_file, 'r') as f:
                actual_content = f.read()
        assert expected_content == actual_content
