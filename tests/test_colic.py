#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2020 Bitergia
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
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Valerio Cosentino <valcos@bitergia.com>
#     inishchith <inishchith@gmail.com>
#

import os
import unittest.mock

from graal.graal import (GraalCommandArgumentParser,
                         GraalError)
from graal.backends.core.analyzers.nomos import Nomos
from graal.backends.core.analyzers.scancode import ScanCode
from graal.backends.core.colic import (CATEGORY_COLIC_NOMOS,
                                       CATEGORY_COLIC_SCANCODE,
                                       CATEGORY_COLIC_SCANCODE_CLI,
                                       NOMOS,
                                       SCANCODE,
                                       SCANCODE_CLI,
                                       CoLic,
                                       LicenseAnalyzer,
                                       CoLicCommand)
from perceval.utils import DEFAULT_DATETIME
from base_analyzer import (ANALYZER_TEST_FILE,
                           TestCaseAnalyzer)
from base_repo import TestCaseRepo
from utils import NOMOS_PATH, SCANCODE_PATH, SCANCODE_CLI_PATH


class TestCoLicBackend(TestCaseRepo):
    """CoLic backend tests"""

    def test_initialization(self):
        """Test whether attributes are initializated"""

        cl = CoLic('http://example.com', self.git_path, self.worktree_path, exec_path=NOMOS_PATH, tag='test')
        self.assertEqual(cl.uri, 'http://example.com')
        self.assertEqual(cl.gitpath, self.git_path)
        self.assertEqual(cl.worktreepath, os.path.join(self.worktree_path, os.path.split(cl.gitpath)[1]))
        self.assertEqual(cl.origin, 'http://example.com')
        self.assertEqual(cl.tag, 'test')
        self.assertEqual(cl.exec_path, NOMOS_PATH)
        self.assertIsNone(cl.analyzer)
        self.assertIsNone(cl.analyzer_kind)

        cl = CoLic('http://example.com', self.git_path, self.worktree_path, exec_path=NOMOS_PATH, tag='test')
        self.assertEqual(cl.uri, 'http://example.com')
        self.assertEqual(cl.gitpath, self.git_path)
        self.assertEqual(cl.worktreepath, os.path.join(self.worktree_path, os.path.split(cl.gitpath)[1]))
        self.assertEqual(cl.origin, 'http://example.com')
        self.assertEqual(cl.tag, 'test')
        self.assertEqual(cl.exec_path, NOMOS_PATH)
        self.assertIsNone(cl.analyzer)
        self.assertIsNone(cl.analyzer_kind)

        # When tag is empty or None it will be set to the value in uri
        cl = CoLic('http://example.com', self.git_path, self.worktree_path, exec_path=NOMOS_PATH)
        self.assertEqual(cl.origin, 'http://example.com')
        self.assertEqual(cl.tag, 'http://example.com')
        self.assertEqual(cl.exec_path, NOMOS_PATH)
        self.assertIsNone(cl.analyzer)
        self.assertIsNone(cl.analyzer_kind)

        cl = CoLic('http://example.com', self.git_path, self.worktree_path, exec_path=NOMOS_PATH)
        self.assertEqual(cl.origin, 'http://example.com')
        self.assertEqual(cl.tag, 'http://example.com')
        self.assertEqual(cl.exec_path, NOMOS_PATH)
        self.assertIsNone(cl.analyzer)
        self.assertIsNone(cl.analyzer_kind)

        with self.assertRaises(GraalError):
            _ = CoLic('http://example.com', self.git_path, worktreepath=self.worktree_path, exec_path="/tmp/invalid")

    def test_fetch_nomossa(self):
        """Test whether commits are properly processed"""

        cl = CoLic('http://example.com', self.git_path, self.worktree_path, exec_path=NOMOS_PATH,
                   in_paths=['perceval/backends/core/github.py'])
        commits = [commit for commit in cl.fetch(category=CATEGORY_COLIC_NOMOS)]

        self.assertEqual(len(commits), 1)
        self.assertFalse(os.path.exists(cl.worktreepath))

        commit = commits[0]
        self.assertEqual(commit['backend_name'], 'CoLic')
        self.assertEqual(commit['category'], CATEGORY_COLIC_NOMOS)
        self.assertEqual(commit['data']['analysis'][0]['file_path'],
                         'perceval/backends/core/github.py')
        self.assertTrue('Author' in commit['data'])
        self.assertTrue('Commit' in commit['data'])
        self.assertFalse('files' in commit['data'])
        self.assertFalse('parents' in commit['data'])
        self.assertFalse('refs' in commit['data'])

    def test_fetch_scancode(self):
        """Test whether commits are properly processed"""

        cl = CoLic('http://example.com', self.git_path, self.worktree_path, exec_path=SCANCODE_PATH,
                   in_paths=['perceval/backends/core/github.py'])
        commits = [commit for commit in cl.fetch(category=CATEGORY_COLIC_SCANCODE)]

        self.assertEqual(len(commits), 1)
        self.assertFalse(os.path.exists(cl.worktreepath))

        commit = commits[0]
        self.assertEqual(commit['backend_name'], 'CoLic')
        self.assertEqual(commit['category'], CATEGORY_COLIC_SCANCODE)
        self.assertEqual(commit['data']['analysis'][0]['file_path'],
                         'perceval/backends/core/github.py')
        self.assertTrue('Author' in commit['data'])
        self.assertTrue('Commit' in commit['data'])
        self.assertFalse('files' in commit['data'])
        self.assertFalse('parents' in commit['data'])
        self.assertFalse('refs' in commit['data'])

    def test_fetch_scancode_cli(self):
        """Test whether commits are properly processed"""

        cl = CoLic('http://example.com', self.git_path, self.worktree_path, exec_path=SCANCODE_CLI_PATH,
                   in_paths=['perceval/backends/core/github.py'])
        commits = [commit for commit in cl.fetch(category=CATEGORY_COLIC_SCANCODE_CLI)]

        self.assertEqual(len(commits), 1)
        self.assertFalse(os.path.exists(cl.worktreepath))

        commit = commits[0]
        self.assertEqual(commit['backend_name'], 'CoLic')
        self.assertEqual(commit['category'], CATEGORY_COLIC_SCANCODE_CLI)
        self.assertEqual(commit['data']['analysis'][0]['file_path'],
                         'perceval/backends/core/github.py')
        self.assertTrue('Author' in commit['data'])
        self.assertTrue('Commit' in commit['data'])
        self.assertFalse('files' in commit['data'])
        self.assertFalse('parents' in commit['data'])
        self.assertFalse('refs' in commit['data'])

    def test_fetch_unknown(self):
        """Test whether commits are properly processed"""

        cl = CoLic('http://example.com', self.git_path, self.worktree_path, exec_path=SCANCODE_CLI_PATH,
                   in_paths=['perceval/backends/core/github.py'])

        with self.assertRaises(GraalError):
            _ = cl.fetch(category="unknown")

    def test_fetch_empty_in_paths(self):
        """Test whether all commits are processed when the no `in_paths` are provided"""

        cl = CoLic('http://example.com', self.git_path, self.worktree_path, exec_path=NOMOS_PATH, in_paths=[])
        commits = [commit for commit in cl.fetch(category=CATEGORY_COLIC_NOMOS)]

        self.assertEqual(len(commits), 6)
        for commit in commits:
            self.assertEqual(commit['backend_name'], 'CoLic')
            self.assertEqual(commit['category'], CATEGORY_COLIC_NOMOS)
            self.assertIn('analysis', commit['data'])
            self.assertTrue('Author' in commit['data'])
            self.assertTrue('Commit' in commit['data'])
            self.assertFalse('files' in commit['data'])
            self.assertFalse('parents' in commit['data'])
            self.assertFalse('refs' in commit['data'])

    def test_metadata_category(self):
        """Test metadata_category"""

        item = {
            "Author": "Valerio Cosentino <valcos@bitergia.com>",
            "AuthorDate": "Fri May 18 18:26:48 2018 +0200",
            "Commit": "Valerio Cosentino <valcos@bitergia.com>",
            "CommitDate": "Fri May 18 18:26:48 2018 +0200",
            "analysis": [],
            "analyzer": "scancode",
            "commit": "075f0c6161db5a3b1c8eca45e08b88469bb148b9",
            "message": "[perceval] first commit"
        }
        self.assertEqual(CoLic.metadata_category(item), CATEGORY_COLIC_SCANCODE)

        item = {
            "Author": "Valerio Cosentino <valcos@bitergia.com>",
            "AuthorDate": "Fri May 18 18:26:48 2018 +0200",
            "Commit": "Valerio Cosentino <valcos@bitergia.com>",
            "CommitDate": "Fri May 18 18:26:48 2018 +0200",
            "analysis": [],
            "analyzer": "nomos",
            "commit": "075f0c6161db5a3b1c8eca45e08b88469bb148b9",
            "message": "[perceval] first commit"
        }
        self.assertEqual(CoLic.metadata_category(item), CATEGORY_COLIC_NOMOS)

        item = {
            "Author": "Valerio Cosentino <valcos@bitergia.com>",
            "AuthorDate": "Fri May 18 18:26:48 2018 +0200",
            "Commit": "Valerio Cosentino <valcos@bitergia.com>",
            "CommitDate": "Fri May 18 18:26:48 2018 +0200",
            "analysis": [],
            "analyzer": "scancode_cli",
            "commit": "075f0c6161db5a3b1c8eca45e08b88469bb148b9",
            "message": "[perceval] first commit"
        }
        self.assertEqual(CoLic.metadata_category(item), CATEGORY_COLIC_SCANCODE_CLI)

        item = {
            "Author": "Valerio Cosentino <valcos@bitergia.com>",
            "AuthorDate": "Fri May 18 18:26:48 2018 +0200",
            "Commit": "Valerio Cosentino <valcos@bitergia.com>",
            "CommitDate": "Fri May 18 18:26:48 2018 +0200",
            "analysis": [],
            "analyzer": "unknown",
            "commit": "075f0c6161db5a3b1c8eca45e08b88469bb148b9",
            "message": "[perceval] first commit"
        }
        with self.assertRaises(GraalError):
            _ = CoLic.metadata_category(item)


class TestLicenseAnalyzer(TestCaseAnalyzer):
    """LicenseAnalyzer tests"""

    def test_init(self):
        """Test initialization"""

        license_analyzer = LicenseAnalyzer(NOMOS_PATH)
        self.assertIsInstance(license_analyzer, LicenseAnalyzer)
        self.assertIsInstance(license_analyzer.analyzer, Nomos)

        license_analyzer = LicenseAnalyzer(NOMOS_PATH, NOMOS)
        self.assertIsInstance(license_analyzer, LicenseAnalyzer)
        self.assertIsInstance(license_analyzer.analyzer, Nomos)

        license_analyzer = LicenseAnalyzer(SCANCODE_PATH, SCANCODE)
        self.assertIsInstance(license_analyzer, LicenseAnalyzer)
        self.assertIsInstance(license_analyzer.analyzer, ScanCode)

        license_analyzer = LicenseAnalyzer(SCANCODE_CLI_PATH, SCANCODE_CLI)
        self.assertIsInstance(license_analyzer, LicenseAnalyzer)
        self.assertIsInstance(license_analyzer.analyzer, ScanCode)

        with self.assertRaises(GraalError):
            _ = LicenseAnalyzer("/tmp/analyzer", SCANCODE)

    def test_analyze(self):
        """Test whether the analyze method works"""

        file_path = os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)
        license_analyzer = LicenseAnalyzer(NOMOS_PATH)
        analysis = license_analyzer.analyze(file_path)

        self.assertIn('licenses', analysis)

        file_path = os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)
        license_analyzer = LicenseAnalyzer(SCANCODE_PATH, kind=SCANCODE)
        analysis = license_analyzer.analyze(file_path)

        self.assertIn('licenses', analysis)
        self.assertIn('copyrights', analysis)

        file_paths = [os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)]
        license_analyzer = LicenseAnalyzer(SCANCODE_CLI_PATH, kind=SCANCODE_CLI)
        analysis = license_analyzer.analyze(file_paths)

        self.assertIn('licenses', analysis[0])
        self.assertIn('copyrights', analysis[0])


class TestCoLicCommand(unittest.TestCase):
    """CoLicCommand tests"""

    def test_backend_class(self):
        """Test if the backend class is CoLic"""

        self.assertIs(CoLicCommand.BACKEND, CoLic)

    def test_setup_cmd_parser(self):
        """Test setup_cmd_parser"""

        parser = CoLicCommand.setup_cmd_parser()

        self.assertIsInstance(parser, GraalCommandArgumentParser)
        self.assertEqual(parser._backend, CoLic)

        args = ['http://example.com/',
                '--git-path', '/tmp/gitpath',
                '--tag', 'test',
                '--from-date', '1970-01-01',
                '--exec-path', '/tmp/execpath']

        parsed_args = parser.parse(*args)
        self.assertEqual(parsed_args.uri, 'http://example.com/')
        self.assertEqual(parsed_args.git_path, '/tmp/gitpath')
        self.assertEqual(parsed_args.tag, 'test')
        self.assertEqual(parsed_args.from_date, DEFAULT_DATETIME)
        self.assertEqual(parsed_args.exec_path, '/tmp/execpath')


if __name__ == "__main__":
    unittest.main()
