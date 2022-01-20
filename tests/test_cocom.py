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

import os
from unicodedata import category
import unittest
import unittest.mock
from build.lib.graal.backends.core.cocom.compositions.composition_lizard_file import LIZARD_FILE
from graal.backends.core import cocom

from graal.graal import GraalError
from graal.graal import GraalCommandArgumentParser

from graal.backends.core.analyzers.cloc import Cloc
from graal.backends.core.analyzers.lizard import Lizard

from graal.backends.core.cocom.compositions.composition_lizard_file import (CATEGORY_COCOM_LIZARD_FILE, LIZARD_FILE)
from graal.backends.core.cocom.compositions.composition_lizard_repository import (
    CATEGORY_COCOM_LIZARD_REPOSITORY, LIZARD_REPOSITORY)
from graal.backends.core.cocom.compositions.composition_scc_file import (CATEGORY_COCOM_SCC_FILE, SCC_FILE)
from graal.backends.core.cocom.compositions.composition_scc_repository import (CATEGORY_COCOM_SCC_REPOSITORY, SCC_REPOSITORY)

from graal.backends.core.cocom import (CoCom, CoComCommand)
from perceval.utils import DEFAULT_DATETIME

from .base_analyzer import (ANALYZER_TEST_FILE,
                            TestCaseAnalyzer)
from .base_repo import TestCaseRepo


class TestCoComBackend(TestCaseRepo):
    """CoCom backend tests"""

    def test_constructor(self):
        """Tests constructor."""

        cc = CoCom('http://example.com', self.git_path, self.worktree_path, tag='test')
        self.assertEqual(cc.uri, 'http://example.com')
        self.assertEqual(cc.gitpath, self.git_path)
        self.assertEqual(cc.worktreepath,
                         os.path.join(self.worktree_path, os.path.split(cc.gitpath)[1]))
        self.assertEqual(cc.origin, 'http://example.com')
        self.assertEqual(cc.tag, 'test')

        cc = CoCom('http://example.com', self.git_path, self.worktree_path,
                   details=True, tag='test')
        self.assertEqual(cc.uri, 'http://example.com')
        self.assertEqual(cc.gitpath, self.git_path)
        self.assertEqual(cc.worktreepath,
                         os.path.join(self.worktree_path, os.path.split(cc.gitpath)[1]))
        self.assertEqual(cc.origin, 'http://example.com')
        self.assertEqual(cc.tag, 'test')

        # When tag is empty or None it will be set to the value in uri
        cc = CoCom('http://example.com', self.git_path, self.worktree_path)
        self.assertEqual(cc.origin, 'http://example.com')
        self.assertEqual(cc.tag, 'http://example.com')

        cc = CoCom('http://example.com', self.git_path, self.worktree_path)
        self.assertEqual(cc.origin, 'http://example.com')
        self.assertEqual(cc.tag, 'http://example.com')

        self.assertGreater(len(cc.CATEGORIES), 0)

    def test_fetch_lizard_file(self):
        """Test whether commits are properly processed via file level"""

        ccom = CoCom('http://example.com', self.git_path, self.worktree_path,
                     in_paths=['perceval/backends/core/github.py'])
        commits = [commit for commit in ccom.fetch(category=CATEGORY_COCOM_LIZARD_FILE)]

        self.assertEqual(len(commits), 1)
        self.assertFalse(os.path.exists(ccom.worktreepath))

        for commit in commits:
            self.assertEqual(commit['backend_name'], 'CoCom')
            self.assertEqual(commit['category'], CATEGORY_COCOM_LIZARD_FILE)
            self.assertIn('data', commit)

            data = commit['data']
            self.assertEqual(data['analysis'][0]['file_path'],
                             'perceval/backends/core/github.py')

            self.assertIn('Author', data)
            self.assertIn('Commit', data)
            self.assertIn('files', data)
            self.assertIn('parents', data)
            self.assertNotIn('refs', data)
            self.assertIn('analyzer', data)
            self.assertEqual(data['analyzer'], LIZARD_FILE)

    def test_fetch_scc_file(self):
        """Test whether commits are properly processed via file level"""

        ccom = CoCom('http://example.com', self.git_path, self.worktree_path,
                     in_paths=['perceval/backends/core/github.py'])
        commits = [commit for commit in ccom.fetch(category=CATEGORY_COCOM_SCC_FILE)]

        self.assertEqual(len(commits), 1)
        self.assertFalse(os.path.exists(ccom.worktreepath))

        for commit in commits:
            self.assertEqual(commit['backend_name'], 'CoCom')
            self.assertEqual(commit['category'], CATEGORY_COCOM_SCC_FILE)

            data = commit['data']
            self.assertEqual(data['analysis'][0]['file_path'],
                             'perceval/backends/core/github.py')

            self.assertIn('Author', data)
            self.assertIn('Commit', data)
            self.assertIn('files', data)
            self.assertIn('parents', data)
            self.assertNotIn('refs', data)
            self.assertIn('analyzer', data)
            self.assertEqual(data['analyzer'], SCC_FILE)

    def test_fetch_lizard_repository(self):
        """Test whether commits are properly processed via repository level"""

        cc = CoCom('http://example.com', self.git_path, self.worktree_path)
        commits = [commit for commit in cc.fetch(category=CATEGORY_COCOM_LIZARD_REPOSITORY)]

        self.assertEqual(len(commits), 6)
        self.assertFalse(os.path.exists(cc.worktreepath))

        for commit in commits:
            self.assertEqual(commit['backend_name'], 'CoCom')
            self.assertEqual(commit['category'], CATEGORY_COCOM_LIZARD_REPOSITORY)
            self.assertIn('data', commit)

            data = commit['data']
            self.assertIn('Author', data)
            self.assertIn('Commit', data)
            self.assertIn('files', data)
            self.assertIn('parents', data)
            self.assertNotIn('refs', data)
            self.assertIn('analyzer', data)
            self.assertEqual(data['analyzer'], LIZARD_REPOSITORY)

    def test_fetch_scc_repository(self):
        """Test whether commits are properly processed via repository level"""

        cc = CoCom('http://example.com', self.git_path, self.worktree_path)
        commits = [commit for commit in cc.fetch(category=CATEGORY_COCOM_SCC_REPOSITORY)]

        self.assertEqual(len(commits), 6)
        self.assertFalse(os.path.exists(cc.worktreepath))

        for commit in commits:
            self.assertEqual(commit['backend_name'], 'CoCom')
            self.assertEqual(commit['category'], CATEGORY_COCOM_SCC_REPOSITORY)
            self.assertIn('data', commit)

            data = commit['data']
            self.assertIn('Author', data)
            self.assertIn('Commit', data)
            self.assertIn('files', data)
            self.assertIn('parents', data)
            self.assertNotIn('refs', data)
            self.assertIn('analyzer', data)
            self.assertEqual(data['analyzer'], SCC_REPOSITORY)

    def test_fetch_unknown(self):
        """Test whether commits are properly processed"""

        cc = CoCom('http://example.com', self.git_path, self.worktree_path)

        with self.assertRaises(GraalError):
            _ = cc.fetch(category="unknown")

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


if __name__ == "__main__":
    unittest.main()
