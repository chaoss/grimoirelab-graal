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
#     James Walden <james.walden@acm.org>
#     Valerio Cosentino <valcos@bitergia.com>
#     inishchith <inishchith@gmail.com>
#

import os
import subprocess
import unittest.mock

from base_analyzer import (TestCaseAnalyzer,
                           ANALYZER_TEST_C_FILE)
from base_repo import TestCaseRepo

from graal.backends.core.analyzers.qmcalc import QMCalc
from graal.graal import GraalError


class TestQMCalc(TestCaseAnalyzer):
    """QMCalc tests"""

    def test_initialization(self):
        """Test whether attributes are initializated"""

        qmc = QMCalc()
        self.assertEqual(len(qmc.metrics_names), 111)

    def test_analyze_fields_present(self):
        """Test whether qmcalc returns the expected fields """

        qmc = QMCalc()
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_C_FILE)}
        result = qmc.analyze(**kwargs)

        for metric_name in qmc.metrics_names:
            self.assertIn(metric_name, result)

    def test_analyze_c(self):
        """Test whether qmcalc returns expected code metric values"""

        qmc = QMCalc()
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_C_FILE)}
        result = qmc.analyze(**kwargs)

        self.assertEqual(result['nchar'], 839)
        self.assertEqual(result['nline'], 44)
        self.assertEqual(result['nfunction'], 3)
        self.assertEqual(result['nfunction'], result['nfunction2'])
        self.assertEqual(result['identifier_length_max'], 14)
        self.assertEqual(result['identifier_length_min'], 1)
        self.assertEqual(result['line_length_min'], 0)
        self.assertEqual(result['line_length_median'], 15.5)
        self.assertEqual(result['line_length_max'], 73)
        self.assertEqual(result['ncpp_directive'], 5)
        self.assertEqual(result['ncpp_conditional'], 1)
        self.assertEqual(result['ncpp_include'], 2)
        self.assertEqual(result['ncomment'], 1)
        self.assertEqual(result['nconst'], 1)
        self.assertEqual(result['nenum'], 0)
        self.assertEqual(result['ngoto'], 0)
        self.assertEqual(result['nsigned'], 0)
        self.assertEqual(result['nstruct'], 0)
        self.assertEqual(result['nunion'], 0)
        self.assertEqual(result['nunsigned'], 1)
        self.assertEqual(result['nvoid'], 2)
        self.assertAlmostEqual(result['halstead_mean'], 124.599, 2)
        self.assertAlmostEqual(result['halstead_median'], 114.714, 2)
        self.assertAlmostEqual(result['halstead_max'], 228.898, 2)
        self.assertAlmostEqual(result['halstead_min'], 30.185, 2)
        self.assertEqual(result['statement_nesting_max'], 2)

class TestQMCalcRepo(TestCaseRepo):
    repo_name = 'BSDCoreUtils'

    def test_analyze_repository_level_summary(self):
        """Test metric summary values for repository."""

        qmc = QMCalc()
        origin_path = os.path.join(self.tmp_repo_path, self.repo_name)
        kwargs = {
            'repository_path': origin_path,
            'repository_level': True
        }
        results = qmc.analyze(**kwargs)
        self.assertEqual(results['nfiles'], 186)
        self.assertEqual(results['nline'], 43440)
        self.assertEqual(results['nfunction'], 892)
        self.assertEqual(results['ngoto'], 161)
        self.assertAlmostEqual(results['halstead_mean'], 605.45, 2)
        self.assertAlmostEqual(results['halstead_median'], 332.97, 2)
        self.assertAlmostEqual(results['halstead_max'], 11686.9, 2)
        self.assertAlmostEqual(results['halstead_min'], 0, 2)
        self.assertAlmostEqual(results['halstead_sd'], 551.99, 2)
        self.assertEqual(results['statement_nesting_max'], 9)

    def test_analyze_repository_level_files(self):
        """Test metric values for a single file from repository."""

        qmc = QMCalc()
        origin_path = os.path.join(self.tmp_repo_path, self.repo_name)
        kwargs = {
            'repository_path': origin_path,
            'repository_level': True
        }
        results = qmc.analyze(**kwargs)
        result = results['files'][-1] # strlcpy.c

        self.assertEqual(result['nchar'], 1686)
        self.assertEqual(result['nline'], 54)
        self.assertEqual(result['nfunction'], 1)
        self.assertAlmostEqual(result['cyclomatic_mean'], 7.0, 1)
        self.assertAlmostEqual(result['cyclomatic_median'], 7.0, 1)
        self.assertAlmostEqual(result['cyclomatic_max'], 7.0, 1)
        self.assertAlmostEqual(result['cyclomatic_min'], 7.0, 1)
        self.assertEqual(result['statement_nesting_max'], 5)

if __name__ == "__main__":
    unittest.main()
