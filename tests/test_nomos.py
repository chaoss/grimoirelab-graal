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

from graal.backends.core.analyzers.nomos import Nomos
from graal.graal import GraalError
from utils import NOMOS_PATH


class TestNomos(TestCaseAnalyzer):
    """Nomos tests"""

    def test_init(self):
        """Test the analyzer is properly initialized"""

        nomos = Nomos(exec_path=NOMOS_PATH)
        self.assertEqual(nomos.exec_path, NOMOS_PATH)
        self.assertIsNotNone(nomos.search_pattern)

        with self.assertRaises(GraalError):
            _ = Nomos("/tmp/invalid")

    def test_analyze(self):
        """Test whether nomos returns the expected fields data"""

        nomos = Nomos(exec_path=NOMOS_PATH)
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)}
        result = nomos.analyze(**kwargs)

        self.assertIn('licenses', result)

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_error(self, check_output_mock):
        """Test whether an exception is thrown in case of errors"""

        check_output_mock.side_effect = subprocess.CalledProcessError(-1, "command", output=b'output')

        nomos = Nomos(exec_path=NOMOS_PATH)
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)}
        with self.assertRaises(GraalError):
            _ = nomos.analyze(**kwargs)


if __name__ == "__main__":
    unittest.main()
