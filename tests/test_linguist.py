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

import subprocess
import unittest.mock

from base_analyzer import TestCaseAnalyzer

from graal.backends.core.analyzers.linguist import Linguist


class TestLinguist(TestCaseAnalyzer):
    """Linguist tests"""

    def test_analyze_details(self):
        """Test whether linguist returns the expected fields data"""

        linguist = Linguist()
        kwargs = {
            'repository_path': self.repo_path,
            'details': True
        }
        result = linguist.analyze(**kwargs)

        self.assertIn('breakdown', result)
        self.assertTrue(type(result['breakdown']), dict)
        self.assertIn('Python', result)
        self.assertTrue(type(result['Python']), float)

    def test_analyze_no_details(self):
        """Test whether linguist returns the expected fields data"""

        linguist = Linguist()
        kwargs = {
            'repository_path': self.repo_path,
            'details': False
        }
        result = linguist.analyze(**kwargs)

        self.assertNotIn('breakdown', result)
        self.assertIn('Python', result)
        self.assertTrue(type(result['Python']), float)

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_error(self, check_output_mock):
        """Test whether an exception is thrown in case of errors"""

        check_output_mock.side_effect = subprocess.CalledProcessError(
            -1, "command", output=b'output')

        linguist = Linguist()
        kwargs = {
            'repository_path': self.repo_path,
            'details': False
        }
        _ = linguist.analyze(**kwargs)


if __name__ == "__main__":
    unittest.main()
