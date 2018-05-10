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

from graal.backends.core.analyzers.cloc import Cloc


class TestCloc(TestCaseAnalyzer):
    """Cloc tests"""

    def test_analyze(self):
        """Test whether cloc returns the expected fields data"""

        cloc = Cloc()
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)}
        result = cloc.analyze(**kwargs)

        self.assertIn('blanks', result)
        self.assertIn('comments', result)
        self.assertIn('loc', result)


if __name__ == "__main__":
    unittest.main()
