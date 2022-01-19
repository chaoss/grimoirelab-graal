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
#     wmeijer221 <w.meijer.5@student.rug.nl>
#

import unittest

from graal.backends.core.analyzers.lizard import Lizard

from .base_analyzer import (TestCaseAnalyzer, ANALYZER_TEST_FILE)


class TestLizard(TestCaseAnalyzer):
    """Lizard tests"""

    def test_constructor(self):
        """Tests the constructor with different repository levels."""

        liz = Lizard(repository_level=False)
        self.assertEqual(liz.analyze, liz.analyze_files)

        liz = Lizard(repository_level=True)
        self.assertEqual(liz.analyze, liz.analyze_repository)

    def test_analyze_repository_no_details(self):
        """Tests analysis on repository without details"""

        liz = Lizard(repository_level=True)

        kwargs = {
            'worktreepath': self.tmp_data_path,
            'commit': {'files': [ANALYZER_TEST_FILE]},
            'details': False
        }

        results = liz.analyze(**kwargs)

        for result in results:
            self.assertIn('file_path', result)
            self.assertEqual(type(result['file_path']), str)
            self.assertIn('ext', result)
            self.assertEqual(type(result['ext']), str)
            self.assertIn('in_commit', result)
            self.assertEqual(type(result['in_commit']), bool)

            if result['file_path'] == ANALYZER_TEST_FILE:
                self.assertTrue(result['in_commit'])

            self.assertIn('ccn', result)
            self.assertEqual(type(result['ccn']), int)
            self.assertIn('num_funs', result)
            self.assertEqual(type(result['num_funs']), int)
            self.assertIn('loc', result)
            self.assertEqual(type(result['loc']), int)
            self.assertIn('tokens', result)
            self.assertEqual(type(result['tokens']), int)
            self.assertIn('avg_ccn', result)
            self.assertEqual(type(result['avg_ccn']), float)
            self.assertIn('avg_loc', result)
            self.assertEqual(type(result['avg_loc']), float)
            self.assertIn('avg_tokens', result)
            self.assertEqual(type(result['avg_tokens']), float)

    def test_analyze_repository_details(self):
        """Tests analysis on repository with details"""
        # TODO: repository analysis with details is not implemented yet.

    def test_analyze_files_no_details(self):
        """Tests analysis on repository without details"""

        liz = Lizard(repository_level=False)

        kwargs = {
            'commit': {'files': [{'file': ANALYZER_TEST_FILE}]},
            'in_paths': [],
            'details': False,
            'worktreepath': self.tmp_data_path
        }

        results = liz.analyze(**kwargs)

        self.assertEqual(len(results), 1)

        for result in results:
            self.assertIn('file_path', result)
            self.assertEqual(type(result['file_path']), str)
            self.assertIn('ext', result)
            self.assertEqual(type(result['ext']), str)
            self.assertIn('ccn', result)
            self.assertEqual(type(result['ccn']), int)
            self.assertIn('num_funs', result)
            self.assertEqual(type(result['num_funs']), int)
            self.assertIn('loc', result)
            self.assertEqual(type(result['loc']), int)
            self.assertIn('tokens', result)
            self.assertEqual(type(result['tokens']), int)
            self.assertIn('avg_ccn', result)
            self.assertEqual(type(result['avg_ccn']), float)
            self.assertIn('avg_loc', result)
            self.assertEqual(type(result['avg_loc']), float)
            self.assertIn('avg_tokens', result)
            self.assertEqual(type(result['avg_tokens']), float)

    def test_analyze_files_details(self):
        """Tests analysis on repository with details"""

        liz = Lizard(repository_level=False)

        liz = Lizard(repository_level=False)

        kwargs = {
            'commit': {'files': [{'file': ANALYZER_TEST_FILE}]},
            'in_paths': [],
            'details': True,
            'worktreepath': self.tmp_data_path
        }

        results = liz.analyze(**kwargs)

        self.assertEqual(len(results), 1)

        for result in results:
            self.assertIn('file_path', result)
            self.assertEqual(type(result['file_path']), str)
            self.assertIn('ext', result)
            self.assertEqual(type(result['ext']), str)
            self.assertIn('ccn', result)
            self.assertEqual(type(result['ccn']), int)
            self.assertIn('num_funs', result)
            self.assertEqual(type(result['num_funs']), int)
            self.assertIn('loc', result)
            self.assertEqual(type(result['loc']), int)
            self.assertIn('tokens', result)
            self.assertEqual(type(result['tokens']), int)
            self.assertIn('avg_ccn', result)
            self.assertEqual(type(result['avg_ccn']), float)
            self.assertIn('avg_loc', result)
            self.assertEqual(type(result['avg_loc']), float)
            self.assertIn('avg_tokens', result)
            self.assertEqual(type(result['avg_tokens']), float)

            self.assertIn('funs', result)
            self.assertEqual(type(result['funs']), list)

            for fd in result['funs']:
                self.assertIn('ccn', fd)
                self.assertTrue(type(fd['ccn']), int)
                self.assertIn('tokens', fd)
                self.assertTrue(type(fd['tokens']), int)
                self.assertIn('loc', fd)
                self.assertTrue(type(fd['loc']), int)
                self.assertIn('lines', fd)
                self.assertTrue(type(fd['lines']), int)
                self.assertIn('name', fd)
                self.assertTrue(type(fd['name']), str)
                self.assertIn('args', fd)
                self.assertTrue(type(fd['args']), int)
                self.assertIn('start', fd)
                self.assertTrue(type(fd['start']), int)
                self.assertIn('end', fd)
                self.assertTrue(type(fd['end']), int)


if __name__ == "__main__":
    unittest.main()
