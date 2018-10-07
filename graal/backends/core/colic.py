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

from graal.graal import (Graal,
                         GraalRepository,
                         GraalCommand,
                         DEFAULT_WORKTREE_PATH)
from graal.backends.core.analyzers.nomos import Nomos
from perceval.utils import DEFAULT_DATETIME, DEFAULT_LAST_DATETIME

CATEGORY_COLIC = 'code_license'

logger = logging.getLogger(__name__)


class CoLic(Graal):
    """CoLic backend.

    This class extends the Graal backend. It gathers license information
    using Nomos

    :param uri: URI of the Git repository
    :param gitpath: path to the repository or to the log file
    :param worktreepath: the directory where to store the working tree
    :param entrypoint: the entrypoint of the analysis
    :param in_paths: the target paths of the analysis
    :param out_paths: the paths to be excluded from the analysis
    :param tag: label used to mark the data
    :param archive: archive to store/retrieve items

    :raises RepositoryError: raised when there was an error cloning or
        updating the repository.
    """
    version = '0.2.2'

    CATEGORIES = [CATEGORY_COLIC]

    def __init__(self, uri, git_path, worktreepath=DEFAULT_WORKTREE_PATH,
                 entrypoint=None, in_paths=None, out_paths=None,
                 tag=None, archive=None):
        super().__init__(uri, git_path, worktreepath,
                         entrypoint=entrypoint, in_paths=in_paths, out_paths=out_paths,
                         tag=tag, archive=archive)
        self.license_analyzer = LicenseAnalyzer()

    def fetch(self, category=CATEGORY_COLIC, paths=None,
              from_date=DEFAULT_DATETIME, to_date=DEFAULT_LAST_DATETIME,
              branches=None, latest_items=False):
        """Fetch commits and add license information."""

        items = super().fetch(category,
                              from_date=from_date, to_date=to_date,
                              branches=branches, latest_items=latest_items)

        return items

    @staticmethod
    def metadata_category(item):
        """Extracts the category from a Code item.

        This backend only generates one type of item which is
        'code_complexity'.
        """
        return CATEGORY_COLIC

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
        files = GraalRepository.files(self.worktreepath)
        analysis = []

        for file_path in files:

            if self.in_paths:
                found = [p for p in self.in_paths if file_path.endswith(p)]
                if not found:
                    continue

            license_info = self.license_analyzer.analyze(file_path)
            license_info.update({'file_path': file_path.replace(self.worktreepath + '/', "")})
            analysis.append(license_info)

        return analysis

    def _post(self, commit):
        """Remove attributes of the Graal item obtained

        :param commit: a Graal commit item
        """
        commit.pop('files', None)
        commit.pop('parents', None)
        commit.pop('refs', None)
        return commit


class LicenseAnalyzer:
    """Class to analyse the content of files"""

    def __init__(self):
        self.nomos = Nomos()

    def analyze(self, file_path):
        """Analyze the content of a file using Nomos

        :param file_path: file path

        :returns a dict containing the results of the analysis, like the one below
        {
          'licenses': [..]
        }
        """
        kwargs = {'file_path': file_path}
        analysis = self.nomos.analyze(**kwargs)

        return analysis


class CoLicCommand(GraalCommand):
    """Class to run CoLic backend from the command line."""

    BACKEND = CoLic
