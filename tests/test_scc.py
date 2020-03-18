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
import unittest

from base_analyzer import (TestCaseAnalyzer,
                           ANALYZER_TEST_FILE)

from graal.backends.core.analyzers.scc import SCC


class TestSCC(TestCaseAnalyzer):
    """SCC tests"""

    def test_analyze_file_no_details(self):
        """Test whether SCC returns the expected fields data for files"""

        scc = SCC()
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE),
                  'details': False}
        result = scc.analyze(**kwargs)

        self.assertIn('ccn', result)
        self.assertTrue(type(result['ccn']), int)
        self.assertIn('loc', result)
        self.assertTrue(type(result['loc']), int)
        self.assertIn('comments', result)
        self.assertTrue(type(result['comments']), int)
        self.assertIn('blanks', result)
        self.assertTrue(type(result['blanks']), int)

    def test_analyze_file_details(self):
        """Test whether SCC returns the expected fields data for files"""

        scc = SCC()
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE),
                  'details': True}
        result = scc.analyze(**kwargs)

        self.assertIn('ccn', result)
        self.assertTrue(type(result['ccn']), int)
        self.assertIn('loc', result)
        self.assertTrue(type(result['loc']), int)
        self.assertIn('comments', result)
        self.assertTrue(type(result['comments']), int)
        self.assertIn('blanks', result)
        self.assertTrue(type(result['blanks']), int)

    def test_analyze_repository(self):
        """Test whether SCC returns the expected fields data for repository"""

        scc = SCC()
        kwargs = {'repository_path': self.tmp_data_path,
                  'repository_level': True,
                  'files_affected': [],
                  'details': False}
        result = scc.analyze(**kwargs)

        for language in result.keys():
            language_result = result[language]
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
    def test_analyze_error(self, check_output_mock):
        """Test whether an exception is thrown in case of errors"""

        check_output_mock.side_effect = subprocess.CalledProcessError(
            -1, "command", output=b'output')

        scc = SCC()
        kwargs = {'repository_path': self.tmp_data_path,
                  'repository_level': True,
                  'files_affected': [],
                  'details': False}
        _ = scc.analyze(**kwargs)


if __name__ == "__main__":
    unittest.main()
