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
from graal.backends.core.analyzers.bandit import Bandit
from perceval.utils import DEFAULT_DATETIME, DEFAULT_LAST_DATETIME

CATEGORY_COVULN = 'code_vulnerabilities'

logger = logging.getLogger(__name__)


class CoVuln(Graal):
    """CoVuln backend.

    This class extends the Graal backend. It gathers
    insights about security vulnerabilities in Python code.

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
    version = '0.3.0'

    CATEGORIES = [CATEGORY_COVULN]

    def __init__(self, uri, git_path, worktreepath=DEFAULT_WORKTREE_PATH, exec_path=None,
                 entrypoint=None, in_paths=None, out_paths=None, details=False,
                 tag=None, archive=None):
        super().__init__(uri, git_path, worktreepath, exec_path=exec_path,
                         entrypoint=entrypoint, in_paths=in_paths, out_paths=out_paths, details=details,
                         tag=tag, archive=archive)

        if not self.entrypoint:
            raise GraalError(cause="Entrypoint cannot be null")

        self.vuln_analyzer = VulnAnalyzer(self.details)

    def fetch(self, category=CATEGORY_COVULN, paths=None,
              from_date=DEFAULT_DATETIME, to_date=DEFAULT_LAST_DATETIME,
              branches=None, latest_items=False):
        """Fetch commits and add code vulnerabilities information."""

        items = super().fetch(category,
                              from_date=from_date, to_date=to_date,
                              branches=branches, latest_items=latest_items)

        return items

    @staticmethod
    def metadata_category(item):
        """Extracts the category from a Code item.

        This backend only generates one type of item which is
        'code_quality'.
        """
        return CATEGORY_COVULN

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
        module_path = self.worktreepath
        if self.entrypoint:
            module_path = os.path.join(self.worktreepath, self.entrypoint)

            if not GraalRepository.exists(module_path):
                logger.warning("module path %s does not exist at commit %s, analysis will be skipped"
                               % (module_path, commit['commit']))
                return {}

        analysis = self.vuln_analyzer.analyze(module_path)

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


class VulnAnalyzer:
    """Class to identify security vulnerabilities in a Python project"""

    def __init__(self, details=False):
        self.details = details
        self.bandit = Bandit()

    def analyze(self, folder_path):
        """Analyze the content of a folder using Bandit

        :param folder_path: folder path

        :returns a dict containing the results of the analysis, like the one below
        {
          'code_quality': ..,
          'modules': [..]
        }
        """
        kwargs = {
            'folder_path': folder_path,
            'details': self.details
        }
        analysis = self.bandit.analyze(**kwargs)

        return analysis


class CoVulnCommand(GraalCommand):
    """Class to run CoVuln backend from the command line."""

    BACKEND = CoVuln

    @classmethod
    def setup_cmd_parser(cls):
        """Returns the CoVuln argument parser."""

        parser = GraalCommand.setup_cmd_parser(cls.BACKEND)

        return parser
