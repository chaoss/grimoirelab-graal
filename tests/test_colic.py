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

from grimoirelab_toolkit.datetime import str_to_datetime
from graal.graal import (GraalCommandArgumentParser,
                         GraalError)
from graal.backends.core.analyzers.nomos import Nomos
from graal.backends.core.analyzers.scancode import ScanCode
from graal.backends.core.colic import (CATEGORY_COLIC_NOMOS,
                                       CATEGORY_COLIC_SCANCODE,
                                       NOMOS,
                                       SCANCODE,
                                       CoLic,
                                       LicenseAnalyzer,
                                       CoLicCommand)
from test_graal import TestCaseGraal
from base_analyzer import (ANALYZER_TEST_FILE,
                           TestCaseAnalyzer)


NOMOS_PATH = "/home/slimbook/Escritorio/sources/graal-libs/nomossa"
SCANCODE_PATH = "/home/slimbook/Escritorio/sources/graal-libs/scancode-toolkit-2.9.2/scancode"


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

        cl = CoLic('http://example.com', self.git_path, NOMOS_PATH, self.worktree_path, tag='test')
        self.assertEqual(cl.uri, 'http://example.com')
        self.assertEqual(cl.gitpath, self.git_path)
        self.assertEqual(cl.worktreepath, os.path.join(self.worktree_path, os.path.split(cl.gitpath)[1]))
        self.assertEqual(cl.origin, 'http://example.com')
        self.assertEqual(cl.tag, 'test')
        self.assertEqual(cl.exec_path, NOMOS_PATH)
        self.assertIsNone(cl.analyzer)
        self.assertIsNone(cl.analyzer_kind)

        cl = CoLic('http://example.com', self.git_path, NOMOS_PATH, self.worktree_path, tag='test')
        self.assertEqual(cl.uri, 'http://example.com')
        self.assertEqual(cl.gitpath, self.git_path)
        self.assertEqual(cl.worktreepath, os.path.join(self.worktree_path, os.path.split(cl.gitpath)[1]))
        self.assertEqual(cl.origin, 'http://example.com')
        self.assertEqual(cl.tag, 'test')
        self.assertEqual(cl.exec_path, NOMOS_PATH)
        self.assertIsNone(cl.analyzer)
        self.assertIsNone(cl.analyzer_kind)

        # When tag is empty or None it will be set to the value in uri
        cl = CoLic('http://example.com', self.git_path, NOMOS_PATH, self.worktree_path)
        self.assertEqual(cl.origin, 'http://example.com')
        self.assertEqual(cl.tag, 'http://example.com')
        self.assertEqual(cl.exec_path, NOMOS_PATH)
        self.assertIsNone(cl.analyzer)
        self.assertIsNone(cl.analyzer_kind)

        cl = CoLic('http://example.com', self.git_path, NOMOS_PATH, self.worktree_path)
        self.assertEqual(cl.origin, 'http://example.com')
        self.assertEqual(cl.tag, 'http://example.com')
        self.assertEqual(cl.exec_path, NOMOS_PATH)
        self.assertIsNone(cl.analyzer)
        self.assertIsNone(cl.analyzer_kind)

        with self.assertRaises(GraalError):
            _ = CoLic('http://example.com', self.git_path, "/tmp/invalid", worktreepath=self.worktree_path)

    def test_fetch_nomossa(self):
        """Test whether commits are properly processed"""

        cl = CoLic('http://example.com', self.git_path, NOMOS_PATH, self.worktree_path,
                   in_paths=['perceval/backends/core/github.py'])
        commits = [commit for commit in cl.fetch()]

        self.assertEqual(len(commits), 1)
        self.assertFalse(os.path.exists(cl.worktreepath))

        for commit in commits:
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

        cl = CoLic('http://example.com', self.git_path, SCANCODE_PATH, self.worktree_path,
                   in_paths=['perceval/backends/core/github.py'])
        commits = [commit for commit in cl.fetch(category=CATEGORY_COLIC_SCANCODE)]

        self.assertEqual(len(commits), 1)
        self.assertFalse(os.path.exists(cl.worktreepath))

        for commit in commits:
            self.assertEqual(commit['backend_name'], 'CoLic')
            self.assertEqual(commit['category'], CATEGORY_COLIC_SCANCODE)
            self.assertEqual(commit['data']['analysis'][0]['file_path'],
                             'perceval/backends/core/github.py')
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


class TestCoLicCommand(unittest.TestCase):
    """CoLicCommand tests"""

    def test_backend_class(self):
        """Test if the backend class is CoLic"""

        self.assertIs(CoLicCommand.BACKEND, CoLic)

    def test_setup_cmd_parser(self):
        """Test setup_cmd_parser"""

        parser = CoLicCommand.setup_cmd_parser()

        self.assertIsInstance(parser, GraalCommandArgumentParser)

        args = ['http://example.com/',
                '--git-path', '/tmp/gitpath',
                '--tag', 'test',
                '--from-date', '1975-01-01',
                '--exec-path', '/tmp/execpath']

        parsed_args = parser.parse(*args)
        self.assertEqual(parsed_args.uri, 'http://example.com/')
        self.assertEqual(parsed_args.git_path, '/tmp/gitpath')
        self.assertEqual(parsed_args.tag, 'test')
        self.assertEqual(parsed_args.from_date, str_to_datetime('1975-01-01'))
        self.assertEqual(parsed_args.exec_path, '/tmp/execpath')


if __name__ == "__main__":
    unittest.main()
