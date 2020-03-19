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
from graal.backends.core.analyzers.bandit import Bandit
from graal.backends.core.covuln import (CATEGORY_COVULN,
                                        CoVuln,
                                        VulnAnalyzer,
                                        CoVulnCommand)
from perceval.utils import DEFAULT_DATETIME
from graal.graal import GraalError
from base_analyzer import TestCaseAnalyzer
from base_repo import TestCaseRepo


class TestCoVulnBackend(TestCaseRepo):
    """CoVuln backend tests"""

    def test_initialization(self):
        """Test whether attributes are initializated"""

        cv = CoVuln('http://example.com', self.git_path, self.worktree_path, entrypoint="module", tag='test')
        self.assertEqual(cv.uri, 'http://example.com')
        self.assertEqual(cv.gitpath, self.git_path)
        self.assertEqual(cv.worktreepath, os.path.join(self.worktree_path, os.path.split(cv.gitpath)[1]))
        self.assertEqual(cv.origin, 'http://example.com')
        self.assertEqual(cv.tag, 'test')
        self.assertEqual(cv.entrypoint, "module")

        with self.assertRaises(GraalError):
            _ = CoVuln('http://example.com', self.git_path, self.worktree_path, details=True, tag='test')

    def test_fetch(self):
        """Test whether commits are properly processed"""

        cd = CoVuln('http://example.com', self.git_path, self.worktree_path, entrypoint="perceval")
        commits = [commit for commit in cd.fetch()]

        self.assertEqual(len(commits), 6)
        self.assertFalse(os.path.exists(cd.worktreepath))

        commit = commits[0]
        self.assertEqual(commit['backend_name'], 'CoVuln')
        self.assertEqual(commit['category'], CATEGORY_COVULN)
        result = commit['data']['analysis']

        self.assertIn('loc_analyzed', result)
        self.assertTrue(type(result['loc_analyzed']), int)
        self.assertIn('num_vulns', result)
        self.assertTrue(type(result['num_vulns']), int)
        self.assertIn('by_severity', result)
        self.assertTrue(type(result['by_severity']), dict)
        self.assertIn('undefined', result['by_severity'])
        self.assertTrue(type(result['by_severity']['undefined']), int)
        self.assertIn('low', result['by_severity'])
        self.assertTrue(type(result['by_severity']['low']), int)
        self.assertIn('medium', result['by_severity'])
        self.assertTrue(type(result['by_severity']['medium']), int)
        self.assertIn('high', result['by_severity'])
        self.assertTrue(type(result['by_severity']['high']), int)

        self.assertIn('by_confidence', result)
        self.assertTrue(type(result['by_confidence']), dict)
        self.assertIn('undefined', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['undefined']), int)
        self.assertIn('low', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['low']), int)
        self.assertIn('medium', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['medium']), int)
        self.assertIn('high', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['high']), int)


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

        vuln_analyzer = VulnAnalyzer()

        self.assertIsInstance(vuln_analyzer, VulnAnalyzer)
        self.assertIsInstance(vuln_analyzer.bandit, Bandit)

    def test_analyze(self):
        """Test whether the analyze method works"""

        module_path = os.path.join(self.tmp_path, 'graaltest', 'perceval')
        vuln_analyzer = VulnAnalyzer()
        result = vuln_analyzer.analyze(module_path)

        self.assertIn('loc_analyzed', result)
        self.assertTrue(type(result['loc_analyzed']), int)
        self.assertIn('num_vulns', result)
        self.assertTrue(type(result['num_vulns']), int)
        self.assertIn('by_severity', result)
        self.assertTrue(type(result['by_severity']), dict)
        self.assertIn('undefined', result['by_severity'])
        self.assertTrue(type(result['by_severity']['undefined']), int)
        self.assertIn('low', result['by_severity'])
        self.assertTrue(type(result['by_severity']['low']), int)
        self.assertIn('medium', result['by_severity'])
        self.assertTrue(type(result['by_severity']['medium']), int)
        self.assertIn('high', result['by_severity'])
        self.assertTrue(type(result['by_severity']['high']), int)

        self.assertIn('by_confidence', result)
        self.assertTrue(type(result['by_confidence']), dict)
        self.assertIn('undefined', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['undefined']), int)
        self.assertIn('low', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['low']), int)
        self.assertIn('medium', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['medium']), int)
        self.assertIn('high', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['high']), int)


class TestCoVulnCommand(unittest.TestCase):
    """CoVulnCommand tests"""

    def test_backend_class(self):
        """Test if the backend class is CoVuln"""

        self.assertIs(CoVulnCommand.BACKEND, CoVuln)

    def test_setup_cmd_parser(self):
        """Test setup_cmd_parser"""

        parser = CoVulnCommand.setup_cmd_parser()

        self.assertIsInstance(parser, GraalCommandArgumentParser)
        self.assertEqual(parser._backend, CoVuln)

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
