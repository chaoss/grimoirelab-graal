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
import shutil
import subprocess
import tempfile
import unittest.mock

from graal.graal import GraalCommandArgumentParser
from graal.backends.core.analyzers.pylint import PyLint
from graal.backends.core.analyzers.flake8 import Flake8
from graal.backends.core.analyzers.jadolint import Jadolint, SMELLS
from graal.backends.core.coqua import (CATEGORY_COQUA_PYLINT,
                                       CATEGORY_COQUA_FLAKE8,
                                       CATEGORY_COQUA_JADOLINT,
                                       FLAKE8,
                                       CoQua,
                                       JadolintAnalyzer,
                                       ModuleAnalyzer,
                                       CoQuaCommand,
                                       logger)
from perceval.utils import DEFAULT_DATETIME
from graal.graal import GraalError
from base_analyzer import (TestCaseAnalyzer,
                           ANALYZER_TEST_FOLDER,
                           DOCKERFILE_TEST,
                           get_file_path)
from base_repo import TestCaseRepo
from utils import JADOLINT_PATH


class TestCoQuaBackend(TestCaseRepo):
    """CoQua backend tests"""

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

    def test_fetch_pylint(self):
        """Test whether commits are properly processed"""

        cq = CoQua('http://example.com', self.git_path,
                   self.worktree_path, entrypoint="perceval")
        commits = [commit for commit in cq.fetch()]

        self.assertEqual(len(commits), 6)
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

        self.assertEqual(len(commits), 6)
        self.assertFalse(os.path.exists(cq.worktreepath))

        commit = commits[0]
        self.assertEqual(commit['backend_name'], 'CoQua')
        self.assertEqual(commit['category'], CATEGORY_COQUA_FLAKE8)
        result = commit['data']['analysis']
        self.assertIn('warnings', result)
        self.assertTrue(type(result['warnings']), int)
        self.assertNotIn('lines', result)

    def test_fetch_error(self):
        """Test whether an exception is thrown when the module isn't defined and the category is pylint or flake8"""

        cq = CoQua('http://example.com', self.git_path, self.worktree_path, tag='test')
        with self.assertRaises(GraalError):
            _ = [item for item in cq.fetch(category=CATEGORY_COQUA_PYLINT)]

        with self.assertRaises(GraalError):
            _ = [item for item in cq.fetch(category=CATEGORY_COQUA_FLAKE8)]

    def test_fetch_unknown(self):
        """Test whether commits are properly processed"""

        cq = CoQua('http://example.com', self.git_path,
                   self.worktree_path, entrypoint="perceval")

        with self.assertRaises(GraalError):
            _ = cq.fetch(category="unknown")

    def test_fetch_module_not_found(self):
        """Test whether a warning is thrown when the module is not found"""

        cq = CoQua('http://example.com', self.git_path,
                   self.worktree_path, entrypoint="unknown")

        with self.assertLogs(logger, level='WARNING') as cm:
            _ = [item for item in cq.fetch(category=CATEGORY_COQUA_PYLINT)]

            self.assertRegex(cm.output[0], '.*does not exist at commit.*')

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


class TestCoQuaJadolintBackend(TestCaseRepo):
    """CoQua backend tests for Jadolint"""

    repo_name = 'graaltest-dockerfile'

    def setUp(self):
        super().setUp()

    def test_initialization(self):
        """Test whether attributes are initializated"""

        cq = CoQua('http://example.com', self.git_path, self.worktree_path, exec_path=JADOLINT_PATH, tag='test')
        self.assertEqual(cq.uri, 'http://example.com')
        self.assertEqual(cq.gitpath, self.git_path)
        self.assertEqual(cq.worktreepath, os.path.join(self.worktree_path, os.path.split(cq.gitpath)[1]))
        self.assertEqual(cq.origin, 'http://example.com')
        self.assertEqual(cq.tag, 'test')
        self.assertEqual(cq.exec_path, JADOLINT_PATH)

    def test_fetch(self):
        """Test whether commits are properly processed"""

        cq = CoQua('http://example.com', self.git_path, self.worktree_path,
                   exec_path=JADOLINT_PATH, in_paths=['Dockerfile'])
        commits = [commit for commit in cq.fetch(category=CATEGORY_COQUA_JADOLINT)]

        self.assertEqual(len(commits), 2)

        analysis = commits[0]['data']['analysis']
        self.assertIn('Dockerfile', analysis)
        expected_smells = [
            '/Dockerfile 5 DL4000 MAINTAINER is deprecated',
            '/Dockerfile 5 DL4000 MAINTAINER is deprecated',
            '/Dockerfile 5 DL4000 MAINTAINER is deprecated',
            '/Dockerfile 5 DL4000 MAINTAINER is deprecated',
            '/Dockerfile 5 DL4000 MAINTAINER is deprecated',
            '/Dockerfile 13 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 16 DL3008 Pin versions in apt-get install',
            '/Dockerfile 16 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 16 DL3014 Use the -y switch',
            '/Dockerfile 16 DL3015 Avoid additional packages by specifying --no-install-recommends',
            '/Dockerfile 32 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 34 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 34 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 37 DL3020 Use COPY instead of ADD for files and folders',
            '/Dockerfile 38 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 55 DL3000 Use absolute WORKDIR',
            '/Dockerfile 57 DL3025 Use arguments JSON notation for CMD and ENTRYPOINT arguments'
        ]

        analysis['Dockerfile'][SMELLS].sort()
        expected_smells.sort()
        self.assertListEqual(analysis['Dockerfile'][SMELLS], expected_smells)

        analysis = commits[1]['data']['analysis']
        self.assertIn('Dockerfile', analysis)
        expected_smells = [
            '/Dockerfile 5 DL4000 MAINTAINER is deprecated',
            '/Dockerfile 5 DL4000 MAINTAINER is deprecated',
            '/Dockerfile 5 DL4000 MAINTAINER is deprecated',
            '/Dockerfile 5 DL4000 MAINTAINER is deprecated',
            '/Dockerfile 5 DL4000 MAINTAINER is deprecated',
            '/Dockerfile 13 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 16 DL3008 Pin versions in apt-get install',
            '/Dockerfile 16 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 16 DL3014 Use the -y switch',
            '/Dockerfile 16 DL3015 Avoid additional packages by specifying --no-install-recommends',
            '/Dockerfile 33 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 35 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 35 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 38 DL3020 Use COPY instead of ADD for files and folders',
            '/Dockerfile 39 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 41 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 41 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 41 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 41 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 41 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 41 DL3009 Delete the apt-get lists after installing something',
            '/Dockerfile 56 DL3000 Use absolute WORKDIR',
            '/Dockerfile 58 DL3025 Use arguments JSON notation for CMD and ENTRYPOINT arguments'
        ]

        analysis['Dockerfile'][SMELLS].sort()
        expected_smells.sort()
        self.assertListEqual(analysis['Dockerfile'][SMELLS], expected_smells)

    def test_fetch_empty(self):
        """Test whether no commits are returned"""

        cq = CoQua('http://example.com', self.git_path, self.worktree_path,
                   exec_path=JADOLINT_PATH, in_paths=['unknown'])
        commits = [commit for commit in cq.fetch(category=CATEGORY_COQUA_JADOLINT)]
        self.assertEqual(commits, [])

    def test_fetch_error(self):
        """Test whether an exception is thrown when the exec_path isn't defined and the category is jadolint"""

        cq = CoQua('http://example.com', self.git_path, self.worktree_path, entrypoint="module", tag='test')
        with self.assertRaises(GraalError):
            _ = [item for item in cq.fetch(category=CATEGORY_COQUA_JADOLINT)]


class TestJadolintAnalyzer(TestCaseAnalyzer):
    """JadolintAnalyzer tests"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_path = tempfile.mkdtemp(prefix='codep_')

        test_analyzer = get_file_path(ANALYZER_TEST_FOLDER + DOCKERFILE_TEST)
        shutil.copy2(test_analyzer, cls.tmp_path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)

    def test_init(self):
        """Test initialization"""

        smells_analyzer = JadolintAnalyzer(JADOLINT_PATH)

        self.assertIsInstance(smells_analyzer, JadolintAnalyzer)
        self.assertIsInstance(smells_analyzer.analyzer, Jadolint)
        self.assertEqual(smells_analyzer.analyzer.analysis, SMELLS)

    def test_analyze(self):
        """Test whether the analyze method works"""

        file_path = os.path.join(self.tmp_path, DOCKERFILE_TEST)
        smells_analyzer = JadolintAnalyzer(JADOLINT_PATH)
        result = smells_analyzer.analyze(file_path)

        expected = [
            'Dockerfile 5 DL4000 MAINTAINER is deprecated',
            'Dockerfile 5 DL4000 MAINTAINER is deprecated',
            'Dockerfile 5 DL4000 MAINTAINER is deprecated',
            'Dockerfile 5 DL4000 MAINTAINER is deprecated',
            'Dockerfile 5 DL4000 MAINTAINER is deprecated',
            'Dockerfile 13 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 16 DL3008 Pin versions in apt-get install',
            'Dockerfile 16 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 16 DL3014 Use the -y switch',
            'Dockerfile 16 DL3015 Avoid additional packages by specifying --no-install-recommends',
            'Dockerfile 32 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 34 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 34 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 37 DL3020 Use COPY instead of ADD for files and folders',
            'Dockerfile 38 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 55 DL3000 Use absolute WORKDIR',
            'Dockerfile 57 DL3025 Use arguments JSON notation for CMD and ENTRYPOINT arguments'
        ]

        self.assertIn(SMELLS, result)

        for i in range(len(result[SMELLS])):
            self.assertRegex(result[SMELLS][i], expected[i])


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
        self.assertEqual(parser._backend, CoQua)

        args = ['http://example.com/',
                '--git-path', '/tmp/gitpath',
                '--tag', 'test',
                '--from-date', '1970-01-01']

        parsed_args = parser.parse(*args)
        self.assertEqual(parsed_args.uri, 'http://example.com/')
        self.assertEqual(parsed_args.git_path, '/tmp/gitpath')
        self.assertEqual(parsed_args.tag, 'test')
        self.assertEqual(parsed_args.from_date, DEFAULT_DATETIME)

        args = ['http://example.com/',
                '--git-path', '/tmp/gitpath',
                '--tag', 'test',
                '--exec-path', JADOLINT_PATH,
                '--category', CATEGORY_COQUA_JADOLINT,
                '--in-paths', 'Dockerfile', 'Dockerfile-full', 'Dockerfile-secured']

        parsed_args = parser.parse(*args)
        self.assertEqual(parsed_args.uri, 'http://example.com/')
        self.assertEqual(parsed_args.git_path, '/tmp/gitpath')
        self.assertEqual(parsed_args.tag, 'test')
        self.assertEqual(parsed_args.from_date, DEFAULT_DATETIME)
        self.assertEqual(parsed_args.category, CATEGORY_COQUA_JADOLINT),
        self.assertEqual(parsed_args.exec_path, JADOLINT_PATH)
        self.assertListEqual(parsed_args.in_paths, ['Dockerfile', 'Dockerfile-full', 'Dockerfile-secured'])


if __name__ == "__main__":
    unittest.main()
