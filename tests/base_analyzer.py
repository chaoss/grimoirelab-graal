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
import tempfile
import unittest

ANALYZER_TEST_FOLDER = "data/"
ANALYZER_TEST_FILE = "sample_code.py"


def get_file_path(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


class TestCaseAnalyzer(unittest.TestCase):
    """Base class to test Analyzers"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_path = tempfile.mkdtemp(prefix='analyzers_')
        cls.tmp_data_path = os.path.join(cls.tmp_path, 'data')
        os.mkdir(cls.tmp_data_path)

        test_analyzer = get_file_path(ANALYZER_TEST_FOLDER + ANALYZER_TEST_FILE)
        shutil.copy2(test_analyzer, cls.tmp_data_path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)


if __name__ == "__main__":
    unittest.main()
