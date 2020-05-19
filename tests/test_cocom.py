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
import unittest.mock

from graal.graal import GraalError
from graal.graal import GraalCommandArgumentParser
from graal.backends.core.analyzers.cloc import Cloc
from graal.backends.core.analyzers.lizard import Lizard
from graal.backends.core.cocom import (CATEGORY_COCOM_LIZARD_FILE,
                                       CATEGORY_COCOM_LIZARD_REPOSITORY,
                                       CATEGORY_COCOM_SCC_FILE,
                                       CATEGORY_COCOM_SCC_REPOSITORY,
                                       CoCom,
                                       FileAnalyzer,
                                       RepositoryAnalyzer,
                                       CoComCommand)
from perceval.utils import DEFAULT_DATETIME
from base_analyzer import (ANALYZER_TEST_FILE,
                           TestCaseAnalyzer)
from base_repo import TestCaseRepo


class TestCoComBackend(TestCaseRepo):
    """CoCom backend tests"""

    def test_initialization(self):
        """Test whether attributes are initializated"""

        cc = CoCom('http://example.com', self.git_path, self.worktree_path, tag='test')
        self.assertEqual(cc.uri, 'http://example.com')
        self.assertEqual(cc.gitpath, self.git_path)
        self.assertEqual(cc.worktreepath, os.path.join(self.worktree_path, os.path.split(cc.gitpath)[1]))
        self.assertEqual(cc.origin, 'http://example.com')
        self.assertEqual(cc.tag, 'test')

        cc = CoCom('http://example.com', self.git_path, self.worktree_path, details=True, tag='test')
        self.assertEqual(cc.uri, 'http://example.com')
        self.assertEqual(cc.gitpath, self.git_path)
        self.assertEqual(cc.worktreepath, os.path.join(self.worktree_path, os.path.split(cc.gitpath)[1]))
        self.assertEqual(cc.origin, 'http://example.com')
        self.assertEqual(cc.tag, 'test')

        # When tag is empty or None it will be set to the value in uri
        cc = CoCom('http://example.com', self.git_path, self.worktree_path)
        self.assertEqual(cc.origin, 'http://example.com')
        self.assertEqual(cc.tag, 'http://example.com')

        cc = CoCom('http://example.com', self.git_path, self.worktree_path)
        self.assertEqual(cc.origin, 'http://example.com')
        self.assertEqual(cc.tag, 'http://example.com')

    def test_fetch_lizard_file(self):
        """Test whether commits are properly processed via file level"""

        cc = CoCom('http://example.com', self.git_path, self.worktree_path, in_paths=['perceval/backends/core/github.py'])
        commits = [commit for commit in cc.fetch()]

        self.assertEqual(len(commits), 1)
        self.assertFalse(os.path.exists(cc.worktreepath))

        for commit in commits:
            self.assertEqual(commit['backend_name'], 'CoCom')
            self.assertEqual(commit['category'], CATEGORY_COCOM_LIZARD_FILE)
            self.assertEqual(commit['data']['analysis'][0]['file_path'],
                             'perceval/backends/core/github.py')
            self.assertTrue('Author' in commit['data'])
            self.assertTrue('Commit' in commit['data'])
            self.assertTrue('files' in commit['data'])
            self.assertTrue('parents' in commit['data'])
            self.assertFalse('refs' in commit['data'])

    def test_fetch_scc_file(self):
        """Test whether commits are properly processed via file level"""

        cc = CoCom('http://example.com', self.git_path, self.worktree_path, in_paths=['perceval/backends/core/github.py'])
        commits = [commit for commit in cc.fetch(category="code_complexity_scc_file")]

        self.assertEqual(len(commits), 1)
        self.assertFalse(os.path.exists(cc.worktreepath))

        for commit in commits:
            self.assertEqual(commit['backend_name'], 'CoCom')
            self.assertEqual(commit['category'], CATEGORY_COCOM_SCC_FILE)
            self.assertEqual(commit['data']['analysis'][0]['file_path'],
                             'perceval/backends/core/github.py')
            self.assertTrue('Author' in commit['data'])
            self.assertTrue('Commit' in commit['data'])
            self.assertTrue('files' in commit['data'])
            self.assertTrue('parents' in commit['data'])
            self.assertFalse('refs' in commit['data'])

    def test_fetch_lizard_repository(self):
        """Test whether commits are properly processed via repository level"""

        cc = CoCom('http://example.com', self.git_path, self.worktree_path)
        commits = [commit for commit in cc.fetch(category="code_complexity_lizard_repository")]

        self.assertEqual(len(commits), 6)
        self.assertFalse(os.path.exists(cc.worktreepath))

        for commit in commits:
            self.assertEqual(commit['backend_name'], 'CoCom')
            self.assertEqual(commit['category'], CATEGORY_COCOM_LIZARD_REPOSITORY)
            self.assertTrue('Author' in commit['data'])
            self.assertTrue('Commit' in commit['data'])
            self.assertTrue('files' in commit['data'])
            self.assertTrue('parents' in commit['data'])
            self.assertFalse('refs' in commit['data'])

    def test_fetch_scc_repository(self):
        """Test whether commits are properly processed via repository level"""

        cc = CoCom('http://example.com', self.git_path, self.worktree_path)
        commits = [commit for commit in cc.fetch(category="code_complexity_scc_repository")]

        self.assertEqual(len(commits), 6)
        self.assertFalse(os.path.exists(cc.worktreepath))

        for commit in commits:
            self.assertEqual(commit['backend_name'], 'CoCom')
            self.assertEqual(commit['category'], CATEGORY_COCOM_SCC_REPOSITORY)
            self.assertTrue('Author' in commit['data'])
            self.assertTrue('Commit' in commit['data'])
            self.assertTrue('files' in commit['data'])
            self.assertTrue('parents' in commit['data'])
            self.assertFalse('refs' in commit['data'])

    def test_fetch_unknown(self):
        """Test whether commits are properly processed"""

        cc = CoCom('http://example.com', self.git_path, self.worktree_path)

        with self.assertRaises(GraalError):
            _ = cc.fetch(category="unknown")

    def test_fetch_analysis(self):
        """Test whether commits have properly set values"""

        cc = CoCom('http://example.com', self.git_path, self.worktree_path, details=True)
        commits = [commit for commit in cc.fetch()]

        self.assertEqual(len(commits), 6)
        self.assertFalse(os.path.exists(cc.worktreepath))

        deleted_file_commit = commits[5]

        self.assertEqual(deleted_file_commit['data']['analysis'][0]['file_path'],
                         'perceval/backends/graal.py')
        self.assertEqual(deleted_file_commit['data']['analysis'][0]['blanks'], None)
        self.assertEqual(deleted_file_commit['data']['analysis'][0]['comments'], None)
        self.assertEqual(deleted_file_commit['data']['analysis'][0]['loc'], None)
        self.assertEqual(deleted_file_commit['data']['analysis'][0]['ccn'], None)
        self.assertEqual(deleted_file_commit['data']['analysis'][0]['avg_ccn'], None)
        self.assertEqual(deleted_file_commit['data']['analysis'][0]['avg_loc'], None)
        self.assertEqual(deleted_file_commit['data']['analysis'][0]['avg_tokens'], None)
        self.assertEqual(deleted_file_commit['data']['analysis'][0]['num_funs'], None)
        self.assertEqual(deleted_file_commit['data']['analysis'][0]['tokens'], None)
        self.assertEqual(deleted_file_commit['data']['analysis'][0]['funs'], [])

    def test_metadata_category(self):
        """Test metadata_category"""
        item = {
            "Author": "Nishchith Shetty <inishchith@gmail.com>",
            "AuthorDate": "Tue Feb 26 22:06:31 2019 +0530",
            "Commit": "Nishchith Shetty <inishchith@gmail.com>",
            "CommitDate": "Tue Feb 26 22:06:31 2019 +0530",
            "analysis": [],
            "analyzer": "lizard_file",
            "commit": "5866a479587e8b548b0cb2d591f3a3f5dab04443",
            "message": "[copyright] Update copyright dates"
        }
        self.assertEqual(CoCom.metadata_category(item), CATEGORY_COCOM_LIZARD_FILE)

        item = {
            "Author": "Nishchith Shetty <inishchith@gmail.com>",
            "AuthorDate": "Tue Feb 26 22:06:31 2019 +0530",
            "Commit": "Nishchith Shetty <inishchith@gmail.com>",
            "CommitDate": "Tue Feb 26 22:06:31 2019 +0530",
            "analysis": [],
            "analyzer": "lizard_repository",
            "commit": "5866a479587e8b548b0cb2d591f3a3f5dab04443",
            "message": "[copyright] Update copyright dates"
        }
        self.assertEqual(CoCom.metadata_category(item), CATEGORY_COCOM_LIZARD_REPOSITORY)

        item = {
            "Author": "Nishchith Shetty <inishchith@gmail.com>",
            "AuthorDate": "Tue Feb 26 22:06:31 2019 +0530",
            "Commit": "Nishchith Shetty <inishchith@gmail.com>",
            "CommitDate": "Tue Feb 26 22:06:31 2019 +0530",
            "analysis": [],
            "analyzer": "unknown",
            "commit": "5866a479587e8b548b0cb2d591f3a3f5dab04443",
            "message": "[copyright] Update copyright dates"
        }
        with self.assertRaises(GraalError):
            _ = CoCom.metadata_category(item)


class TestFileAnalyzer(TestCaseAnalyzer):
    """FileAnalyzer tests"""

    def test_init(self):
        """Test initialization"""

        file_analyzer = FileAnalyzer()

        self.assertIsInstance(file_analyzer, FileAnalyzer)
        self.assertIsInstance(file_analyzer.cloc, Cloc)
        self.assertIsInstance(file_analyzer.lizard, Lizard)
        self.assertFalse(file_analyzer.details)

        file_analyzer = FileAnalyzer(details=True)

        self.assertIsInstance(file_analyzer, FileAnalyzer)
        self.assertIsInstance(file_analyzer.cloc, Cloc)
        self.assertIsInstance(file_analyzer.lizard, Lizard)
        self.assertTrue(file_analyzer.details)

    def test_analyze_no_functions(self):
        """Test whether the analyze method works"""

        file_path = os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)
        file_analyzer = FileAnalyzer()
        analysis = file_analyzer.analyze(file_path)

        self.assertNotIn('funs', analysis)
        self.assertIn('ccn', analysis)
        self.assertIn('avg_loc', analysis)
        self.assertIn('avg_tokens', analysis)
        self.assertIn('loc', analysis)
        self.assertIn('tokens', analysis)
        self.assertIn('blanks', analysis)
        self.assertIn('comments', analysis)

    def test_analyze_functions(self):
        """Test whether the analyze method returns functions information"""

        file_path = os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)
        file_analyzer = FileAnalyzer(details=True)
        analysis = file_analyzer.analyze(file_path)

        self.assertIn('ccn', analysis)
        self.assertIn('avg_loc', analysis)
        self.assertIn('avg_tokens', analysis)
        self.assertIn('loc', analysis)
        self.assertIn('tokens', analysis)
        self.assertIn('blanks', analysis)
        self.assertIn('comments', analysis)
        self.assertIn('funs', analysis)

        for fd in analysis['funs']:
            self.assertIn('ccn', fd)
            self.assertIn('tokens', fd)
            self.assertIn('loc', fd)
            self.assertIn('lines', fd)
            self.assertIn('name', fd)
            self.assertIn('args', fd)
            self.assertIn('start', fd)
            self.assertIn('end', fd)


class TestRepositoryAnalyzer(TestCaseAnalyzer):
    """RepositoryAnalyzer tests"""

    def test_init(self):
        """Test initialization"""

        repository_analyzer = RepositoryAnalyzer()

        self.assertIsInstance(repository_analyzer, RepositoryAnalyzer)
        self.assertIsInstance(repository_analyzer.analyzer, Lizard)
        self.assertFalse(repository_analyzer.details)

        repository_analyzer = RepositoryAnalyzer(details=True)

        self.assertIsInstance(repository_analyzer, RepositoryAnalyzer)
        self.assertIsInstance(repository_analyzer.analyzer, Lizard)
        self.assertTrue(repository_analyzer.details)

    def test_analyze(self):
        """Test whether the analyze method works"""

        repository_path = self.tmp_data_path
        repository_analyzer = RepositoryAnalyzer()
        analysis = repository_analyzer.analyze(repository_path, files_affected=[])

        file_analysis = analysis[0]

        self.assertIn('num_funs', file_analysis)
        self.assertIn('ccn', file_analysis)
        self.assertIn('loc', file_analysis)
        self.assertIn('tokens', file_analysis)
        self.assertIn('file_path', file_analysis)
        self.assertIn('in_commit', file_analysis)
        self.assertIn('blanks', file_analysis)
        self.assertIn('comments', file_analysis)


class TestCoComCommand(unittest.TestCase):
    """CoComCommand tests"""

    def test_backend_class(self):
        """Test if the backend class is CoCom"""

        self.assertIs(CoComCommand.BACKEND, CoCom)

    def test_setup_cmd_parser(self):
        """Test setup_cmd_parser"""

        parser = CoComCommand.setup_cmd_parser()
        self.assertIsInstance(parser, GraalCommandArgumentParser)
        self.assertEqual(parser._backend, CoCom)

        args = ['http://example.com/',
                '--git-path', '/tmp/gitpath',
                '--tag', 'test',
                '--from-date', '1970-01-01']

        parsed_args = parser.parse(*args)
        self.assertEqual(parsed_args.uri, 'http://example.com/')
        self.assertEqual(parsed_args.git_path, '/tmp/gitpath')
        self.assertEqual(parsed_args.tag, 'test')
        self.assertEqual(parsed_args.from_date, DEFAULT_DATETIME)


if __name__ == "__main__":
    unittest.main()
