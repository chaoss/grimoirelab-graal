#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2019 Bitergia
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

from graal.graal import GraalCommandArgumentParser
from graal.backends.core.analyzers.pylint import PyLint
from graal.backends.core.analyzers.flake8 import Flake8
from graal.backends.core.coqua import (CATEGORY_COQUA_PYLINT,
                                       CATEGORY_COQUA_FLAKE8,
                                       FLAKE8,
                                       CoQua,
                                       ModuleAnalyzer,
                                       CoQuaCommand)
from perceval.utils import DEFAULT_DATETIME
from graal.graal import GraalError
from test_graal import TestCaseGraal
from base_analyzer import TestCaseAnalyzer


class TestCoQuaBackend(TestCaseGraal):
    """CoQua backend tests"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_path = tempfile.mkdtemp(prefix='coqua_')
        cls.tmp_repo_path = os.path.join(cls.tmp_path, 'repos')
        os.mkdir(cls.tmp_repo_path)

        cls.git_path = os.path.join(cls.tmp_path, 'graaltest')
        cls.worktree_path = os.path.join(cls.tmp_path, 'coqua_worktrees')

        data_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(data_path, 'data')

        repo_name = 'graaltest'
        repo_path = cls.git_path

        fdout, _ = tempfile.mkstemp(dir=cls.tmp_path)

        zip_path = os.path.join(data_path, repo_name + '.zip')
        subprocess.check_call(
            ['unzip', '-qq', zip_path, '-d', cls.tmp_repo_path])

        origin_path = os.path.join(cls.tmp_repo_path, repo_name)
        subprocess.check_call(['git', 'clone', '-q', '--bare', origin_path, repo_path],
                              stderr=fdout)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)

    def test_initialization(self):
        """Test whether attributes are initializated"""

        cq = CoQua('http://example.com', self.git_path,
                   self.worktree_path, entrypoint="module", tag='test')
        self.assertEqual(cq.uri, 'http://example.com')
        self.assertEqual(cq.gitpath, self.git_path)
        self.assertEqual(cq.worktreepath, os.path.join(
            self.worktree_path, os.path.split(cq.gitpath)[1]))
        self.assertEqual(cq.origin, 'http://example.com')
        self.assertEqual(cq.tag, 'test')
        self.assertEqual(cq.entrypoint, "module")

        with self.assertRaises(GraalError):
            _ = CoQua('http://example.com', self.git_path,
                      self.worktree_path, details=True, tag='test')

    def test_fetch_pylint(self):
        """Test whether commits are properly processed"""

        cq = CoQua('http://example.com', self.git_path,
                   self.worktree_path, entrypoint="perceval")
        commits = [commit for commit in cq.fetch()]

        self.assertEqual(len(commits), 3)
        self.assertFalse(os.path.exists(cq.worktreepath))

        commit = commits[0]
        self.assertEqual(commit['backend_name'], 'CoQua')
        self.assertEqual(commit['category'], CATEGORY_COQUA_PYLINT)
        result = commit['data']['analysis']
        self.assertNotIn('modules', result)
        self.assertIn('quality', result)
        self.assertTrue(type(result['quality']), str)
        self.assertIn('num_modules', result)
        self.assertTrue(type(result['num_modules']), int)
        self.assertIn('warnings', result)
        self.assertTrue(type(result['warnings']), int)

    def test_fetch_flake8(self):
        """Test whether commits are properly processed"""

        cq = CoQua('http://example.com', self.git_path,
                   self.worktree_path, entrypoint="perceval")
        commits = [commit for commit in cq.fetch(
            category=CATEGORY_COQUA_FLAKE8)]

        self.assertEqual(len(commits), 3)
        self.assertFalse(os.path.exists(cq.worktreepath))

        commit = commits[0]
        self.assertEqual(commit['backend_name'], 'CoQua')
        self.assertEqual(commit['category'], CATEGORY_COQUA_FLAKE8)
        result = commit['data']['analysis']
        self.assertIn('warnings', result)
        self.assertTrue(type(result['warnings']), int)
        self.assertNotIn('lines', result)

        cq = CoQua('http://example.com', self.git_path,
                   self.worktree_path, entrypoint="unknown")

    def test_fetch_unknown(self):
        """Test whether commits are properly processed"""

        cq = CoQua('http://example.com', self.git_path,
                   self.worktree_path, entrypoint="perceval")

        with self.assertRaises(GraalError):
            _ = cq.fetch(category="unknown")

    def test_metadata_category(self):
        """Test metadata_category"""
        item = {
            "Author": "Nishchith Shetty <inishchith@gmail.com>",
            "AuthorDate": "Tue Feb 26 22:06:31 2019 +0530",
            "Commit": "Nishchith Shetty <inishchith@gmail.com>",
            "CommitDate": "Tue Feb 26 22:06:31 2019 +0530",
            "analysis": [],
            "analyzer": "pylint",
            "commit": "5866a479587e8b548b0cb2d591f3a3f5dab04443",
            "message": "[copyright] Update copyright dates"
        }
        self.assertEqual(CoQua.metadata_category(item), CATEGORY_COQUA_PYLINT)

        item = {
            "Author": "Nishchith Shetty <inishchith@gmail.com>",
            "AuthorDate": "Tue Feb 26 22:06:31 2019 +0530",
            "Commit": "Nishchith Shetty <inishchith@gmail.com>",
            "CommitDate": "Tue Feb 26 22:06:31 2019 +0530",
            "analysis": [],
            "analyzer": "flake8",
            "commit": "5866a479587e8b548b0cb2d591f3a3f5dab04443",
            "message": "[copyright] Update copyright dates"
        }
        self.assertEqual(CoQua.metadata_category(item), CATEGORY_COQUA_FLAKE8)

        item = {
            "Author": "Nishchith Shetty <inishchith@gmail.com>",
            "AuthorDate": "Tue Feb 26 22:06:31 2019 +0530",
            "Commit": "Nishchith Shetty <inishchith@gmail.com>",
            "CommitDate": "Tue Feb 26 22:06:31 2019 +0530",
            "analysis": [],
            "analyzer": "unknown",
            "commit": "5866a479587e8b548b0cb2d591f3a3f5dab04443",
            "message": "[copyright] Update copyright dates"
        }
        with self.assertRaises(GraalError):
            _ = CoQua.metadata_category(item)


class TestModuleAnalyzer(TestCaseAnalyzer):
    """ModuleAnalyzer tests"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_path = tempfile.mkdtemp(prefix='coqua_')

        data_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(data_path, 'data')

        repo_name = 'graaltest'
        cls.repo_path = os.path.join(cls.tmp_path, repo_name)
        cls.worktree_path = os.path.join(cls.tmp_path, 'coqua_worktrees')

        fdout, _ = tempfile.mkstemp(dir=cls.tmp_path)

        zip_path = os.path.join(data_path, repo_name + '.zip')
        subprocess.check_call(['unzip', '-qq', zip_path, '-d', cls.tmp_path])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)

    def test_init(self):
        """Test initialization"""

        mod_analyzer = ModuleAnalyzer()
        self.assertIsInstance(mod_analyzer, ModuleAnalyzer)
        self.assertIsInstance(mod_analyzer.analyzer, PyLint)

        mod_analyzer = ModuleAnalyzer(kind=FLAKE8)
        self.assertIsInstance(mod_analyzer, ModuleAnalyzer)
        self.assertIsInstance(mod_analyzer.analyzer, Flake8)

    def test_analyze(self):
        """Test whether the analyze method works"""

        module_path = os.path.join(self.tmp_path, 'graaltest', 'perceval')

        mod_analyzer = ModuleAnalyzer()
        result = mod_analyzer.analyze(module_path, self.worktree_path)
        self.assertNotIn('modules', result)
        self.assertIn('quality', result)
        self.assertTrue(type(result['quality']), str)
        self.assertIn('num_modules', result)
        self.assertTrue(type(result['num_modules']), int)
        self.assertIn('warnings', result)
        self.assertTrue(type(result['warnings']), int)

        mod_analyzer = ModuleAnalyzer(kind=FLAKE8)
        result = mod_analyzer.analyze(module_path, self.worktree_path)
        self.assertNotIn('lines', result)
        self.assertIn('warnings', result)
        self.assertTrue(type(result['warnings']), int)


class TestCoDepCommand(unittest.TestCase):
    """CoQuaCommand tests"""

    def test_backend_class(self):
        """Test if the backend class is CoQua"""

        self.assertIs(CoQuaCommand.BACKEND, CoQua)

    def test_setup_cmd_parser(self):
        """Test setup_cmd_parser"""

        parser = CoQuaCommand.setup_cmd_parser()

        self.assertIsInstance(parser, GraalCommandArgumentParser)
        self.assertEqual(parser._categories, CoQua.CATEGORIES)

        args = ['http://example.com/',
                '--git-path', '/tmp/gitpath',
                '--tag', 'test',
                '--from-date', '1970-01-01']

        parsed_args = parser.parse(*args)
        self.assertEqual(parsed_args.uri, 'http://example.com/')
        self.assertEqual(parsed_args.git_path, '/tmp/gitpath')
        self.assertEqual(parsed_args.tag, 'test')
        self.assertEqual(parsed_args.from_date, DEFAULT_DATETIME)


if __name__ == "__main__":
    unittest.main()
