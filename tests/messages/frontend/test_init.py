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
import unittest
from datetime import datetime

import pytest
from freezegun import freeze_time

from babel import __version__ as VERSION
from babel.dates import format_datetime
from babel.messages import frontend
from babel.util import LOCALTZ
from tests.messages.consts import (
    TEST_PROJECT_DISTRIBUTION_DATA,
    data_dir,
    get_po_file_path,
    i18n_dir,
)
from tests.messages.utils import Distribution


class InitCatalogTestCase(unittest.TestCase):

    def setUp(self):
        self.olddir = os.getcwd()
        os.chdir(data_dir)

        self.dist = Distribution(TEST_PROJECT_DISTRIBUTION_DATA)
        self.cmd = frontend.InitCatalog(self.dist)
        self.cmd.initialize_options()

    def tearDown(self):
        for dirname in ['en_US', 'ja_JP', 'lv_LV']:
            locale_dir = os.path.join(i18n_dir, dirname)
            if os.path.isdir(locale_dir):
                shutil.rmtree(locale_dir)

        os.chdir(self.olddir)

    def test_no_input_file(self):
        self.cmd.locale = 'en_US'
        self.cmd.output_file = 'dummy'
        with pytest.raises(frontend.OptionError):
            self.cmd.finalize_options()

    def test_no_locale(self):
        self.cmd.input_file = 'dummy'
        self.cmd.output_file = 'dummy'
        with pytest.raises(frontend.OptionError):
            self.cmd.finalize_options()

    @freeze_time("1994-11-11")
    def test_with_output_dir(self):
        self.cmd.input_file = 'project/i18n/messages.pot'
        self.cmd.locale = 'en_US'
        self.cmd.output_dir = 'project/i18n'

        self.cmd.finalize_options()
        self.cmd.run()

        po_file = get_po_file_path('en_US')
        assert os.path.isfile(po_file)

        date = format_datetime(datetime(1994, 11, 11, 00, 00), 'yyyy-MM-dd HH:mmZ', tzinfo=LOCALTZ, locale='en')
        expected_content = fr"""# English (United States) translations for TestProject.
# Copyright (C) 2007 FooBar, Inc.
# This file is distributed under the same license as the TestProject
# project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2007.
#
msgid ""
msgstr ""
"Project-Id-Version: TestProject 0.1\n"
"Report-Msgid-Bugs-To: bugs.address@email.tld\n"
"POT-Creation-Date: 2007-04-01 15:30+0200\n"
"PO-Revision-Date: {date}\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language: en_US\n"
"Language-Team: en_US <LL@li.org>\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel {VERSION}\n"

#. This will be a translator coment,
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
        with open(po_file) as f:
            actual_content = f.read()
        assert expected_content == actual_content

    @freeze_time("1994-11-11")
    def test_keeps_catalog_non_fuzzy(self):
        self.cmd.input_file = 'project/i18n/messages_non_fuzzy.pot'
        self.cmd.locale = 'en_US'
        self.cmd.output_dir = 'project/i18n'

        self.cmd.finalize_options()
        self.cmd.run()

        po_file = get_po_file_path('en_US')
        assert os.path.isfile(po_file)

        date = format_datetime(datetime(1994, 11, 11, 00, 00), 'yyyy-MM-dd HH:mmZ', tzinfo=LOCALTZ, locale='en')
        expected_content = fr"""# English (United States) translations for TestProject.
# Copyright (C) 2007 FooBar, Inc.
# This file is distributed under the same license as the TestProject
# project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2007.
#
msgid ""
msgstr ""
"Project-Id-Version: TestProject 0.1\n"
"Report-Msgid-Bugs-To: bugs.address@email.tld\n"
"POT-Creation-Date: 2007-04-01 15:30+0200\n"
"PO-Revision-Date: {date}\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language: en_US\n"
"Language-Team: en_US <LL@li.org>\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel {VERSION}\n"

#. This will be a translator coment,
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
        with open(po_file) as f:
            actual_content = f.read()
        assert expected_content == actual_content

    @freeze_time("1994-11-11")
    def test_correct_init_more_than_2_plurals(self):
        self.cmd.input_file = 'project/i18n/messages.pot'
        self.cmd.locale = 'lv_LV'
        self.cmd.output_dir = 'project/i18n'

        self.cmd.finalize_options()
        self.cmd.run()

        po_file = get_po_file_path('lv_LV')
        assert os.path.isfile(po_file)

        date = format_datetime(datetime(1994, 11, 11, 00, 00), 'yyyy-MM-dd HH:mmZ', tzinfo=LOCALTZ, locale='en')
        expected_content = fr"""# Latvian (Latvia) translations for TestProject.
# Copyright (C) 2007 FooBar, Inc.
# This file is distributed under the same license as the TestProject
# project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2007.
#
msgid ""
msgstr ""
"Project-Id-Version: TestProject 0.1\n"
"Report-Msgid-Bugs-To: bugs.address@email.tld\n"
"POT-Creation-Date: 2007-04-01 15:30+0200\n"
"PO-Revision-Date: {date}\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language: lv_LV\n"
"Language-Team: lv_LV <LL@li.org>\n"
"Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n != 0 ? 1 :"
" 2);\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel {VERSION}\n"

#. This will be a translator coment,
#. that will include several lines
#: project/file1.py:8
msgid "bar"
msgstr ""

#: project/file2.py:9
msgid "foobar"
msgid_plural "foobars"
msgstr[0] ""
msgstr[1] ""
msgstr[2] ""

"""
        with open(po_file) as f:
            actual_content = f.read()
        assert expected_content == actual_content

    @freeze_time("1994-11-11")
    def test_correct_init_singular_plural_forms(self):
        self.cmd.input_file = 'project/i18n/messages.pot'
        self.cmd.locale = 'ja_JP'
        self.cmd.output_dir = 'project/i18n'

        self.cmd.finalize_options()
        self.cmd.run()

        po_file = get_po_file_path('ja_JP')
        assert os.path.isfile(po_file)

        date = format_datetime(datetime(1994, 11, 11, 00, 00), 'yyyy-MM-dd HH:mmZ', tzinfo=LOCALTZ, locale='ja_JP')
        expected_content = fr"""# Japanese (Japan) translations for TestProject.
# Copyright (C) 2007 FooBar, Inc.
# This file is distributed under the same license as the TestProject
# project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2007.
#
msgid ""
msgstr ""
"Project-Id-Version: TestProject 0.1\n"
"Report-Msgid-Bugs-To: bugs.address@email.tld\n"
"POT-Creation-Date: 2007-04-01 15:30+0200\n"
"PO-Revision-Date: {date}\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language: ja_JP\n"
"Language-Team: ja_JP <LL@li.org>\n"
"Plural-Forms: nplurals=1; plural=0;\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel {VERSION}\n"

#. This will be a translator coment,
#. that will include several lines
#: project/file1.py:8
msgid "bar"
msgstr ""

#: project/file2.py:9
msgid "foobar"
msgid_plural "foobars"
msgstr[0] ""

"""
        with open(po_file) as f:
            actual_content = f.read()
        assert expected_content == actual_content

    @freeze_time("1994-11-11")
    def test_supports_no_wrap(self):
        self.cmd.input_file = 'project/i18n/long_messages.pot'
        self.cmd.locale = 'en_US'
        self.cmd.output_dir = 'project/i18n'

        long_message = '"' + 'xxxxx ' * 15 + '"'

        with open('project/i18n/messages.pot', 'rb') as f:
            pot_contents = f.read().decode('latin-1')
        pot_with_very_long_line = pot_contents.replace('"bar"', long_message)
        with open(self.cmd.input_file, 'wb') as f:
            f.write(pot_with_very_long_line.encode('latin-1'))
        self.cmd.no_wrap = True

        self.cmd.finalize_options()
        self.cmd.run()

        po_file = get_po_file_path('en_US')
        assert os.path.isfile(po_file)
        date = format_datetime(datetime(1994, 11, 11, 00, 00), 'yyyy-MM-dd HH:mmZ', tzinfo=LOCALTZ, locale='en_US')
        expected_content = fr"""# English (United States) translations for TestProject.
# Copyright (C) 2007 FooBar, Inc.
# This file is distributed under the same license as the TestProject
# project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2007.
#
msgid ""
msgstr ""
"Project-Id-Version: TestProject 0.1\n"
"Report-Msgid-Bugs-To: bugs.address@email.tld\n"
"POT-Creation-Date: 2007-04-01 15:30+0200\n"
"PO-Revision-Date: {date}\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language: en_US\n"
"Language-Team: en_US <LL@li.org>\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel {VERSION}\n"

#. This will be a translator coment,
#. that will include several lines
#: project/file1.py:8
msgid {long_message}
msgstr ""

#: project/file2.py:9
msgid "foobar"
msgid_plural "foobars"
msgstr[0] ""
msgstr[1] ""

"""
        with open(po_file) as f:
            actual_content = f.read()
        assert expected_content == actual_content

    @freeze_time("1994-11-11")
    def test_supports_width(self):
        self.cmd.input_file = 'project/i18n/long_messages.pot'
        self.cmd.locale = 'en_US'
        self.cmd.output_dir = 'project/i18n'

        long_message = '"' + 'xxxxx ' * 15 + '"'

        with open('project/i18n/messages.pot', 'rb') as f:
            pot_contents = f.read().decode('latin-1')
        pot_with_very_long_line = pot_contents.replace('"bar"', long_message)
        with open(self.cmd.input_file, 'wb') as f:
            f.write(pot_with_very_long_line.encode('latin-1'))
        self.cmd.width = 120
        self.cmd.finalize_options()
        self.cmd.run()

        po_file = get_po_file_path('en_US')
        assert os.path.isfile(po_file)
        date = format_datetime(datetime(1994, 11, 11, 00, 00), 'yyyy-MM-dd HH:mmZ', tzinfo=LOCALTZ, locale='en_US')
        expected_content = fr"""# English (United States) translations for TestProject.
# Copyright (C) 2007 FooBar, Inc.
# This file is distributed under the same license as the TestProject
# project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2007.
#
msgid ""
msgstr ""
"Project-Id-Version: TestProject 0.1\n"
"Report-Msgid-Bugs-To: bugs.address@email.tld\n"
"POT-Creation-Date: 2007-04-01 15:30+0200\n"
"PO-Revision-Date: {date}\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language: en_US\n"
"Language-Team: en_US <LL@li.org>\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel {VERSION}\n"

#. This will be a translator coment,
#. that will include several lines
#: project/file1.py:8
msgid {long_message}
msgstr ""

#: project/file2.py:9
msgid "foobar"
msgid_plural "foobars"
msgstr[0] ""
msgstr[1] ""

"""
        with open(po_file) as f:
            actual_content = f.read()
        assert expected_content == actual_content
