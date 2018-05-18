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
import shutil
import subprocess
import tempfile
import unittest

from base_analyzer import (TestCaseAnalyzer,
                           ANALYZER_TEST_FILE)

from graal.backends.core.analyzers.bandit import Bandit


class TestBandit(TestCaseAnalyzer):
    """Bandit tests"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_path = tempfile.mkdtemp(prefix='graal_')

        data_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(data_path, 'data')

        repo_name = 'graaltest'
        cls.repo_path = os.path.join(cls.tmp_path, repo_name)

        fdout, _ = tempfile.mkstemp(dir=cls.tmp_path)

        zip_path = os.path.join(data_path, repo_name + '.zip')
        subprocess.check_call(['unzip', '-qq', zip_path, '-d', cls.tmp_path])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)

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


if __name__ == "__main__":
    unittest.main()
