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
import subprocess
import unittest
import unittest.mock

from base_analyzer import (TestCaseAnalyzer,
                           ANALYZER_TEST_FILE)

from graal.backends.core.analyzers.scancode import ScanCode
from graal.graal import GraalError
from utils import SCANCODE_PATH, SCANCODE_CLI_PATH


class TestScanCode(TestCaseAnalyzer):
    """ScanCode tests"""

    def test_init(self):
        """Test the analyzer is properly initialized"""

        scancode = ScanCode(exec_path=SCANCODE_PATH)
        self.assertEqual(scancode.exec_path, SCANCODE_PATH)

        with self.assertRaises(GraalError):
            _ = ScanCode("/tmp/invalid")

    def test_analyze_scancode(self):
        """Test whether scancode returns the expected fields data"""

        scancode = ScanCode(exec_path=SCANCODE_PATH)
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)}
        result = scancode.analyze(**kwargs)

        self.assertIn('licenses', result)
        self.assertIn('copyrights', result)

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_error(self, check_output_mock):
        """Test whether an exception is thrown in case of errors"""

        check_output_mock.side_effect = subprocess.CalledProcessError(-1, "command", output=b'output')

        scancode = ScanCode(exec_path=SCANCODE_PATH)
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)}
        with self.assertRaises(GraalError):
            _ = scancode.analyze(**kwargs)


class TestScanCodeCli(TestCaseAnalyzer):
    """ScanCodeCli tests"""

    def test_init(self):
        """Test the analyzer is properly initialized"""

        scancode_cli = ScanCode(exec_path=SCANCODE_CLI_PATH)
        self.assertEqual(scancode_cli.exec_path, SCANCODE_CLI_PATH)

        with self.assertRaises(GraalError):
            _ = ScanCode("/tmp/invalid")

    def test_analyze_scancode_cli(self):
        """Test whether scancode_cli returns the expected fields data"""

        scancode_cli = ScanCode(exec_path=SCANCODE_CLI_PATH, cli=True)
        kwargs = {'file_paths': [os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)]}
        result = scancode_cli.analyze(**kwargs)

        self.assertIn('licenses', result[0])
        self.assertIn('copyrights', result[0])

    def test_analyze_error(self):
        """Test whether an exception is thrown in case of error"""

        scancode_cli = ScanCode(exec_path=SCANCODE_CLI_PATH, cli=True)
        kwargs = {'file_paths': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)}
        with self.assertRaises(GraalError):
            _ = scancode_cli.analyze(**kwargs)


if __name__ == "__main__":
    unittest.main()
