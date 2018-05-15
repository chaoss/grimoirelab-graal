# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2018 Bitergia
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
                         DEFAULT_WORKTREE_PATH)
from graal.backends.core.analyzers.lint import Lint
from perceval.backend import BackendCommandArgumentParser
from perceval.utils import DEFAULT_DATETIME, DEFAULT_LAST_DATETIME
from grimoirelab.toolkit.datetime import str_to_datetime

CATEGORY_COQUA = 'code_quality'

logger = logging.getLogger(__name__)


class CoQua(Graal):
    """CoQua backend.

    This class extends the Graal backend. It gathers
    insights about code quality in Python code.

    :param uri: URI of the Git repository
    :param gitpath: path to the repository or to the log file
    :param worktreepath: the directory where to store the working tree
    :param module_path: the path of the module to analyze
    :param tag: label used to mark the data
    :param archive: archive to store/retrieve items

    :raises RepositoryError: raised when there was an error cloning or
        updating the repository.
    """
    version = '0.1.0'

    CATEGORIES = [CATEGORY_COQUA]

    def __init__(self, uri, git_path, worktreepath=DEFAULT_WORKTREE_PATH, module_path=None,
                 tag=None, archive=None):
        super().__init__(uri, git_path, worktreepath, tag=tag, archive=archive)

        if not module_path:
            raise GraalError(cause="module_path cannot be null")

        self.module_path = module_path
        self.module_analyzer = ModuleAnalyzer()
        self.monthly_checkpoints = []

    def fetch(self, category=CATEGORY_COQUA, paths=None,
              from_date=DEFAULT_DATETIME, to_date=DEFAULT_LAST_DATETIME,
              branches=None, latest_items=False):
        """Fetch commits and add code quality information."""

        items = super().fetch(category, paths=paths,
                              from_date=from_date, to_date=to_date,
                              branches=branches, latest_items=latest_items)

        return items

    @staticmethod
    def metadata_category(item):
        """Extracts the category from a Code item.

        This backend only generates one type of item which is
        'code_quality'.
        """
        return CATEGORY_COQUA

    def _filter_commit(self, commit, ncommit, paths=None):
        """Filter a commit according to its data (e.g., author, sha, etc.)

        :param commit: a Perceval commit item
        :param ncommit: commit number (from the initial commit)
        :param paths: a list of paths to drive the filtering

        :returns: a boolean value
        """
        authored_date = str_to_datetime(commit['AuthorDate'])

        checkpoint = '-'.join([str(authored_date.year), str(authored_date.month)])

        if checkpoint in self.monthly_checkpoints:
            return True

        self.monthly_checkpoints.append(checkpoint)
        return False

    def _analyze(self, commit, paths=None):
        """Analyse a snapshot and the corresponding
        checkout version of the repository

        :param commit: a Perceval commit item
        :param paths: a list of paths to narrow the analysis
        """
        module_path = os.path.join(self.worktreepath, self.module_path)

        if not os.path.exists(module_path):
            logger.warning("module path %s does not exist at commit %s, analysis will be skipped"
                           % (module_path, commit['commit']))
            return {}

        analysis = self.module_analyzer.analyze(module_path)

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
        return commit


class ModuleAnalyzer:
    """Class to evaluate code quality in a Python project"""

    def __init__(self):
        self.lint = Lint()

    def analyze(self, module_path):
        """Analyze the content of a module using Pylint

        :param folder_path: folder path

        :returns a dict containing the results of the analysis, like the one below
        {
          'code_quality': ..,
          'modules': [..]
        }
        """
        kwargs = {'module_path': module_path}
        analysis = self.lint.analyze(**kwargs)

        return analysis


class CoQuaCommand(GraalCommand):
    """Class to run CoQua backend from the command line."""

    BACKEND = CoQua

    @staticmethod
    def setup_cmd_parser():
        """Returns the Graal argument parser."""

        parser = BackendCommandArgumentParser(from_date=True, to_date=True)

        # Optional arguments
        group = parser.parser.add_argument_group('Git arguments')
        group.add_argument('--branches', dest='branches',
                           nargs='+', type=str, default=None,
                           help="Fetch commits only from these branches")
        group.add_argument('--latest-items', dest='latest_items',
                           action='store_true',
                           help="Fetch latest commits added to the repository")
        group.add_argument('--worktree-path', dest='worktreepath',
                           default=DEFAULT_WORKTREE_PATH,
                           help="Path where to save the working tree")
        group.add_argument('--paths', dest='paths',
                           nargs='+', type=str, default=None,
                           help="Paths to narrow the analysis")
        group.add_argument('--module-path', dest='module_path',
                           default=None,
                           help="Path where the module is located")

        # Required arguments
        parser.parser.add_argument('uri',
                                   help="URI of the Git log repository")
        parser.parser.add_argument('--git-path', dest='git_path',
                                   help="Path where the Git repository will be cloned")

        return parser
