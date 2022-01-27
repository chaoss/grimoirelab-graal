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
#     inishchith <inishchith@gmail.com>
#     Valerio Cosentino <valcos@bitergia.com>
#     Groninger Bugbusters <w.meijer.5@student.rug.nl>
#

import os
import tempfile
import shutil
import subprocess
import unittest
import unittest.mock

from perceval.utils import DEFAULT_DATETIME
from graal.backends.core.analyzer_composition_factory import AnalyzerCompositionFactory

from graal.backends.core.colang.colang import CoLang, CoLangCommand, CATEGORY_PACKAGE
from graal.backends.core.analyzers.linguist import Linguist
from graal.backends.core.analyzers.cloc import Cloc

from graal.backends.core.colang.compositions.composition_linguist import CATEGORY_COLANG_LINGUIST
from graal.backends.core.colang.compositions.composition_cloc import CATEGORY_COLANG_CLOC
from graal.graal import GraalError, GraalCommandArgumentParser

from base_repo import TestCaseRepo
from base_analyzer import ANALYZER_TEST_FILE, TestCaseAnalyzer


class TestCoLangBackend(TestCaseRepo):
    """CoLang backend tests"""

    def test_constructor(self):
        "Tests constructor"

        cl = CoLang('http://example.com', self.git_path,
                    self.worktree_path, tag="test")
        self.assertEqual(cl.uri, 'http://example.com')
        self.assertEqual(cl.gitpath, self.git_path)
        self.assertEqual(cl.worktreepath, os.path.join(
            self.worktree_path, os.path.split(cl.gitpath)[1]))
        self.assertEqual(cl.origin, 'http://example.com')
        self.assertEqual(cl.tag, 'test')

    def test_fetch_linguist(self):
        """Test whether commits are properly processed"""

        cl = CoLang('http://example.com', self.git_path, tag="test")
        commits = [commit for commit in cl.fetch(category=CATEGORY_COLANG_LINGUIST)]

        self.assertEqual(len(commits), 6)
        self.assertFalse(os.path.exists(cl.worktreepath))

        commit = commits[0]
        self.assertEqual(commit['backend_name'], 'CoLang')
        self.assertEqual(commit['category'], CATEGORY_COLANG_LINGUIST)
        result = commit['data']['analysis']
        self.assertNotIn('breakdown', result)

    def test_fetch_cloc(self):
        """Test whether commits are properly processed"""

        cl = CoLang('http://example.com', self.git_path, tag="test")
        commits = [commit for commit in cl.fetch(category=CATEGORY_COLANG_CLOC)]

        self.assertEqual(len(commits), 6)
        self.assertFalse(os.path.exists(cl.worktreepath))

        commit = commits[0]
        self.assertEqual(commit['backend_name'], 'CoLang')
        self.assertEqual(commit['category'], CATEGORY_COLANG_CLOC)
        results = commit['data']['analysis']
        result = results[0]

        self.assertIn('blanks', result)
        self.assertTrue(type(result['blanks']), int)
        self.assertIn('comments', result)
        self.assertTrue(type(result['comments']), int)
        self.assertIn('loc', result)
        self.assertTrue(type(result['loc']), int)

    def test_fetch_unknown(self):
        """Test whether commits are properly processed"""

        cl = CoLang('http://example.com', self.git_path, tag="test")

        with self.assertRaises(GraalError):
            _ = cl.fetch(category="unknown")

    def test_metadata_category(self):
        """Test metadata_category"""

        item = {
            "Author": "Nishchith Shetty <inishchith@gmail.com>",
            "AuthorDate": "Tue Feb 26 22:06:31 2019 +0530",
            "Commit": "Nishchith Shetty <inishchith@gmail.com>",
            "CommitDate": "Tue Feb 26 22:06:31 2019 +0530",
            "analysis": [],
            "analyzer": "linguist",
            "commit": "5866a479587e8b548b0cb2d591f3a3f5dab04443",
            "message": "[copyright] Update copyright dates"
        }
        self.assertEqual(CoLang.metadata_category(item), CATEGORY_COLANG_LINGUIST)

        item = {
            "Author": "Nishchith Shetty <inishchith@gmail.com>",
            "AuthorDate": "Tue Feb 26 22:06:31 2019 +0530",
            "Commit": "Nishchith Shetty <inishchith@gmail.com>",
            "CommitDate": "Tue Feb 26 22:06:31 2019 +0530",
            "analysis": [],
            "analyzer": "cloc",
            "commit": "5866a479587e8b548b0cb2d591f3a3f5dab04443",
            "message": "[copyright] Update copyright dates"
        }
        self.assertEqual(CoLang.metadata_category(item), CATEGORY_COLANG_CLOC)

        item = {
            "Author": "Nishchith Shetty <inishchith@gmail.com>",
            "AuthorDate": "Tue Feb 26 22:06:31 2019 +0530",
            "Commit": "Nishchith Shetty <inishchith@gmail.com>",
            "CommitDate": "Tue Feb 26 22:06:31 2019 +0530",
            "analysis": [],
            "analyzer": "code_language",
            "commit": "5866a479587e8b548b0cb2d591f3a3f5dab04443",
            "message": "[copyright] Update copyright dates"
        }
        with self.assertRaises(GraalError):
            _ = CoLang.metadata_category(item, )


class TestRepositoryAnalyzer(TestCaseAnalyzer):
    """RepositoryAnalyzer tests"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_path = tempfile.mkdtemp(prefix='colang_')
        cls.tmp_repo_path = os.path.join(cls.tmp_path, 'repos')
        os.mkdir(cls.tmp_repo_path)

        data_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(data_path, 'data')

        repo_name = 'graaltest'
        fdout, _ = tempfile.mkstemp(dir=cls.tmp_path)

        zip_path = os.path.join(data_path, repo_name + '.zip')
        subprocess.check_call(['unzip', '-qq', zip_path, '-d', cls.tmp_repo_path])

        cls.origin_path = os.path.join(cls.tmp_repo_path, repo_name)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)

    def test_init(self):
        """Test initialization"""

        factory = AnalyzerCompositionFactory(CATEGORY_PACKAGE)

        # Linguist
        composer = factory.get_composer(CATEGORY_COLANG_LINGUIST)
        composition = composer.get_composition()
        self.assertEqual(len(composition), 1)
        self.assertIsInstance(composition[0], Linguist)

        # Cloc
        composer = factory.get_composer(CATEGORY_COLANG_CLOC)
        composition = composer.get_composition()
        self.assertEqual(len(composition), 1)
        self.assertIsInstance(composition[0], Cloc)

    def test_analyze(self):
        """Test whether the analyze method works"""

        factory = AnalyzerCompositionFactory(CATEGORY_PACKAGE)

        # linguist
        composer = factory.get_composer(CATEGORY_COLANG_LINGUIST)
        composition = composer.get_composition()

        kwargs = {
            'worktreepath': self.origin_path,
            'details': False
        }

        results = [analyzer.analyze(**kwargs) for analyzer in composition]
        results = composer.merge_results(results)

        self.assertIn('Python', results)
        self.assertTrue(type(results['Python']), float)
        self.assertNotIn('breakdown', results)

        # cloc
        composer = factory.get_composer(CATEGORY_COLANG_CLOC)
        composition = composer.get_composition()

        kwargs = {
            'in_paths': [ANALYZER_TEST_FILE],
            'worktreepath': self.origin_path,
        }

        results = [analyzer.analyze(**kwargs) for analyzer in composition]
        results = composer.merge_results(results)

        for result in results:
            self.assertIn('blanks', result)
            self.assertTrue(type(result['blanks']), int)
            self.assertIn('comments', result)
            self.assertTrue(type(result['comments']), int)
            self.assertIn('loc', result)
            self.assertTrue(type(result['loc']), int)
            self.assertIn('total_files', result)
            self.assertTrue(type(result['total_files']), int)


class TestCoLangCommand(unittest.TestCase):
    """CoLangCommand tests"""

    def test_backend_class(self):
        """Test if the backend class is CoLang"""

        self.assertIs(CoLangCommand.BACKEND, CoLang)

    def test_setup_cmd_parser(self):
        """Test setup_cmd_parser"""

        parser = CoLangCommand.setup_cmd_parser()
        self.assertIsInstance(parser, GraalCommandArgumentParser)
        self.assertEqual(parser._backend, CoLang)

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
