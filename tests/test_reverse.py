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

from base_analyzer import TestCaseAnalyzer

from graal.backends.core.analyzers.reverse import Reverse


class TestReverse(TestCaseAnalyzer):
    """Reverse tests"""

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


if __name__ == "__main__":
    unittest.main()
