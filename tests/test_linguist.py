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
#     Nishchith Shetty <inishchith@gmail.com>
#

import os
import shutil
import subprocess
import tempfile
import unittest
import unittest.mock

from base_analyzer import TestCaseAnalyzer

from graal.backends.core.analyzers.linguist import Linguist


class TestLinguist(TestCaseAnalyzer):
    """Linguist tests"""

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
