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
import unittest

from base_analyzer import (TestCaseAnalyzer,
                           ANALYZER_TEST_FILE)

from graal.backends.core.analyzers.lizard import Lizard


class TestLizard(TestCaseAnalyzer):
    """Lizard tests"""

    def test_analyze_no_functions(self):
        """Test whether lizard returns the expected fields data"""

        lizard = Lizard()
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE),
                  'functions': False}
        result = lizard.analyze(**kwargs)

        self.assertNotIn('funs_data', result)
        self.assertIn('ccn', result)
        self.assertIn('avg_ccn', result)
        self.assertIn('avg_loc', result)
        self.assertIn('avg_tokens', result)
        self.assertIn('funs', result)
        self.assertIn('loc', result)
        self.assertIn('tokens', result)

    def test_analyze_functions(self):
        """Test whether lizard returns the expected fields data"""

        lizard = Lizard()
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE),
                  'functions': True}
        result = lizard.analyze(**kwargs)

        self.assertIn('ccn', result)
        self.assertIn('avg_ccn', result)
        self.assertIn('avg_loc', result)
        self.assertIn('avg_tokens', result)
        self.assertIn('funs', result)
        self.assertIn('loc', result)
        self.assertIn('tokens', result)
        self.assertIn('funs_data', result)

        for fd in result['funs_data']:
            self.assertIn('ccn', fd)
            self.assertIn('tokens', fd)
            self.assertIn('loc', fd)
            self.assertIn('lines', fd)
            self.assertIn('name', fd)
            self.assertIn('args', fd)
            self.assertIn('start', fd)
            self.assertIn('end', fd)


if __name__ == "__main__":
    unittest.main()
