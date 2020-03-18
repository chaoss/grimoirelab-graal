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
import unittest.mock

from base_analyzer import TestCaseAnalyzer

from graal.backends.core.analyzers.reverse import Reverse
from graal.graal import GraalError


class TestReverse(TestCaseAnalyzer):
    """Reverse tests"""

    def test_analyze(self):
        """Test whether Reverse returns the expected fields data"""

        reverse = Reverse()
        kwargs = {
            'module_path': os.path.join(self.repo_path, "perceval"),
        }
        result = reverse.analyze(**kwargs)

        self.assertIn('classes', result)
        self.assertTrue(type(result['classes']), dict)
        self.assertIn('nodes', result['classes'])
        self.assertTrue(type(result['classes']['nodes']), list)
        self.assertIn('links', result['classes'])
        self.assertTrue(type(result['classes']['links']), list)
        self.assertIn('packages', result)
        self.assertTrue(type(result['packages']), dict)
        self.assertTrue(type(result['packages']['nodes']), list)
        self.assertIn('links', result['packages'])
        self.assertTrue(type(result['packages']['links']), list)

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_error(self, check_output_mock):
        """Test whether an exception is thrown in case of errors"""

        check_output_mock.side_effect = subprocess.CalledProcessError(-1, "command", output=b'output')

        reverse = Reverse()
        kwargs = {
            'module_path': os.path.join(self.repo_path, "perceval"),
        }
        with self.assertRaises(GraalError):
            _ = reverse.analyze(**kwargs)


if __name__ == "__main__":
    unittest.main()
