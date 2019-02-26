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
# along with this program; if not, write to the Free Software
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1335, USA.
#
# Authors:
#     Valerio Cosentino <valcos@bitergia.com>
#

import os
import subprocess
import unittest
import unittest.mock

from base_analyzer import (TestCaseAnalyzer,
                           ANALYZER_TEST_FILE)

from graal.backends.core.analyzers.scancode import ScanCode
from graal.graal import GraalError
from utils import SCANCODE_PATH


class TestScanCode(TestCaseAnalyzer):
    """ScanCode tests"""

    def test_init(self):
        """Test the analyzer is properly initialized"""

        scancode = ScanCode(exec_path=SCANCODE_PATH)
        self.assertEqual(scancode.exec_path, SCANCODE_PATH)

        with self.assertRaises(GraalError):
            _ = ScanCode("/tmp/invalid")

    def test_analyze(self):
        """Test whether nomos returns the expected fields data"""

        scancode = ScanCode(exec_path=SCANCODE_PATH)
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)}
        result = scancode.analyze(**kwargs)

        self.assertIn('licenses', result)

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_error(self, check_output_mock):
        """Test whether an exception is thrown in case of errors"""

        check_output_mock.side_effect = subprocess.CalledProcessError(-1, "command", output=b'output')

        scancode = ScanCode(exec_path=SCANCODE_PATH)
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)}
        with self.assertRaises(GraalError):
            _ = scancode.analyze(**kwargs)


if __name__ == "__main__":
    unittest.main()
