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

from graal.backends.core.analyzers.lint import Lint
from graal.backends.core.coqua import (CATEGORY_COQUA,
                                       CoQua,
                                       ModuleAnalyzer,
                                       CoQuaCommand)
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
        subprocess.check_call(['unzip', '-qq', zip_path, '-d', cls.tmp_repo_path])

        origin_path = os.path.join(cls.tmp_repo_path, repo_name)
        subprocess.check_call(['git', 'clone', '-q', '--bare', origin_path, repo_path],
                              stderr=fdout)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)

    def test_initialization(self):
        """Test whether attributes are initializated"""

        cq = CoQua('http://example.com', self.git_path, self.worktree_path, entrypoint="module", tag='test')
        self.assertEqual(cq.uri, 'http://example.com')
        self.assertEqual(cq.gitpath, self.git_path)
        self.assertEqual(cq.worktreepath, os.path.join(self.worktree_path, os.path.split(cq.gitpath)[1]))
        self.assertEqual(cq.origin, 'http://example.com')
        self.assertEqual(cq.tag, 'test')
        self.assertEqual(cq.entrypoint, "module")

        with self.assertRaises(GraalError):
            _ = CoQua('http://example.com', self.git_path, self.worktree_path, details=True, tag='test')

    def test_fetch(self):
        """Test whether commits are properly processed"""

        cd = CoQua('http://example.com', self.git_path, self.worktree_path, entrypoint="perceval")
        commits = [commit for commit in cd.fetch()]

        self.assertEqual(len(commits), 3)
        self.assertFalse(os.path.exists(cd.worktreepath))

        commit = commits[0]
        self.assertEqual(commit['backend_name'], 'CoQua')
        self.assertEqual(commit['category'], CATEGORY_COQUA)
        result = commit['data']['analysis']
        self.assertNotIn('modules', result)
        self.assertIn('quality', result)
        self.assertTrue(type(result['quality']), str)
        self.assertIn('num_modules', result)
        self.assertTrue(type(result['num_modules']), int)
        self.assertIn('warnings', result)
        self.assertTrue(type(result['warnings']), int)


class TestModuleAnalyzer(TestCaseAnalyzer):
    """ModuleAnalyzer tests"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_path = tempfile.mkdtemp(prefix='coqua_')

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

        mod_analyzer = ModuleAnalyzer()

        self.assertIsInstance(mod_analyzer, ModuleAnalyzer)
        self.assertIsInstance(mod_analyzer.lint, Lint)

    def test_analyze(self):
        """Test whether the analyze method works"""

        module_path = os.path.join(self.tmp_path, 'graaltest', 'perceval')
        mod_analyzer = ModuleAnalyzer()
        result = mod_analyzer.analyze(module_path)

        self.assertNotIn('modules', result)
        self.assertIn('quality', result)
        self.assertTrue(type(result['quality']), str)
        self.assertIn('num_modules', result)
        self.assertTrue(type(result['num_modules']), int)
        self.assertIn('warnings', result)
        self.assertTrue(type(result['warnings']), int)


class TestCoDepCommand(unittest.TestCase):
    """CoQuaCommand tests"""

    def test_backend_class(self):
        """Test if the backend class is CoQua"""

        self.assertIs(CoQuaCommand.BACKEND, CoQua)


if __name__ == "__main__":
    unittest.main()
