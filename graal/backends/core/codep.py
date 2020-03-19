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

import logging
import os

from graal.graal import (Graal,
                         GraalCommand,
                         GraalError,
                         GraalRepository,
                         DEFAULT_WORKTREE_PATH)
from graal.backends.core.analyzers.analyzer import Analyzer
from graal.backends.core.analyzers.jadolint import Jadolint, DEPENDENCIES
from graal.backends.core.analyzers.reverse import Reverse
from perceval.utils import DEFAULT_DATETIME, DEFAULT_LAST_DATETIME

PYREVERSE = 'pyreverse'
JADOLINT = 'jadolint'

CATEGORY_CODEP_PYREVERSE = 'code_dependencies_' + PYREVERSE
CATEGORY_CODEP_JADOLINT = 'code_dependencies_' + JADOLINT

logger = logging.getLogger(__name__)


class CoDep(Graal):
    """CoDep backend.

    This class extends the Graal backend. It extract package and class dependencies
    of a Python module to understand its evolution.

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
    version = '0.4.0'

    CATEGORIES = [CATEGORY_CODEP_PYREVERSE, CATEGORY_CODEP_JADOLINT]

    def __init__(self, uri, git_path, worktreepath=DEFAULT_WORKTREE_PATH, exec_path=None,
                 entrypoint=None, in_paths=None, out_paths=None, details=False,
                 tag=None, archive=None):
        super().__init__(uri, git_path, worktreepath, exec_path=exec_path,
                         entrypoint=entrypoint, in_paths=in_paths, out_paths=out_paths, details=details,
                         tag=tag, archive=archive)

        self.analyzer_kind = None
        self.analyzer = None

    def fetch(self, category=CATEGORY_CODEP_PYREVERSE, paths=None,
              from_date=DEFAULT_DATETIME, to_date=DEFAULT_LAST_DATETIME,
              branches=None, latest_items=False):
        """Fetch commits and code (package and class) dependencies information."""

        if not self.entrypoint and category == CATEGORY_CODEP_PYREVERSE:
            raise GraalError(cause="Entrypoint cannot be null")

        if not self.exec_path and category == CATEGORY_CODEP_JADOLINT:
            raise GraalError(cause="Exec path cannot be null")

        if category == CATEGORY_CODEP_PYREVERSE:
            self.analyzer_kind = PYREVERSE
            self.analyzer = PyreverseAnalyzer()
        elif category == CATEGORY_CODEP_JADOLINT:
            self.analyzer_kind = JADOLINT
            self.analyzer = JadolintAnalyzer(self.exec_path, analysis=DEPENDENCIES)
        else:
            raise GraalError(cause="Unknown category %s" % category)

        items = super().fetch(category,
                              from_date=from_date, to_date=to_date,
                              branches=branches, latest_items=latest_items)

        return items

    @staticmethod
    def metadata_category(item):
        """Extracts the category from a Code item.

        This backend generates the following types of item:
        - 'code_dependencies_pyreverse'
        - 'code_dependencies_jadolint'
        """
        if item['analyzer'] == PYREVERSE:
            return CATEGORY_CODEP_PYREVERSE
        elif item['analyzer'] == JADOLINT:
            return CATEGORY_CODEP_JADOLINT
        else:
            raise GraalError(cause="Unknown analyzer %s" % item['analyzer'])

    def _filter_commit(self, commit):
        """Filter a commit according to its data (e.g., author, sha, etc.)

        :param commit: a Perceval commit item

        :returns: a boolean value
        """
        if not self.in_paths:
            return False

        for f in commit['files']:
            for p in self.in_paths:
                if f['file'].endswith(p):
                    return False

        return True

    def _analyze(self, commit):
        """Analyse a snapshot and the corresponding
        checkout version of the repository

        :param commit: a Perceval commit item
        """
        analysis = {}
        if self.analyzer_kind == PYREVERSE:
            module_path = os.path.join(self.worktreepath, self.entrypoint)

            if not GraalRepository.exists(module_path):
                logger.warning("module path %s does not exist at commit %s, analysis will be skipped"
                               % (module_path, commit['commit']))
                return analysis

            analysis = self.analyzer.analyze(module_path)
        else:
            for committed_file in commit['files']:
                file_path = committed_file['file']
                if self.in_paths:
                    found = [p for p in self.in_paths if file_path.endswith(p)]
                    if not found:
                        continue

                local_path = self.worktreepath + '/' + file_path
                if not GraalRepository.exists(local_path):
                    analysis.update({file_path: {DEPENDENCIES: []}})
                    continue

                dependencies = self.analyzer.analyze(local_path)
                analysis.update({file_path: dependencies})

        return analysis

    def _post(self, commit):
        """Remove attributes of the Graal item obtained

        :param commit: a Graal commit item
        """
        commit.pop('Author', None)
        commit.pop('Commit', None)
        commit.pop('files', None)
        commit.pop('parents', None)
        commit.pop('refs', None)
        commit['analyzer'] = self.analyzer_kind

        return commit


class PyreverseAnalyzer(Analyzer):
    """Class to obtain a graph representation of package and class dependencies information
    from a Python module. Such a representation can be then used to plot an UML diagram using common
    visualization libraries.
    """

    def __init__(self):
        self.analyzer = Reverse()

    def analyze(self, module_path):
        """Analyze the content of a Python project using Pyreverse

        :param module_path: folder path

        :returns a dict containing the results of the analysis, like the one below
        {
          'image_path': ..
        }
        """
        kwargs = {'module_path': module_path}
        analysis = self.analyzer.analyze(**kwargs)

        return analysis


class JadolintAnalyzer(Analyzer):
    """Class to obtain a list of dependencies extracted from Dockerfiles."""

    def __init__(self, exec_path, analysis=DEPENDENCIES):
        self.analyzer = Jadolint(exec_path, analysis=analysis)

    def analyze(self, file_path):
        """Analyze the content of a Python project using Jadolint

        :param file_path: path of the target file

        :returns a dict containing the results of the analysis, like the one below
        {
          'image_path': ..
        }
        """
        kwargs = {'file_path': file_path}
        analysis = self.analyzer.analyze(**kwargs)

        return analysis


class CoDepCommand(GraalCommand):
    """Class to run CoDep backend from the command line."""

    BACKEND = CoDep

    @classmethod
    def setup_cmd_parser(cls):
        """Returns the CoDep argument parser."""

        parser = GraalCommand.setup_cmd_parser(cls.BACKEND)

        return parser
