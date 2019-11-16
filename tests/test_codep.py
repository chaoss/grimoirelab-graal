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
# along with this program. If not, see <http://www.gnu.org/licenses/>.
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
from graal.backends.core.analyzers.reverse import Reverse
from graal.backends.core.codep import (CATEGORY_CODEP,
                                       CoDep,
                                       DependencyAnalyzer,
                                       CoDepCommand,
                                       logger)
from graal.graal import GraalError
from perceval.utils import DEFAULT_DATETIME
from base_analyzer import TestCaseAnalyzer
from base_repo import TestCaseRepo


class TestCoDepBackend(TestCaseRepo):
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

        with self.assertRaises(GraalError):
            _ = CoDep('http://example.com', self.git_path, self.worktree_path, details=True, tag='test')

    def test_fetch(self):
        """Test whether commits are properly processed"""

        cd = CoDep('http://example.com', self.git_path, self.worktree_path, entrypoint="perceval")
        commits = [commit for commit in cd.fetch()]

        self.assertEqual(len(commits), 6)
        self.assertFalse(os.path.exists(cd.worktreepath))

        commit = commits[0]
        self.assertEqual(commit['backend_name'], 'CoDep')
        self.assertEqual(commit['category'], CATEGORY_CODEP)
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

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)

    def test_init(self):
        """Test initialization"""

        dep_analyzer = DependencyAnalyzer()

        self.assertIsInstance(dep_analyzer, DependencyAnalyzer)
        self.assertIsInstance(dep_analyzer.reverse, Reverse)

    def test_analyze(self):
        """Test whether the analyze method works"""

        module_path = os.path.join(self.tmp_path, 'graaltest', 'perceval')
        dep_analyzer = DependencyAnalyzer()
        result = dep_analyzer.analyze(module_path)

        self.assertIn('classes', result)
        self.assertTrue(type(result['classes']), dict)
        self.assertIn('nodes', result['classes'])
        self.assertTrue(type(result['classes']['nodes']), list)
        self.assertIn('links', result['classes'])
        self.assertTrue(type(result['classes']['links']), list)


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


if __name__ == "__main__":
    unittest.main()
