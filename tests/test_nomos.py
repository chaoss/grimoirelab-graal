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
#     Groninger Bugbusters <w.meijer.5@student.rug.nl>
#

import os
import subprocess
import unittest
import unittest.mock

from base_analyzer import (DOCKERFILE_TEST, TestCaseAnalyzer,
                           ANALYZER_TEST_FILE)

from graal.backends.core.analyzers.nomos import Nomos
from graal.graal import GraalError
from utils import NOMOS_PATH


class TestNomos(TestCaseAnalyzer):
    """Nomos tests"""

    def test_init(self):
        """Test the analyzer is properly initialized"""

        nomos = Nomos()
        self.assertIsNotNone(nomos.search_pattern)

    def test_analyze(self):
        """Test whether nomos returns the expected fields data"""

        nomos = Nomos()
        kwargs = {
            'worktreepath': self.tmp_data_path,
            'commit': {'files': [{'file': ANALYZER_TEST_FILE}, {'file': DOCKERFILE_TEST}]},
            'exec_path': NOMOS_PATH,
            'in_paths': []
        }
        results = nomos.analyze(**kwargs)

        for result in results:
            self.assertIn('licenses', result)

        with self.assertRaises(GraalError):
            kwargs['exec_path'] = "/tmp/invalid"
            _ = nomos.analyze(**kwargs)

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_error(self, check_output_mock):
        """Test whether an exception is thrown in case of errors"""

        check_output_mock.side_effect = subprocess.CalledProcessError(-1, "command", output=b'output')

        nomos = Nomos()
        with self.assertRaises(GraalError):
            _ = nomos.analyze_file(NOMOS_PATH, ANALYZER_TEST_FILE, os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE))


if __name__ == "__main__":
    unittest.main()
