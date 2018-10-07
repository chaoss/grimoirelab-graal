#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2018 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1335, USA.
#
# Authors:
#     Valerio Cosentino <valcos@bitergia.com>
#

import os
import shutil
import subprocess
import tempfile
import unittest.mock

from graal.backends.core.analyzers.nomos import Nomos
from graal.backends.core.colic import (CATEGORY_COLIC,
                                       CoLic,
                                       LicenseAnalyzer,
                                       CoLicCommand)
from test_graal import TestCaseGraal
from base_analyzer import (ANALYZER_TEST_FILE,
                           TestCaseAnalyzer)


class TestCoLicBackend(TestCaseGraal):
    """CoLic backend tests"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_path = tempfile.mkdtemp(prefix='colic_')
        cls.tmp_repo_path = os.path.join(cls.tmp_path, 'repos')
        os.mkdir(cls.tmp_repo_path)

        cls.git_path = os.path.join(cls.tmp_path, 'graaltest')
        cls.worktree_path = os.path.join(cls.tmp_path, 'colic_worktrees')

        data_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(data_path, 'data')

        repo_name = 'graaltest'
        repo_path = cls.git_path

        fdout, _ = tempfile.mkstemp(dir=cls.tmp_path)

        zip_path = os.path.join(data_path, repo_name + '.zip')
        subprocess.check_call(['unzip', '-qq', zip_path, '-d', cls.tmp_repo_path])

        origin_path = os.path.join(cls.tmp_repo_path, repo_name)
        subprocess.check_call(['git', 'clone', '-q', '--bare', origin_path, repo_path],
                              stderr=fdout)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)

    def test_initialization(self):
        """Test whether attributes are initializated"""

        cl = CoLic('http://example.com', self.git_path, self.worktree_path, tag='test')
        self.assertEqual(cl.uri, 'http://example.com')
        self.assertEqual(cl.gitpath, self.git_path)
        self.assertEqual(cl.worktreepath, os.path.join(self.worktree_path, os.path.split(cl.gitpath)[1]))
        self.assertEqual(cl.origin, 'http://example.com')
        self.assertEqual(cl.tag, 'test')
        self.assertIsInstance(cl.license_analyzer, LicenseAnalyzer)

        cl = CoLic('http://example.com', self.git_path, self.worktree_path, tag='test')
        self.assertEqual(cl.uri, 'http://example.com')
        self.assertEqual(cl.gitpath, self.git_path)
        self.assertEqual(cl.worktreepath, os.path.join(self.worktree_path, os.path.split(cl.gitpath)[1]))
        self.assertEqual(cl.origin, 'http://example.com')
        self.assertEqual(cl.tag, 'test')
        self.assertIsInstance(cl.license_analyzer, LicenseAnalyzer)

        # When tag is empty or None it will be set to the value in uri
        cl = CoLic('http://example.com', self.git_path, self.worktree_path)
        self.assertEqual(cl.origin, 'http://example.com')
        self.assertEqual(cl.tag, 'http://example.com')

        cl = CoLic('http://example.com', self.git_path, self.worktree_path)
        self.assertEqual(cl.origin, 'http://example.com')
        self.assertEqual(cl.tag, 'http://example.com')

    def test_fetch(self):
        """Test whether commits are properly processed"""

        cl = CoLic('http://example.com', self.git_path, self.worktree_path, in_paths=['perceval/backends/core/github.py'])
        commits = [commit for commit in cl.fetch()]

        self.assertEqual(len(commits), 1)
        self.assertFalse(os.path.exists(cl.worktreepath))

        for commit in commits:
            self.assertEqual(commit['backend_name'], 'CoLic')
            self.assertEqual(commit['category'], CATEGORY_COLIC)
            self.assertEqual(commit['data']['analysis'][0]['file_path'],
                             'perceval/backends/core/github.py')
            self.assertTrue('Author' in commit['data'])
            self.assertTrue('Commit' in commit['data'])
            self.assertFalse('files' in commit['data'])
            self.assertFalse('parents' in commit['data'])
            self.assertFalse('refs' in commit['data'])


class TestLicenseAnalyzer(TestCaseAnalyzer):
    """LicenseAnalyzer tests"""

    def test_init(self):
        """Test initialization"""

        license_analyzer = LicenseAnalyzer()

        self.assertIsInstance(license_analyzer, LicenseAnalyzer)
        self.assertIsInstance(license_analyzer.nomos, Nomos)

    def test_analyze(self):
        """Test whether the analyze method works"""

        file_path = os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)
        license_analyzer = LicenseAnalyzer()
        analysis = license_analyzer.analyze(file_path)

        self.assertIn('licenses', analysis)


class TestCoLicCommand(unittest.TestCase):
    """CoLicCommand tests"""

    def test_backend_class(self):
        """Test if the backend class is CoLic"""

        self.assertIs(CoLicCommand.BACKEND, CoLic)


if __name__ == "__main__":
    unittest.main()
