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
#

import logging
from graal.graal import (Graal,
                         GraalCommand,
                         GraalError,
                         DEFAULT_WORKTREE_PATH)
from graal.backends.core.analyzers.linguist import Linguist
from graal.backends.core.analyzers.cloc import Cloc
from perceval.utils import DEFAULT_DATETIME, DEFAULT_LAST_DATETIME

CLOC = "cloc"
LINGUIST = "linguist"

CATEGORY_COLANG_CLOC = "code_language_" + CLOC
CATEGORY_COLANG_LINGUIST = "code_language_" + LINGUIST

logger = logging.getLogger(__name__)


class CoLang(Graal):
    """CoLang backend.

    This class extends the Graal backend. It extracts
    code language distribution from repository using Linguist

    :param uri: URI of the Git repository
    :param gitpath: path to the repository or to the log file
    :param worktreepath: the directory where to store the working tree
    :param exec_path: path of the executable to perform the analysis
    :param entrypoint: the entrypoint of the analysis
    :param in_paths: the target paths of the analysis
    :param out_paths: the paths to be excluded from the analysis
    :param details: if enable, it returns fine-grained results
    :param tag: label used to mark the data
    :param archive: archive to store/retrieve items

    :raises RepositoryError: raised when there was an error cloning or
        updating the repository.
    """
    version = '0.2.0'

    CATEGORIES = [CATEGORY_COLANG_LINGUIST, CATEGORY_COLANG_CLOC]

    def __init__(self, uri, git_path, worktreepath=DEFAULT_WORKTREE_PATH, exec_path=None,
                 entrypoint=None, in_paths=None, out_paths=None, details=False,
                 tag=None, archive=None):
        super().__init__(uri, git_path, worktreepath, exec_path=exec_path,
                         entrypoint=entrypoint, in_paths=in_paths, out_paths=out_paths, details=details,
                         tag=tag, archive=archive)

        self.repository_path = self.worktreepath
        self.analyzer_kind = None
        self.analyzer = None

    def fetch(self, category=CATEGORY_COLANG_LINGUIST, paths=None,
              from_date=DEFAULT_DATETIME, to_date=DEFAULT_LAST_DATETIME,
              branches=None, latest_items=False):
        """Fetch commits and add code language information."""

        if category == CATEGORY_COLANG_LINGUIST:
            self.analyzer_kind = LINGUIST
        elif category == CATEGORY_COLANG_CLOC:
            self.analyzer_kind = CLOC
        else:
            raise GraalError(cause="Unknown category %s" % category)

        self.repository_analyzer = RepositoryAnalyzer(self.details, self.analyzer_kind)

        items = super().fetch(category, branches=branches, latest_items=latest_items)

        return items

    @staticmethod
    def metadata_category(item):
        """Extracts the category from a Code item.

        This backend generates two types of item which can be:
        'code_language_linguist' or 'code_language_cloc'
        """
        if item['analyzer'] == LINGUIST:
            return CATEGORY_COLANG_LINGUIST
        elif item['analyzer'] == CLOC:
            return CATEGORY_COLANG_CLOC
        else:
            raise GraalError(cause="Unknown analyzer %s" % item['analyzer'])

    def _filter_commit(self, commit):
        """Filter a commit according to its data (e.g., author, sha, etc.)

        :param commit: a Perceval commit item

        :returns: a boolean value
        """
        return False

    def _analyze(self, commit):
        """Analyse a snapshot and the corresponding
        checkout version of the repository

        :param commit: a Perceval commit item
        """

        analysis = self.repository_analyzer.analyze(self.repository_path)

        return analysis

    def _post(self, commit):
        """Remove attributes of the Graal item obtained

        :param commit: a Graal commit item
        """
        commit.pop('files', None)
        commit.pop('parents', None)
        commit.pop('refs', None)
        commit['analyzer'] = self.analyzer_kind
        return commit


class RepositoryAnalyzer:
    """Class to extract code language distribution from a software repository

    :params details: if enable, it returns fine-grained results
    :param kind: the analyzer kind (e.g., LINGUIST, CLOC)
    """

    def __init__(self, details=False, kind=LINGUIST):
        self.details = details
        self.kind = kind

        if kind == LINGUIST:
            self.analyzer = Linguist()
        else:
            self.analyzer = Cloc()

    def analyze(self, repository_path):
        """Analyze the content of a repository using Linguist

        :param repository_path: repository path

        :returns a dict containing the results of the analysis, like the one below
        (for instance, repository is based on Python programming language entirely)
        {
          'Python': 100.0
        }
        """
        kwargs = {
            'repository_path': repository_path,
            'details': self.details
        }

        if self.kind == CLOC:
            kwargs['file_path'] = repository_path
            kwargs['repository_level'] = True
        analysis = self.analyzer.analyze(**kwargs)

        return analysis


class CoLangCommand(GraalCommand):
    """Class to run CoLang backend from the command line."""

    BACKEND = CoLang

    @classmethod
    def setup_cmd_parser(cls):
        """Returns the CoLang argument parser."""

        parser = GraalCommand.setup_cmd_parser(cls.BACKEND)

        return parser
