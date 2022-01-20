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
#     wmeijer221 <w.meijer.5@student.rug.nl>
#

import subprocess
import unittest.mock

from graal.backends.core.analyzers.cloc import (Cloc, DEFAULT_DIFF_TIMEOUT)

from .base_analyzer import (DOCKERFILE_TEST,
                            ANALYZER_TEST_FILE,
                            TestCaseAnalyzer)


class TestCloc(TestCaseAnalyzer):
    """Cloc tests"""

    def test_constructor(self):
        """Tests the constructor with different repository levels."""

        cloc = Cloc(repository_level=False)
        self.assertEqual(cloc.analyze, cloc.analyze_files)

        cloc = Cloc(repository_level=True)
        self.assertEqual(cloc.analyze, cloc.analyze_repository)

        self.assertEqual(cloc.diff_timeout, DEFAULT_DIFF_TIMEOUT)

        set_timeout = 25
        cloc = Cloc(repository_level=True, diff_timeout=set_timeout)
        self.assertEqual(cloc.diff_timeout, set_timeout)

    def test_analyze_repository_without_in_paths(self):
        """Tests CLOC on a repository level without in_paths set."""

        cloc = Cloc(repository_level=True)

        kwargs = {
            'worktreepath': self.tmp_data_path,
            'in_paths': []
        }

        results = cloc.analyze(**kwargs)

        self.assertEqual(len(results), 4)

        for result in results:
            self.assertIn('file_path', result)
            self.assertEqual(type(result['file_path']), str)
            self.assertIn('ext', result)
            self.assertEqual(type(result['ext']), str)
            self.assertIn('blanks', result)
            self.assertEqual(type(result['blanks']), int)
            self.assertIn('comments', result)
            self.assertEqual(type(result['comments']), int)
            self.assertIn('loc', result)
            self.assertEqual(type(result['loc']), int)

    def test_analyze_repository_with_in_paths(self):
        """Tests CLOC on a repository level with in_paths set."""

        cloc = Cloc(repository_level=True)

        kwargs = {
            'worktreepath': self.tmp_data_path,
            'in_paths': [ANALYZER_TEST_FILE, DOCKERFILE_TEST]
        }

        results = cloc.analyze(**kwargs)

        self.assertEqual(len(results), 2)

        for result in results:
            self.assertIn('file_path', result)
            self.assertEqual(type(result['file_path']), str)
            self.assertIn('ext', result)
            self.assertEqual(type(result['ext']), str)
            self.assertIn('blanks', result)
            self.assertEqual(type(result['blanks']), int)
            self.assertIn('comments', result)
            self.assertEqual(type(result['comments']), int)
            self.assertIn('loc', result)
            self.assertEqual(type(result['loc']), int)

    def test_analyze_files_without_in_paths(self):
        """Tests CLOC on a file level without in_paths set."""

        cloc = Cloc(repository_level=False)

        kwargs = {
            'commit': {'files': [{'file': ANALYZER_TEST_FILE}, {'file': DOCKERFILE_TEST}]},
            'in_paths': [],
            'worktreepath': self.tmp_data_path
        }

        results = cloc.analyze(**kwargs)

        self.assertEqual(len(results), 2)

        for result in results:
            self.assertIn('file_path', result)
            self.assertEqual(type(result['file_path']), str)
            self.assertIn('ext', result)
            self.assertEqual(type(result['ext']), str)
            self.assertIn('blanks', result)
            self.assertEqual(type(result['blanks']), int)
            self.assertIn('comments', result)
            self.assertEqual(type(result['comments']), int)
            self.assertIn('loc', result)
            self.assertEqual(type(result['loc']), int)

    def test_analyze_files_with_in_paths(self):
        """Tests CLOC on a file level with in_paths set."""

        cloc = Cloc(repository_level=False)

        kwargs = {
            'commit': {'files': [{'file': ANALYZER_TEST_FILE}]},
            'in_paths': [ANALYZER_TEST_FILE],
            'worktreepath': self.tmp_data_path
        }

        results = cloc.analyze(**kwargs)

        self.assertEqual(len(results), 1)

        for result in results:
            self.assertIn('file_path', result)
            self.assertEqual(type(result['file_path']), str)
            self.assertIn('ext', result)
            self.assertEqual(type(result['ext']), str)
            self.assertIn('blanks', result)
            self.assertEqual(type(result['blanks']), int)
            self.assertIn('comments', result)
            self.assertEqual(type(result['comments']), int)
            self.assertIn('loc', result)
            self.assertEqual(type(result['loc']), int)

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_repository_error(self, check_output_mock):
        """Test whether an exception is thrown in case of errors"""

        check_output_mock.side_effect = subprocess.CalledProcessError(-1, "command", output=b'output')

        cloc = Cloc(repository_level=True)

        kwargs = {
            'worktreepath': self.tmp_data_path,
            'in_paths': []
        }

        _ = cloc.analyze(**kwargs)

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_files_error(self, check_output_mock):
        """Test whether an exception is thrown in case of errors"""

        check_output_mock.side_effect = subprocess.CalledProcessError(-1, "command", output=b'output')

        cloc = Cloc(repository_level=True)

        kwargs = {
            'commit': {'files': [{'file': self.tmp_data_path}]},
            'in_paths': [],
            'worktreepath': self.tmp_data_path
        }

        _ = cloc.analyze(**kwargs)


if __name__ == "__main__":
    unittest.main()
