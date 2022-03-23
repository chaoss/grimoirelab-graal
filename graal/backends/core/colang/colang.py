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

from perceval.utils import DEFAULT_DATETIME, DEFAULT_LAST_DATETIME

from graal.graal import Graal, GraalCommand, DEFAULT_WORKTREE_PATH
from graal.backends.core.analyzer_composition_factory import AnalyzerCompositionFactory
from graal.backends.core.colang.compositions.composition_linguist import CATEGORY_COLANG_LINGUIST

CATEGORY_PACKAGE = "graal.backends.core.colang.compositions"
DEFAULT_CATEGORY = CATEGORY_COLANG_LINGUIST


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

    version = '0.2.1'

    def __init__(self, uri, git_path, worktreepath=DEFAULT_WORKTREE_PATH, exec_path=None,
                 entrypoint=None, in_paths=None, out_paths=None, details=False,
                 tag=None, archive=None):
        super().__init__(uri, git_path, worktreepath, exec_path=exec_path,
                         entrypoint=entrypoint, in_paths=in_paths, out_paths=out_paths,
                         details=details, tag=tag, archive=archive)

        self.__factory = AnalyzerCompositionFactory(CATEGORY_PACKAGE)
        self.CATEGORIES = self.__factory.get_categories()
        self.__composer = None

    def fetch(self, category=DEFAULT_CATEGORY, from_date=DEFAULT_DATETIME,
              to_date=DEFAULT_LAST_DATETIME, branches=None, latest_items=False):
        """Fetch commits and add code language information."""

        self.__composer = self.__factory.get_composer(category)

        items = super().fetch(category, from_date=from_date, to_date=to_date,
                              branches=branches, latest_items=latest_items)

        return items

    def _analyze(self, commit):
        """Analyse a snapshot and the corresponding
        checkout version of the repository

        :param commit: a Perceval commit item
        """

        analyzers = self.__composer.get_composition()
        results = []

        kwargs = {
            'commit': commit,
            'worktreepath': self.worktreepath,
            'in_paths': self.in_paths,
            'details': self.details
        }

        for analyzer in analyzers:
            subresult = analyzer.analyze(**kwargs)
            results.append(subresult)

        merged_results = self.__composer.merge_results(results)

        return merged_results

    def _post(self, commit):
        """Remove attributes of the Graal item obtained

        :param commit: a Graal commit item
        """
        commit.pop('files', None)
        commit.pop('parents', None)
        commit.pop('refs', None)
        commit['analyzer'] = self.__composer.get_kind()

        return commit

    @staticmethod
    def metadata_category(item):
        """Extracts the category from a Code item."""

        analyzer = item['analyzer']
        factory = AnalyzerCompositionFactory(CATEGORY_PACKAGE)

        return factory.get_category_from_kind(analyzer)


class CoLangCommand(GraalCommand):
    """Class to run CoLang backend from the command line."""

    BACKEND = CoLang

    @classmethod
    def setup_cmd_parser(cls):
        """Returns the CoLang argument parser."""

        return GraalCommand.setup_cmd_parser(cls.BACKEND)
