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
import shutil
import subprocess
import tempfile
import unittest

ANALYZER_TEST_FOLDER = "data/"
ANALYZER_TEST_FILE = "sample_code.py"
DOCKERFILE_TEST = "Dockerfile"


def get_file_path(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


class TestCaseAnalyzer(unittest.TestCase):
    """Base class to test Analyzers"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_path = tempfile.mkdtemp(prefix='graal_')

        data_path = os.path.dirname(os.path.abspath(__file__))
        cls.tmp_data_path = os.path.join(data_path, 'data')

        repo_name = 'graaltest'
        cls.repo_path = os.path.join(cls.tmp_path, repo_name)

        fdout, _ = tempfile.mkstemp(dir=cls.tmp_path)

        zip_path = os.path.join(cls.tmp_data_path, repo_name + '.zip')
        subprocess.check_call(['unzip', '-qq', zip_path, '-d', cls.tmp_path])

        cls.origin_path = os.path.join(cls.tmp_path, repo_name)

        # copy file to tmp_path
        test_analyzer = get_file_path(ANALYZER_TEST_FOLDER + ANALYZER_TEST_FILE)
        shutil.copy2(test_analyzer, cls.tmp_path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)


if __name__ == "__main__":
    unittest.main()
