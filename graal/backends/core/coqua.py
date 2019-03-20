# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2019 Bitergia
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

import logging
import os

from graal.graal import (Graal,
                         GraalCommand,
                         GraalError,
                         GraalRepository,
                         DEFAULT_WORKTREE_PATH)
from graal.backends.core.analyzers.pylint import PyLint
from graal.backends.core.analyzers.flake8 import Flake8
from perceval.utils import DEFAULT_DATETIME, DEFAULT_LAST_DATETIME

PYLINT = "pylint"
FLAKE8 = "flake8"

CATEGORY_COQUA_PYLINT = 'code_quality_' + PYLINT
CATEGORY_COQUA_FLAKE8 = 'code_quality_' + FLAKE8

logger = logging.getLogger(__name__)


class CoQua(Graal):
    """CoQua backend.

    This class extends the Graal backend. It gathers
    insights about code quality in Python code.

    :param uri: URI of the Git repository
    :param gitpath: path to the repository or to the log file
    :param worktreepath: the directory where to store the working tree
    :param entrypoint: the entrypoint of the analysis
    :param in_paths: the target paths of the analysis
    :param out_paths: the paths to be excluded from the analysis
    :param details: if enable, it returns fine-grained results
    :param tag: label used to mark the data
    :param archive: archive to store/retrieve items

    :raises RepositoryError: raised when there was an error cloning or
        updating the repository.
    """
    version = '0.3.0'

    CATEGORIES = [CATEGORY_COQUA_PYLINT, CATEGORY_COQUA_FLAKE8]

    def __init__(self, uri, git_path, worktreepath=DEFAULT_WORKTREE_PATH,
                 entrypoint=None, in_paths=None, out_paths=None, details=False,
                 tag=None, archive=None):
        super().__init__(uri, git_path, worktreepath,
                         entrypoint=entrypoint, in_paths=in_paths, out_paths=out_paths, details=details,
                         tag=tag, archive=archive)

        if not self.entrypoint:
            raise GraalError(cause="Entrypoint cannot be null")

        self.analyzer_kind = None
        self.analyzer = None

    def fetch(self, category=CATEGORY_COQUA_PYLINT, paths=None,
              from_date=DEFAULT_DATETIME, to_date=DEFAULT_LAST_DATETIME,
              branches=None, latest_items=False):
        """Fetch commits and add code quality information."""

        if category == CATEGORY_COQUA_PYLINT:
            self.analyzer_kind = PYLINT
        elif category == CATEGORY_COQUA_FLAKE8:
            self.analyzer_kind = FLAKE8
        else:
            raise GraalError(cause="Unknown category %s" % category)

        self.module_analyzer = ModuleAnalyzer(self.details, self.analyzer_kind)

        items = super().fetch(category,
                              from_date=from_date, to_date=to_date,
                              branches=branches, latest_items=latest_items)

        return items

    @staticmethod
    def metadata_category(item):
        """Extracts the category from a Code item.

        This backend generates two types of item which can be:
        'code_quality_pylint' or 'code_quality_flake8'
        """
        if item['analyzer'] == PYLINT:
            return CATEGORY_COQUA_PYLINT
        elif item['analyzer'] == FLAKE8:
            return CATEGORY_COQUA_FLAKE8
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
        module_path = os.path.join(self.worktreepath, self.entrypoint)

        if not GraalRepository.exists(module_path):
            logger.warning("module path %s does not exist at commit %s, analysis will be skipped"
                           % (module_path, commit['commit']))
            return {}

        analysis = self.module_analyzer.analyze(module_path, self.worktreepath)

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


class ModuleAnalyzer:
    """Class to evaluate code quality in a Python project

    :params details: if enable, it returns fine-grained results
    :param kind: the analyzer kind (e.g., PYLINT, FLAKE8)
    """

    def __init__(self, details=False, kind=PYLINT):
        self.details = details
        self.kind = kind

        if kind == PYLINT:
            self.analyzer = PyLint()
        else:
            self.analyzer = Flake8()

    def analyze(self, module_path, worktree_path):
        """Analyze the content of a module

        :param module_path: module path
        :param worktree_path: worktree path

        :returns a dict containing the results of the analysis, like the one below
        {
          'warnings': [..]
        }
        """
        kwargs = {
            'module_path': module_path,
            'details': self.details
        }
        if self.kind == FLAKE8:
            kwargs['worktree_path'] = worktree_path
        analysis = self.analyzer.analyze(**kwargs)

        return analysis


class CoQuaCommand(GraalCommand):
    """Class to run CoQua backend from the command line."""

    BACKEND = CoQua
