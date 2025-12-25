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
import time
import unittest
from datetime import datetime

import pytest
from freezegun import freeze_time

from babel import __version__ as VERSION
from babel.dates import format_datetime
from babel.messages import frontend
from babel.messages.frontend import OptionError
from babel.messages.pofile import read_po
from babel.util import LOCALTZ
from tests.messages.consts import TEST_PROJECT_DISTRIBUTION_DATA, data_dir, pot_file, this_dir
from tests.messages.utils import Distribution


class ExtractMessagesTestCase(unittest.TestCase):

    def setUp(self):
        self.olddir = os.getcwd()
        os.chdir(data_dir)

        self.dist = Distribution(TEST_PROJECT_DISTRIBUTION_DATA)
        self.cmd = frontend.ExtractMessages(self.dist)
        self.cmd.initialize_options()

    def tearDown(self):
        if os.path.isfile(pot_file):
            os.unlink(pot_file)

        os.chdir(self.olddir)

    def assert_pot_file_exists(self):
        assert os.path.isfile(pot_file)

    def test_neither_default_nor_custom_keywords(self):
        self.cmd.output_file = 'dummy'
        self.cmd.no_default_keywords = True
        with pytest.raises(OptionError):
            self.cmd.finalize_options()

    def test_no_output_file_specified(self):
        with pytest.raises(OptionError):
            self.cmd.finalize_options()

    def test_both_sort_output_and_sort_by_file(self):
        self.cmd.output_file = 'dummy'
        self.cmd.sort_output = True
        self.cmd.sort_by_file = True
        with pytest.raises(OptionError):
            self.cmd.finalize_options()

    def test_invalid_file_or_dir_input_path(self):
        self.cmd.input_paths = 'nonexistent_path'
        self.cmd.output_file = 'dummy'
        with pytest.raises(OptionError):
            self.cmd.finalize_options()

    def test_input_paths_is_treated_as_list(self):
        self.cmd.input_paths = data_dir
        self.cmd.output_file = pot_file
        self.cmd.finalize_options()
        self.cmd.run()

        with open(pot_file) as f:
            catalog = read_po(f)
        msg = catalog.get('bar')
        assert len(msg.locations) == 1
        assert ('file1.py' in msg.locations[0][0])

    def test_input_paths_handle_spaces_after_comma(self):
        self.cmd.input_paths = f"{this_dir},  {data_dir}"
        self.cmd.output_file = pot_file
        self.cmd.finalize_options()
        assert self.cmd.input_paths == [this_dir, data_dir]

    def test_input_dirs_is_alias_for_input_paths(self):
        self.cmd.input_dirs = this_dir
        self.cmd.output_file = pot_file
        self.cmd.finalize_options()
        # Gets listified in `finalize_options`:
        assert self.cmd.input_paths == [self.cmd.input_dirs]

    def test_input_dirs_is_mutually_exclusive_with_input_paths(self):
        self.cmd.input_dirs = this_dir
        self.cmd.input_paths = this_dir
        self.cmd.output_file = pot_file
        with pytest.raises(OptionError):
            self.cmd.finalize_options()

    @freeze_time("1994-11-11")
    def test_extraction_with_default_mapping(self):
        self.cmd.copyright_holder = 'FooBar, Inc.'
        self.cmd.msgid_bugs_address = 'bugs.address@email.tld'
        self.cmd.output_file = 'project/i18n/temp.pot'
        self.cmd.add_comments = 'TRANSLATOR:,TRANSLATORS:'

        self.cmd.finalize_options()
        self.cmd.run()

        self.assert_pot_file_exists()

        date = format_datetime(datetime(1994, 11, 11, 00, 00), 'yyyy-MM-dd HH:mmZ', tzinfo=LOCALTZ, locale='en')
        expected_content = fr"""# Translations template for TestProject.
# Copyright (C) {time.strftime('%Y')} FooBar, Inc.
# This file is distributed under the same license as the TestProject
# project.
# FIRST AUTHOR <EMAIL@ADDRESS>, {time.strftime('%Y')}.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: TestProject 0.1\n"
"Report-Msgid-Bugs-To: bugs.address@email.tld\n"
"POT-Creation-Date: {date}\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel {VERSION}\n"

#. TRANSLATOR: This will be a translator coment,
#. that will include several lines
#: project/file1.py:8
msgid "bar"
msgstr ""

#: project/file2.py:9
msgid "foobar"
msgid_plural "foobars"
msgstr[0] ""
msgstr[1] ""

#: project/ignored/this_wont_normally_be_here.py:11
msgid "FooBar"
msgid_plural "FooBars"
msgstr[0] ""
msgstr[1] ""

"""
        with open(pot_file) as f:
            actual_content = f.read()
        assert expected_content == actual_content

    @freeze_time("1994-11-11")
    def test_extraction_with_mapping_file(self):
        self.cmd.copyright_holder = 'FooBar, Inc.'
        self.cmd.msgid_bugs_address = 'bugs.address@email.tld'
        self.cmd.mapping_file = 'mapping.cfg'
        self.cmd.output_file = 'project/i18n/temp.pot'
        self.cmd.add_comments = 'TRANSLATOR:,TRANSLATORS:'

        self.cmd.finalize_options()
        self.cmd.run()

        self.assert_pot_file_exists()

        date = format_datetime(datetime(1994, 11, 11, 00, 00), 'yyyy-MM-dd HH:mmZ', tzinfo=LOCALTZ, locale='en')
        expected_content = fr"""# Translations template for TestProject.
# Copyright (C) {time.strftime('%Y')} FooBar, Inc.
# This file is distributed under the same license as the TestProject
# project.
# FIRST AUTHOR <EMAIL@ADDRESS>, {time.strftime('%Y')}.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: TestProject 0.1\n"
"Report-Msgid-Bugs-To: bugs.address@email.tld\n"
"POT-Creation-Date: {date}\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel {VERSION}\n"

#. TRANSLATOR: This will be a translator coment,
#. that will include several lines
#: project/file1.py:8
msgid "bar"
msgstr ""

#: project/file2.py:9
msgid "foobar"
msgid_plural "foobars"
msgstr[0] ""
msgstr[1] ""

"""
        with open(pot_file) as f:
            actual_content = f.read()
        assert expected_content == actual_content

    @freeze_time("1994-11-11")
    def test_extraction_with_mapping_dict(self):
        self.dist.message_extractors = {
            'project': [
                ('**/ignored/**.*', 'ignore', None),
                ('**.py', 'python', None),
            ],
        }
        self.cmd.copyright_holder = 'FooBar, Inc.'
        self.cmd.msgid_bugs_address = 'bugs.address@email.tld'
        self.cmd.output_file = 'project/i18n/temp.pot'
        self.cmd.add_comments = 'TRANSLATOR:,TRANSLATORS:'

        self.cmd.finalize_options()
        self.cmd.run()

        self.assert_pot_file_exists()

        date = format_datetime(datetime(1994, 11, 11, 00, 00), 'yyyy-MM-dd HH:mmZ', tzinfo=LOCALTZ, locale='en')
        expected_content = fr"""# Translations template for TestProject.
# Copyright (C) {time.strftime('%Y')} FooBar, Inc.
# This file is distributed under the same license as the TestProject
# project.
# FIRST AUTHOR <EMAIL@ADDRESS>, {time.strftime('%Y')}.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: TestProject 0.1\n"
"Report-Msgid-Bugs-To: bugs.address@email.tld\n"
"POT-Creation-Date: {date}\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel {VERSION}\n"

#. TRANSLATOR: This will be a translator coment,
#. that will include several lines
#: project/file1.py:8
msgid "bar"
msgstr ""

#: project/file2.py:9
msgid "foobar"
msgid_plural "foobars"
msgstr[0] ""
msgstr[1] ""

"""
        with open(pot_file) as f:
            actual_content = f.read()
        assert expected_content == actual_content

    def test_extraction_add_location_file(self):
        self.dist.message_extractors = {
            'project': [
                ('**/ignored/**.*', 'ignore', None),
                ('**.py', 'python', None),
            ],
        }
        self.cmd.output_file = 'project/i18n/temp.pot'
        self.cmd.add_location = 'file'
        self.cmd.omit_header = True

        self.cmd.finalize_options()
        self.cmd.run()

        self.assert_pot_file_exists()

        expected_content = r"""#: project/file1.py
msgid "bar"
msgstr ""

#: project/file2.py
msgid "foobar"
msgid_plural "foobars"
msgstr[0] ""
msgstr[1] ""

"""
        with open(pot_file) as f:
            actual_content = f.read()
        assert expected_content == actual_content
