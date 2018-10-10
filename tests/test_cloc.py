#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2018 Bitergia
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

from graal.backends.core.analyzers.cloc import Cloc
from graal.graal import GraalError


class TestCloc(TestCaseAnalyzer):
    """Cloc tests"""

    def test_analyze(self):
        """Test whether cloc returns the expected fields data"""

        cloc = Cloc()
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)}
        result = cloc.analyze(**kwargs)

        self.assertIn('blanks', result)
        self.assertTrue(type(result['blanks']), int)
        self.assertIn('comments', result)
        self.assertTrue(type(result['comments']), int)
        self.assertIn('loc', result)
        self.assertTrue(type(result['loc']), int)

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_error(self, check_output_mock):
        """Test whether an exception is thrown in case of errors"""

        check_output_mock.side_effect = subprocess.CalledProcessError(-1, "command", output=b'output')

        cloc = Cloc()
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)}
        with self.assertRaises(GraalError):
            _ = cloc.analyze(**kwargs)


if __name__ == "__main__":
    unittest.main()
