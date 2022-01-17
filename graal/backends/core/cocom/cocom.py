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

from graal.graal import (Graal, GraalCommand, DEFAULT_WORKTREE_PATH, GraalError, GraalRepository)
from .cocom_analyzer_factory import CoComAnalyzerFactory
from graal.backends.core.composer import Composer
from perceval.utils import DEFAULT_DATETIME, DEFAULT_LAST_DATETIME


class CoCom(Graal):
    """CoCom Backend"""

    version = "0.5.2"

    def __init__(self, uri, git_path, worktreepath=DEFAULT_WORKTREE_PATH,
                 exec_path=None, entrypoint=None, in_paths=None,
                 out_paths=None, details=False, tag=None, archive=None):
        super().__init__(uri, git_path, worktreepath, exec_path=exec_path,
                         entrypoint=entrypoint, in_paths=in_paths, out_paths=out_paths, details=details,
                         tag=tag, archive=archive)

        self.factory = CoComAnalyzerFactory()
        self.CATEGORIES = self.factory.get_categories()
        self.composer = None

    # TODO: wouldn't be a bad idea to introduce parameter object.
    # TODO: could we concatenate categories, and compose them that way?
    #       That'd remove the need for a factory as you can dynamically
    #       load the analyzers.
    def fetch(self, category, from_date=DEFAULT_DATETIME, to_date=DEFAULT_LAST_DATETIME,
              branches=None, latest_items=False):
        """Fetch commits and add code complexity information."""

        items = super().fetch(category, from_date=from_date, to_date=to_date,
                              branches=branches, latest_items=latest_items)

        self.composer = self.factory.get_composer(category)

        return items

    def _filter_commit(self, commit):
        """Filters when changed commit files
        are not inside target directory

        :param commit: a Perceval commit item
        :returns: a boolean value
        """

        if not self.in_paths:
            return False

        for file in commit['files']:
            for path in self.in_paths:
                if file['file'].endswith(path):
                    return False

        return True

    def _analyze(self, commit):
        """Analyse a commit and the corresponding
        checkout version of the repository.

        :param commit: a Perceval commit item
        :returns: a boolean value
        """

        if not self.composer:
            raise GraalError(msg="running analyze without having set an analyzer")

        results = []

        # TODO: take out the kwargs and make a parameter object? 
        #       the data sent is always the same, so no need for abstraction.
        analyzers = self.composer.get_composition()
        for analyzer in analyzers:
            sub_analysis = analyzer.analyze(commit=commit, details=self.details,
                                            in_paths=self.in_paths, worktreepath=self.worktreepath)
            results.append(sub_analysis)

        merged_results = self.composer.merge_results(results)

        return merged_results

    def _post(self, commit):
        """Remove attributes of the Graal item obtained

        :param commit: a Graal commit item
        """

        commit['files'] = [f.replace(self.worktreepath + '/', '')
                           for f in GraalRepository.files(self.worktreepath)]
        commit.pop('refs', None)
        commit['analyzer'] = self.composer.get_kind()

        return commit

    @staticmethod
    def metadata_category(item):
        """Extracts the category from a Code item."""

        # TODO: analyzers essentially have two keys, kind and category: why?
        analyzer = item['analyzer']

        print(f'{analyzer=}')
        factory = CoComAnalyzerFactory()
        composer = factory.get_composer(analyzer)

        return composer.get_category()


class CoComCommand(GraalCommand):
    """Class to run CoCom backend from the command line."""

    BACKEND = CoCom
