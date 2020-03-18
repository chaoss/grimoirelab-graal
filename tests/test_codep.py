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
from graal.backends.core.analyzers.jadolint import Jadolint, DEPENDENCIES
from graal.backends.core.analyzers.reverse import Reverse
from graal.backends.core.codep import (CATEGORY_CODEP_PYREVERSE,
                                       CATEGORY_CODEP_JADOLINT,
                                       CoDep,
                                       PyreverseAnalyzer,
                                       JadolintAnalyzer,
                                       CoDepCommand,
                                       logger)
from graal.graal import GraalError
from perceval.utils import DEFAULT_DATETIME
from base_analyzer import (TestCaseAnalyzer,
                           ANALYZER_TEST_FOLDER,
                           DOCKERFILE_TEST,
                           get_file_path)
from base_repo import TestCaseRepo
from utils import JADOLINT_PATH


class TestCoDepBackend(TestCaseRepo):
    """CoDep backend tests"""

    def test_fetch_unknown_category(self):
        """Test whether an exception is thrown when the category is unknown"""

        cd = CoDep('http://example.com', self.git_path, self.worktree_path, tag='test')
        with self.assertRaises(GraalError):
            _ = [item for item in cd.fetch(category="unknown")]

    def test_metadata_category(self):
        """Test metadata_category"""
        item = {
            "Author": "Nishchith Shetty <inishchith@gmail.com>",
            "AuthorDate": "Tue Feb 26 22:06:31 2019 +0530",
            "Commit": "Nishchith Shetty <inishchith@gmail.com>",
            "CommitDate": "Tue Feb 26 22:06:31 2019 +0530",
            "analysis": [],
            "analyzer": "pyreverse",
            "commit": "5866a479587e8b548b0cb2d591f3a3f5dab04443",
            "message": "[copyright] Update copyright dates"
        }
        self.assertEqual(CoDep.metadata_category(item), CATEGORY_CODEP_PYREVERSE)

        item = {
            "Author": "Nishchith Shetty <inishchith@gmail.com>",
            "AuthorDate": "Tue Feb 26 22:06:31 2019 +0530",
            "Commit": "Nishchith Shetty <inishchith@gmail.com>",
            "CommitDate": "Tue Feb 26 22:06:31 2019 +0530",
            "analysis": [],
            "analyzer": "jadolint",
            "commit": "5866a479587e8b548b0cb2d591f3a3f5dab04443",
            "message": "[copyright] Update copyright dates"
        }
        self.assertEqual(CoDep.metadata_category(item), CATEGORY_CODEP_JADOLINT)

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
            _ = CoDep.metadata_category(item)


class TestCoDepPyReverseBackend(TestCaseRepo):
    """CoDep backend tests"""

    def test_initialization(self):
        """Test whether attributes are initializated"""

        cd = CoDep('http://example.com', self.git_path, self.worktree_path, entrypoint="module", tag='test')
        self.assertEqual(cd.uri, 'http://example.com')
        self.assertEqual(cd.gitpath, self.git_path)
        self.assertEqual(cd.worktreepath, os.path.join(self.worktree_path, os.path.split(cd.gitpath)[1]))
        self.assertEqual(cd.origin, 'http://example.com')
        self.assertEqual(cd.tag, 'test')
        self.assertEqual(cd.entrypoint, "module")

    def test_fetch(self):
        """Test whether commits are properly processed"""

        cd = CoDep('http://example.com', self.git_path, self.worktree_path, entrypoint="perceval")
        commits = [commit for commit in cd.fetch()]

        self.assertEqual(len(commits), 6)
        self.assertFalse(os.path.exists(cd.worktreepath))

        commit = commits[0]
        self.assertEqual(commit['backend_name'], 'CoDep')
        self.assertEqual(commit['category'], CATEGORY_CODEP_PYREVERSE)
        result = commit['data']['analysis']
        self.assertIn('classes', result)
        self.assertTrue(type(result['classes']), dict)
        self.assertIn('nodes', result['classes'])
        self.assertTrue(type(result['classes']['nodes']), list)
        self.assertIn('links', result['classes'])
        self.assertTrue(type(result['classes']['links']), list)
        self.assertIn('packages', result)
        self.assertTrue(type(result['packages']), dict)
        self.assertTrue(type(result['packages']['nodes']), list)
        self.assertIn('links', result['packages'])
        self.assertTrue(type(result['packages']['links']), list)

    def test_fetch_not_existing_module(self):
        """Test whether warning messages are logged when a module is not found"""

        cd = CoDep('http://example.com', self.git_path, self.worktree_path, entrypoint="unknown")

        with self.assertLogs(logger, level='WARNING') as cm:
            for commit in cd.fetch():
                self.assertRegex(cm.output[-1], 'module path .* does not exist .* analysis will be skipped')
                self.assertEqual(commit['data']['analysis'], {})

    def test_fetch_error(self):
        """Test whether an exception is thrown when the entrypoint isn't defined and the category is pyreverse"""

        cd = CoDep('http://example.com', self.git_path, self.worktree_path, details=True, tag='test')
        with self.assertRaises(GraalError):
            _ = [item for item in cd.fetch()]


class TestCoDepJadolintBackend(TestCaseRepo):
    """CoDep backend tests"""

    repo_name = 'graaltest-dockerfile'

    def setUp(self):
        super().setUp()

    def test_initialization(self):
        """Test whether attributes are initializated"""

        cd = CoDep('http://example.com', self.git_path, self.worktree_path, exec_path=JADOLINT_PATH, tag='test')
        self.assertEqual(cd.uri, 'http://example.com')
        self.assertEqual(cd.gitpath, self.git_path)
        self.assertEqual(cd.worktreepath, os.path.join(self.worktree_path, os.path.split(cd.gitpath)[1]))
        self.assertEqual(cd.origin, 'http://example.com')
        self.assertEqual(cd.tag, 'test')
        self.assertEqual(cd.exec_path, JADOLINT_PATH)

    def test_fetch(self):
        """Test whether commits are properly processed"""

        cd = CoDep('http://example.com', self.git_path, self.worktree_path,
                   exec_path=JADOLINT_PATH, in_paths=['Dockerfile'])
        commits = [commit for commit in cd.fetch(category=CATEGORY_CODEP_JADOLINT)]

        self.assertEqual(len(commits), 2)

        analysis = commits[0]['data']['analysis']
        self.assertIn('Dockerfile', analysis)
        expected_deps = ['debian stretch-slim',
                         'bash',
                         'locales',
                         'gcc',
                         'git',
                         'git-core',
                         'python3',
                         'python3-pip',
                         'python3-venv',
                         'python3-dev',
                         'python3-gdbm',
                         'mariadb-client',
                         'unzip',
                         'curl',
                         'wget',
                         'sudo',
                         'ssh']
        analysis['Dockerfile'][DEPENDENCIES].sort()
        expected_deps.sort()
        self.assertListEqual(analysis['Dockerfile'][DEPENDENCIES], expected_deps)

        analysis = commits[1]['data']['analysis']
        self.assertIn('Dockerfile', analysis)
        expected_deps = ['debian stretch-slim',
                         'bash',
                         'locales',
                         'gcc',
                         'git',
                         'cloc',
                         'git-core',
                         'python3',
                         'python3-pip',
                         'python3-venv',
                         'python3-dev',
                         'python3-gdbm',
                         'mariadb-client',
                         'unzip',
                         'curl',
                         'wget',
                         'sudo',
                         'ssh']
        analysis['Dockerfile'][DEPENDENCIES].sort()
        expected_deps.sort()
        self.assertListEqual(analysis['Dockerfile'][DEPENDENCIES], expected_deps)

    def test_fetch_empty(self):
        """Test whether no commits are returned"""

        cd = CoDep('http://example.com', self.git_path, self.worktree_path,
                   exec_path=JADOLINT_PATH, in_paths=['Unknown'])
        commits = [commit for commit in cd.fetch(category=CATEGORY_CODEP_JADOLINT)]
        self.assertEqual(commits, [])

    def test_fetch_error(self):
        """Test whether an exception is thrown when the exec_path isn't defined and the category is jadolint"""

        cd = CoDep('http://example.com', self.git_path, self.worktree_path, tag='test')
        with self.assertRaises(GraalError):
            _ = [item for item in cd.fetch(category=CATEGORY_CODEP_JADOLINT)]


class TestDependencyAnalyzer(TestCaseAnalyzer):
    """DependencyAnalyzer tests"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_path = tempfile.mkdtemp(prefix='codep_')

        data_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(data_path, 'data')

        repo_name = 'graaltest'
        cls.repo_path = os.path.join(cls.tmp_path, repo_name)

        fdout, _ = tempfile.mkstemp(dir=cls.tmp_path)

        zip_path = os.path.join(data_path, repo_name + '.zip')
        subprocess.check_call(['unzip', '-qq', zip_path, '-d', cls.tmp_path])

        test_analyzer = get_file_path(ANALYZER_TEST_FOLDER + DOCKERFILE_TEST)
        shutil.copy2(test_analyzer, cls.tmp_path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)

    def test_pyreverse_init(self):
        """Test initialization"""

        dep_analyzer = PyreverseAnalyzer()

        self.assertIsInstance(dep_analyzer, PyreverseAnalyzer)
        self.assertIsInstance(dep_analyzer.analyzer, Reverse)

    def test_jadolint_init(self):
        """Test initialization"""

        dep_analyzer = JadolintAnalyzer(JADOLINT_PATH)

        self.assertIsInstance(dep_analyzer, JadolintAnalyzer)
        self.assertIsInstance(dep_analyzer.analyzer, Jadolint)

    def test_analyze_pyreverse(self):
        """Test whether the analyze method works"""

        module_path = os.path.join(self.tmp_path, 'graaltest', 'perceval')
        dep_analyzer = PyreverseAnalyzer()
        result = dep_analyzer.analyze(module_path)

        self.assertIn('classes', result)
        self.assertTrue(type(result['classes']), dict)
        self.assertIn('nodes', result['classes'])
        self.assertTrue(type(result['classes']['nodes']), list)
        self.assertIn('links', result['classes'])
        self.assertTrue(type(result['classes']['links']), list)

    def test_analyze_jadolint(self):
        """Test whether the analyze method works"""

        file_path = os.path.join(self.tmp_path, DOCKERFILE_TEST)
        dep_analyzer = JadolintAnalyzer(JADOLINT_PATH)
        result = dep_analyzer.analyze(file_path)

        expected_deps = [
            'debian stretch-slim',
            'bash',
            'locales',
            'gcc',
            'git',
            'git-core',
            'python3',
            'python3-pip',
            'python3-venv',
            'python3-dev',
            'python3-gdbm',
            'mariadb-client',
            'unzip',
            'curl',
            'wget',
            'sudo',
            'ssh'
        ]

        self.assertIn(DEPENDENCIES, result)
        self.assertListEqual(result[DEPENDENCIES], expected_deps)


class TestCoDepCommand(unittest.TestCase):
    """CoDepCommand tests"""

    def test_backend_class(self):
        """Test if the backend class is CoDep"""

        self.assertIs(CoDepCommand.BACKEND, CoDep)

    def test_setup_cmd_parser(self):
        """Test setup_cmd_parser"""

        parser = CoDepCommand.setup_cmd_parser()
        self.assertIsInstance(parser, GraalCommandArgumentParser)
        self.assertEqual(parser._backend, CoDep)

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
                '--category', CATEGORY_CODEP_JADOLINT,
                '--in-paths', 'Dockerfile', 'Dockerfile-full', 'Dockerfile-secured']

        parsed_args = parser.parse(*args)
        self.assertEqual(parsed_args.uri, 'http://example.com/')
        self.assertEqual(parsed_args.git_path, '/tmp/gitpath')
        self.assertEqual(parsed_args.tag, 'test')
        self.assertEqual(parsed_args.from_date, DEFAULT_DATETIME)
        self.assertEqual(parsed_args.category, CATEGORY_CODEP_JADOLINT),
        self.assertEqual(parsed_args.exec_path, JADOLINT_PATH)
        self.assertListEqual(parsed_args.in_paths, ['Dockerfile', 'Dockerfile-full', 'Dockerfile-secured'])


if __name__ == "__main__":
    unittest.main()
