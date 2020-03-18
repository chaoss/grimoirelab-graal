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

from base_analyzer import (TestCaseAnalyzer,
                           ANALYZER_TEST_FILE)

from graal.backends.core.analyzers.bandit import Bandit
from graal.graal import GraalError


class TestBandit(TestCaseAnalyzer):
    """Bandit tests"""

    def test_analyze_details(self):
        """Test whether bandit returns the expected fields data"""

        bandit = Bandit()
        kwargs = {
            'folder_path': os.path.join(self.repo_path),
            'details': True
        }
        result = bandit.analyze(**kwargs)

        self.assertIn('loc_analyzed', result)
        self.assertTrue(type(result['loc_analyzed']), int)
        self.assertIn('num_vulns', result)
        self.assertTrue(type(result['num_vulns']), int)
        self.assertIn('by_severity', result)
        self.assertTrue(type(result['by_severity']), dict)
        self.assertIn('undefined', result['by_severity'])
        self.assertTrue(type(result['by_severity']['undefined']), int)
        self.assertIn('low', result['by_severity'])
        self.assertTrue(type(result['by_severity']['low']), int)
        self.assertIn('medium', result['by_severity'])
        self.assertTrue(type(result['by_severity']['medium']), int)
        self.assertIn('high', result['by_severity'])
        self.assertTrue(type(result['by_severity']['high']), int)

        self.assertIn('by_confidence', result)
        self.assertTrue(type(result['by_confidence']), dict)
        self.assertIn('undefined', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['undefined']), int)
        self.assertIn('low', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['low']), int)
        self.assertIn('medium', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['medium']), int)
        self.assertIn('high', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['high']), int)

        self.assertIn('vulns', result)

        vd = result['vulns'][0]
        self.assertIn('file', vd)
        self.assertTrue(type(vd['file']), str)
        self.assertIn('line', vd)
        self.assertTrue(type(vd['line']), int)
        self.assertIn('severity', vd)
        self.assertTrue(type(vd['severity']), str)
        self.assertIn('confidence', vd)
        self.assertTrue(type(vd['confidence']), str)
        self.assertIn('descr', vd)
        self.assertTrue(type(vd['descr']), str)

    def test_analyze_no_details(self):
        """Test whether bandit returns the expected fields data"""

        bandit = Bandit()
        kwargs = {
            'folder_path': os.path.join(self.repo_path, ANALYZER_TEST_FILE),
            'details': False
        }
        result = bandit.analyze(**kwargs)

        self.assertIn('loc_analyzed', result)
        self.assertTrue(type(result['loc_analyzed']), int)
        self.assertIn('num_vulns', result)
        self.assertTrue(type(result['num_vulns']), int)
        self.assertIn('by_severity', result)
        self.assertTrue(type(result['by_severity']), dict)
        self.assertIn('undefined', result['by_severity'])
        self.assertTrue(type(result['by_severity']['undefined']), int)
        self.assertIn('low', result['by_severity'])
        self.assertTrue(type(result['by_severity']['low']), int)
        self.assertIn('medium', result['by_severity'])
        self.assertTrue(type(result['by_severity']['medium']), int)
        self.assertIn('high', result['by_severity'])
        self.assertTrue(type(result['by_severity']['high']), int)

        self.assertIn('by_confidence', result)
        self.assertTrue(type(result['by_confidence']), dict)
        self.assertIn('undefined', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['undefined']), int)
        self.assertIn('low', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['low']), int)
        self.assertIn('medium', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['medium']), int)
        self.assertIn('high', result['by_confidence'])
        self.assertTrue(type(result['by_confidence']['high']), int)

        self.assertNotIn('vulns', result)

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_error(self, check_output_mock):
        """Test whether an exception is thrown in case of errors"""

        check_output_mock.side_effect = subprocess.CalledProcessError(-1, "command", output=b'output')

        bandit = Bandit()
        kwargs = {
            'folder_path': os.path.join(self.repo_path, ANALYZER_TEST_FILE),
            'details': False
        }
        with self.assertRaises(GraalError):
            _ = bandit.analyze(**kwargs)


if __name__ == "__main__":
    unittest.main()
