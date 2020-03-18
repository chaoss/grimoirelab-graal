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
import unittest

from base_analyzer import (TestCaseAnalyzer,
                           ANALYZER_TEST_FILE)

from graal.backends.core.analyzers.lizard import Lizard


class TestLizard(TestCaseAnalyzer):
    """Lizard tests"""

    def test_analyze_file_no_details(self):
        """Test whether lizard returns the expected fields data for files"""

        lizard = Lizard()
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE),
                  'details': False}
        result = lizard.analyze(**kwargs)

        self.assertNotIn('funs', result)
        self.assertIn('ccn', result)
        self.assertTrue(type(result['ccn']), int)
        self.assertIn('avg_ccn', result)
        self.assertTrue(type(result['avg_ccn']), float)
        self.assertIn('avg_loc', result)
        self.assertTrue(type(result['avg_loc']), float)
        self.assertIn('avg_tokens', result)
        self.assertTrue(type(result['avg_tokens']), float)
        self.assertIn('num_funs', result)
        self.assertTrue(type(result['num_funs']), int)
        self.assertIn('loc', result)
        self.assertTrue(type(result['loc']), int)
        self.assertIn('tokens', result)
        self.assertTrue(type(result['tokens']), int)

    def test_analyze_file_details(self):
        """Test whether lizard returns the expected fields data for files"""

        lizard = Lizard()
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE),
                  'details': True}
        result = lizard.analyze(**kwargs)

        self.assertIn('ccn', result)
        self.assertTrue(type(result['ccn']), int)
        self.assertIn('avg_ccn', result)
        self.assertTrue(type(result['avg_ccn']), float)
        self.assertIn('avg_loc', result)
        self.assertTrue(type(result['avg_loc']), float)
        self.assertIn('avg_tokens', result)
        self.assertTrue(type(result['avg_tokens']), float)
        self.assertIn('num_funs', result)
        self.assertTrue(type(result['num_funs']), int)
        self.assertIn('loc', result)
        self.assertTrue(type(result['loc']), int)
        self.assertIn('tokens', result)
        self.assertTrue(type(result['tokens']), int)
        self.assertIn('funs', result)
        self.assertTrue(type(result['funs']), dict)

        for fd in result['funs']:
            self.assertIn('ccn', fd)
            self.assertTrue(type(fd['ccn']), int)
            self.assertIn('tokens', fd)
            self.assertTrue(type(fd['tokens']), int)
            self.assertIn('loc', fd)
            self.assertTrue(type(fd['loc']), int)
            self.assertIn('lines', fd)
            self.assertTrue(type(fd['lines']), int)
            self.assertIn('name', fd)
            self.assertTrue(type(fd['name']), str)
            self.assertIn('args', fd)
            self.assertTrue(type(fd['args']), int)
            self.assertIn('start', fd)
            self.assertTrue(type(fd['start']), int)
            self.assertIn('end', fd)
            self.assertTrue(type(fd['end']), int)

    def test_analyze_repository(self):
        """Test whether lizard returns the expected fields data for repository"""

        lizard = Lizard()
        kwargs = {'repository_path': self.tmp_data_path,
                  'repository_level': True,
                  'files_affected': [],
                  'details': False}
        result = lizard.analyze(**kwargs)
        result = result[0]

        self.assertIn('ccn', result)
        self.assertTrue(type(result['ccn']), int)
        self.assertIn('num_funs', result)
        self.assertTrue(type(result['num_funs']), int)
        self.assertIn('loc', result)
        self.assertTrue(type(result['loc']), int)
        self.assertIn('tokens', result)
        self.assertTrue(type(result['tokens']), int)
        self.assertIn('in_commit', result)
        self.assertTrue(type(result['in_commit']), bool)
        self.assertIn('blanks', result)
        self.assertTrue(type(result['blanks']), int)
        self.assertIn('comments', result)
        self.assertTrue(type(result['comments']), int)


if __name__ == "__main__":
    unittest.main()
