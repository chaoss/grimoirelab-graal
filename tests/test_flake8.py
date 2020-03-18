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
#     inishchith <inishchith@gmail.com>
#     Valerio Cosentino <valcos@bitergia.com>
#

import os
import subprocess
import unittest.mock

from base_analyzer import (TestCaseAnalyzer,
                           ANALYZER_TEST_FILE)

from graal.backends.core.analyzers.flake8 import Flake8


class TestFlake8(TestCaseAnalyzer):
    """Flake8 tests"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.worktree_path = os.path.join(cls.tmp_path, 'worktrees')

    def test_analyze_details(self):
        """Test whether flake8 returns the expected fields data"""

        flake8 = Flake8()
        kwargs = {
            'module_path': os.path.join(self.repo_path, "perceval"),
            'worktree_path': self.worktree_path,
            'details': True
        }
        result = flake8.analyze(**kwargs)

        self.assertIn('lines', result)
        self.assertTrue(type(result['lines']), list)
        self.assertIn('warnings', result)
        self.assertTrue(type(result['warnings']), int)

    def test_analyze_no_details(self):
        """Test whether flake8 returns the expected fields data"""

        flake8 = Flake8()
        kwargs = {
            'module_path': os.path.join(self.repo_path, ANALYZER_TEST_FILE),
            'worktree_path': self.worktree_path,
            'details': False
        }
        result = flake8.analyze(**kwargs)

        self.assertNotIn('lines', result)
        self.assertIn('warnings', result)
        self.assertTrue(type(result['warnings']), int)

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_error(self, check_output_mock):
        """Test whether an exception is thrown in case of errors"""

        check_output_mock.side_effect = subprocess.CalledProcessError(
            -1, "command", output=b'output')

        flake8 = Flake8()
        kwargs = {
            'module_path': os.path.join(self.repo_path, ANALYZER_TEST_FILE),
            'worktree_path': self.worktree_path,
            'details': False
        }
        _ = flake8.analyze(**kwargs)


if __name__ == "__main__":
    unittest.main()
