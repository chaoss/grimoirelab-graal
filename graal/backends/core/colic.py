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
                         GraalError,
                         GraalRepository,
                         GraalCommand,
                         DEFAULT_WORKTREE_PATH)
from graal.backends.core.analyzers.nomos import Nomos
from graal.backends.core.analyzers.scancode import ScanCode
from perceval.utils import DEFAULT_DATETIME, DEFAULT_LAST_DATETIME

NOMOS = 'nomos'
SCANCODE = 'scancode'
SCANCODE_CLI = 'scancode_cli'

CATEGORY_COLIC_NOMOS = 'code_license_' + NOMOS
CATEGORY_COLIC_SCANCODE = 'code_license_' + SCANCODE
CATEGORY_COLIC_SCANCODE_CLI = 'code_license_' + SCANCODE_CLI

logger = logging.getLogger(__name__)


class CoLic(Graal):
    """CoLic backend.

    This class extends the Graal backend. It gathers license & copyright information
    using Nomos, Scancode or Scancode-cli

    :param uri: URI of the Git repository
    :param git_path: path to the repository or to the log file
    :param worktreepath: the directory where to store the working tree
    :param exec_path: path of the executable
    :param entrypoint: the entrypoint of the analysis
    :param in_paths: the target paths of the analysis
    :param out_paths: the paths to be excluded from the analysis
    :param tag: label used to mark the data
    :param archive: archive to store/retrieve items

    :raises RepositoryError: raised when there was an error cloning or
        updating the repository.
    """
    version = '0.6.0'

    CATEGORIES = [CATEGORY_COLIC_NOMOS,
                  CATEGORY_COLIC_SCANCODE,
                  CATEGORY_COLIC_SCANCODE_CLI]

    def __init__(self, uri, git_path, worktreepath=DEFAULT_WORKTREE_PATH, exec_path=None,
                 entrypoint=None, in_paths=None, out_paths=None,
                 tag=None, archive=None):
        super().__init__(uri, git_path, worktreepath, exec_path=exec_path,
                         entrypoint=entrypoint, in_paths=in_paths, out_paths=out_paths,
                         tag=tag, archive=archive)

        if not GraalRepository.exists(exec_path):
            raise GraalError(cause="executable path %s not valid" % exec_path)

        self.analyzer_kind = None
        self.analyzer = None

    def fetch(self, category=CATEGORY_COLIC_NOMOS, paths=None,
              from_date=DEFAULT_DATETIME, to_date=DEFAULT_LAST_DATETIME,
              branches=None, latest_items=False):
        """Fetch commits and add license information."""

        if category == CATEGORY_COLIC_SCANCODE:
            self.analyzer_kind = SCANCODE
        elif category == CATEGORY_COLIC_SCANCODE_CLI:
            self.analyzer_kind = SCANCODE_CLI
        elif category == CATEGORY_COLIC_NOMOS:
            self.analyzer_kind = NOMOS
        else:
            raise GraalError(cause="Unknown category %s" % category)

        self.analyzer = LicenseAnalyzer(self.exec_path, self.analyzer_kind)

        items = super().fetch(category,
                              from_date=from_date, to_date=to_date,
                              branches=branches, latest_items=latest_items)

        return items

    @staticmethod
    def metadata_category(item):
        """Extracts the category from a Code item.

        This backend generates the following types of item:
        - 'code_license_nomos'
        - 'code_license_scancode'
        - 'code_license_scancode_cli'
        """
        if item['analyzer'] == NOMOS:
            return CATEGORY_COLIC_NOMOS
        elif item['analyzer'] == SCANCODE:
            return CATEGORY_COLIC_SCANCODE
        elif item['analyzer'] == SCANCODE_CLI:
            return CATEGORY_COLIC_SCANCODE_CLI
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
        """Analyse a commit and the corresponding
        checkout version of the repository

        :param commit: a Perceval commit item
        """
        analysis = []
        files_to_process = []

        for committed_file in commit['files']:
            file_path = committed_file['file']
            local_path = self.worktreepath + '/' + file_path

            if self.in_paths:
                found = [p for p in self.in_paths if file_path.endswith(p)]
                if not found:
                    continue

            # Skip files that don't exist, directories and soft links
            if not GraalRepository.exists(local_path) or os.path.isdir(local_path) or os.path.islink(local_path):
                continue

            if self.analyzer_kind == NOMOS or self.analyzer_kind == SCANCODE:
                license_info = self.analyzer.analyze(local_path)
                license_info.update({'file_path': file_path})
                analysis.append(license_info)
            elif self.analyzer_kind == SCANCODE_CLI:
                files_to_process.append((file_path, local_path))

        if files_to_process:
            local_paths = [path[1] for path in files_to_process]
            analysis = self.analyzer.analyze(local_paths)
            for i in range(len(analysis)):
                analysis[i]['file_path'] = files_to_process[i][0]

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


class LicenseAnalyzer:
    """Class to analyse the content of files

    :param exec_path: path of the license analyzer executable
    :param kind: the analyzer kind (e.g., NOMOS, SCANCODE, SCANCODE_CLI)
    """

    def __init__(self, exec_path, kind=NOMOS):
        self.kind = kind
        if kind == SCANCODE:
            self.analyzer = ScanCode(exec_path)
        elif kind == SCANCODE_CLI:
            self.analyzer = ScanCode(exec_path, cli=True)
        else:
            self.analyzer = Nomos(exec_path)

    def analyze(self, file_path):
        """Analyze the content of a file using Nomos/Scancode

        :param file_path: file path (in case of scancode)
        :param file_paths: file paths ( in case of scancode_cli for concurrent execution on files )

        :returns a dict containing the results of the analysis, like the one below
        {
          'licenses': [..],
          'copyrights': [..]
        }
        """
        if self.kind == SCANCODE_CLI:
            kwargs = {'file_paths': file_path}
        else:
            kwargs = {'file_path': file_path}

        analysis = self.analyzer.analyze(**kwargs)

        return analysis


class CoLicCommand(GraalCommand):
    """Class to run CoLic backend from the command line."""

    BACKEND = CoLic

    @classmethod
    def setup_cmd_parser(cls):
        """Returns the CoLic argument parser."""

        parser = GraalCommand.setup_cmd_parser(cls.BACKEND)

        return parser
