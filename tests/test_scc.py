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
#     wmeijer221 <w.meijer.5@student.rug.nl>
#

import subprocess
import unittest.mock
import unittest

from graal.backends.core.analyzers.scc import SCC

from .base_analyzer import (DOCKERFILE_TEST,
                            ANALYZER_TEST_FILE,
                            ANALYZER_TEST_FOLDER,
                            TestCaseAnalyzer)


class TestSCC(TestCaseAnalyzer):
    """SCC Analyzer tests"""

    def test_constructor(self):
        """Tests the constructor with different repository levels."""

        scc = SCC(repository_level=False)
        self.assertEqual(scc.analyze, scc.analyze_files)

        scc = SCC(repository_level=True)
        self.assertEqual(scc.analyze, scc.analyze_repository)

    def test_analyze_files(self):
        """Tests analyze files"""

        scc = SCC(repository_level=False)

        kwargs = {
            'commit': {'files': [
                {'file': ANALYZER_TEST_FILE},
                {'file': DOCKERFILE_TEST}
            ]},
            'in_paths': [],
            'worktreepath': ANALYZER_TEST_FOLDER
        }

        results = scc.analyze(**kwargs)

        self.assertEqual(len(results), 2)

        for result in results:
            self.assertIn('ccn', result)
            self.assertEqual(type(result['ccn']), int)
            self.assertIn('loc', result)
            self.assertEqual(type(result['loc']), int)
            self.assertIn('comments', result)
            self.assertEqual(type(result['comments']), int)
            self.assertIn('blanks', result)
            self.assertEqual(type(result['blanks']), int)

    def test_analyze_repository(self):
        """Tests analyze repository"""

        scc = SCC(repository_level=True)

        kwargs = {
            'worktreepath': self.tmp_data_path
        }

        results = scc.analyze(**kwargs)

        self.assertEqual(type(results), dict)
        self.assertEqual(len(results), 2)

        for language, language_result in results.items():
            self.assertIn('ccn', language_result)
            self.assertTrue(type(language_result['ccn']), int)
            self.assertIn('loc', language_result)
            self.assertTrue(type(language_result['loc']), int)
            self.assertIn('blanks', language_result)
            self.assertTrue(type(language_result['blanks']), int)
            self.assertIn('comments', language_result)
            self.assertTrue(type(language_result['comments']), int)
            self.assertIn('total_files', language_result)
            self.assertTrue(type(language_result['total_files']), int)

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_repository_error(self, check_output_mock):
        """Tests if error is thrown when invalid repository is given."""

        check_output_mock.side_effect = subprocess.CalledProcessError(
            -1, "command", output=b'output')

        scc = SCC(repository_level=True)
        kwargs = {
            'worktreepath': self.tmp_data_path
        }

        _ = scc.analyze(**kwargs)

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_files_error(self, check_output_mock):
        """Tests if error is thrown when invalid file is given."""

        check_output_mock.side_effect = subprocess.CalledProcessError(
            -1, "command", output=b'output')

        scc = SCC(repository_level=False)
        kwargs = {
            'commit': {'files': [
                {'file': self.tmp_data_path},
            ]},
            'in_paths': [],
            'worktreepath': ANALYZER_TEST_FOLDER
        }

        _ = scc.analyze(**kwargs)


if __name__ == "__main__":
    unittest.main()
