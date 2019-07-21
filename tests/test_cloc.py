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
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Valerio Cosentino <valcos@bitergia.com>
#

import os
import shutil
import subprocess
import tempfile
import unittest
import unittest.mock

from base_analyzer import (TestCaseAnalyzer,
                           ANALYZER_TEST_FILE)

from graal.backends.core.analyzers.cloc import Cloc
from graal.graal import GraalError


class TestCloc(TestCaseAnalyzer):
    """Cloc tests"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_path = tempfile.mkdtemp(prefix='cloc_')
        cls.tmp_repo_path = os.path.join(cls.tmp_path, 'repos')
        os.mkdir(cls.tmp_repo_path)

        data_path = os.path.dirname(os.path.abspath(__file__))
        cls.data_path = os.path.join(data_path, 'data')

        repo_name = 'graaltest'
        fdout, _ = tempfile.mkstemp(dir=cls.tmp_path)

        zip_path = os.path.join(cls.data_path, repo_name + '.zip')
        subprocess.check_call(['unzip', '-qq', zip_path, '-d', cls.tmp_repo_path])

        cls.origin_path = os.path.join(cls.tmp_repo_path, repo_name)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)

    def test_analyze(self):
        """Test whether cloc returns the expected fields data"""

        cloc = Cloc()
        kwargs = {'file_path': os.path.join(self.data_path, ANALYZER_TEST_FILE)}
        result = cloc.analyze(**kwargs)

        self.assertIn('blanks', result)
        self.assertTrue(type(result['blanks']), int)
        self.assertTrue(result['blanks'], 27)
        self.assertIn('comments', result)
        self.assertTrue(type(result['comments']), int)
        self.assertTrue(result['comments'], 31)
        self.assertIn('loc', result)
        self.assertTrue(type(result['loc']), int)
        self.assertTrue(result['loc'], 67)

    def test_analyze_repository_level(self):
        """Test whether cloc returns the expected fields data for repository level"""

        cloc = Cloc()
        kwargs = {
            'file_path': self.origin_path,
            'repository_level': True
        }
        results = cloc.analyze(**kwargs)
        result = results[next(iter(results))]

        self.assertIn('blanks', result)
        self.assertTrue(type(result['blanks']), int)
        self.assertIn('comments', result)
        self.assertTrue(type(result['comments']), int)
        self.assertIn('loc', result)
        self.assertTrue(type(result['loc']), int)
        self.assertIn('total_files', result)
        self.assertTrue(type(result['total_files']), int)

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_error(self, check_output_mock):
        """Test whether an exception is thrown in case of errors"""

        check_output_mock.side_effect = subprocess.CalledProcessError(-1, "command", output=b'output')

        cloc = Cloc()
        kwargs = {'file_path': os.path.join(self.data_path, ANALYZER_TEST_FILE)}
        with self.assertRaises(GraalError):
            _ = cloc.analyze(**kwargs)


if __name__ == "__main__":
    unittest.main()
