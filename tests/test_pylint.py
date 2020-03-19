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

from graal.backends.core.analyzers.pylint import PyLint
from graal.graal import GraalError


class TestPyLint(TestCaseAnalyzer):
    """PyLint tests"""

    def test_analyze_details(self):
        """Test whether pylint returns the expected fields data"""

        pylint = PyLint()
        kwargs = {
            'module_path': os.path.join(self.repo_path, "perceval"),
            'details': True
        }
        result = pylint.analyze(**kwargs)

        self.assertIn('quality', result)
        self.assertTrue(type(result['quality']), str)
        self.assertIn('num_modules', result)
        self.assertTrue(type(result['num_modules']), int)
        self.assertIn('warnings', result)
        self.assertTrue(type(result['warnings']), int)
        self.assertIn('modules', result)
        self.assertTrue(type(result['modules']), dict)

        first_key = list(result['modules'].keys())[0]
        for md in result['modules'].get(first_key):
            self.assertTrue(type(md), str)

    def test_analyze_no_details(self):
        """Test whether pylint returns the expected fields data"""

        pylint = PyLint()
        kwargs = {
            'module_path': os.path.join(self.repo_path, ANALYZER_TEST_FILE),
            'details': False
        }
        result = pylint.analyze(**kwargs)

        self.assertNotIn('modules', result)
        self.assertIn('quality', result)
        self.assertTrue(type(result['quality']), str)
        self.assertIn('num_modules', result)
        self.assertTrue(type(result['num_modules']), int)
        self.assertIn('warnings', result)
        self.assertTrue(type(result['warnings']), int)

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_error(self, check_output_mock):
        """Test whether an exception is thrown in case of errors"""

        check_output_mock.side_effect = subprocess.CalledProcessError(-1, "command", output=b'output')

        pylint = PyLint()
        kwargs = {
            'module_path': os.path.join(self.repo_path, ANALYZER_TEST_FILE),
            'details': False
        }
        with self.assertRaises(GraalError):
            _ = pylint.analyze(**kwargs)


if __name__ == "__main__":
    unittest.main()
