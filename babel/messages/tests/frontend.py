# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

import doctest
import unittest
import os
import subprocess

from babel.messages import frontend
from babel import __version__ as VERSION
import time

class TestDistutilsSetuptoolsFrontend(unittest.TestCase):
    
    def setUp(self):
        self.olddir = os.getcwd()
        self.datadir = os.path.join(os.path.dirname(__file__), 'data')
        os.chdir(self.datadir)
        # Do we need to run egg_info?
        if not os.path.exists(os.path.join(self.datadir,
                                           'TestProject.egg-info')):
            subprocess.call(['./setup.py', 'egg_info'])
    
    def test_extracted_pot_no_mapping(self):
        subprocess.call([os.path.join(self.datadir, 'setup.py'),
                         'extract_messages'])
        self.assertEqual(open(os.path.join(self.datadir, 'project', 'i18n',
                                           'project.pot'), 'r').read(), \
r"""# Translations template for TestProject.
# Copyright (C) %(year)s FooBar, TM
# This file is distributed under the same license as the TestProject
# project.
# FIRST AUTHOR <EMAIL@ADDRESS>, %(year)s.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: TestProject 0.1\n"
"Report-Msgid-Bugs-To: bugs.address@email.tld\n"
"POT-Creation-Date: %(date)s\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel %(version)s\n"

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

#: project/CVS/this_wont_normally_be_here.py:11
msgid "FooBar"
msgid_plural "FooBars"
msgstr[0] ""
msgstr[1] ""

""" % {'version': VERSION,
       'year': time.strftime('%Y'),
       'date': time.strftime('%Y-%m-%d %H:%M%z')})
        
    def test_extracted_pot_with_mapping(self):
        subprocess.call([os.path.join(self.datadir, 'setup.py'),
                         'extract_messages', '-F',
                         os.path.join(self.datadir, 'mapping.cfg')])
        self.assertEqual(open(os.path.join(self.datadir, 'project', 'i18n',
                                           'project.pot'), 'r').read(),
r"""# Translations template for TestProject.
# Copyright (C) %(year)s FooBar, TM
# This file is distributed under the same license as the TestProject
# project.
# FIRST AUTHOR <EMAIL@ADDRESS>, %(year)s.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: TestProject 0.1\n"
"Report-Msgid-Bugs-To: bugs.address@email.tld\n"
"POT-Creation-Date: %(date)s\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel %(version)s\n"

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

""" % {'version': VERSION,
       'year': time.strftime('%Y'),
       'date': time.strftime('%Y-%m-%d %H:%M%z')})                                           
        
    def tearDown(self):
        os.chdir(self.olddir)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(frontend))
    suite.addTest(unittest.makeSuite(TestDistutilsSetuptoolsFrontend))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
