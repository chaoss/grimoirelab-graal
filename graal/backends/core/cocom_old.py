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

from graal.graal import (Graal,
                         GraalError,
                         GraalRepository,
                         GraalCommand,
                         DEFAULT_WORKTREE_PATH)
from graal.backends.core.analyzers.cloc import Cloc
from graal.backends.core.analyzers.lizard import Lizard
from graal.backends.core.analyzers.scc import SCC
from perceval.utils import DEFAULT_DATETIME, DEFAULT_LAST_DATETIME

SCC_FILE = 'scc_file'
SCC_REPOSITORY = 'scc_repository'

LIZARD_FILE = 'lizard_file'
LIZARD_REPOSITORY = 'lizard_repository'

CATEGORY_COCOM_LIZARD_FILE = 'code_complexity_' + LIZARD_FILE
CATEGORY_COCOM_LIZARD_REPOSITORY = 'code_complexity_' + LIZARD_REPOSITORY

CATEGORY_COCOM_SCC_FILE = 'code_complexity_' + SCC_FILE
CATEGORY_COCOM_SCC_REPOSITORY = 'code_complexity_' + SCC_REPOSITORY

logger = logging.getLogger(__name__)


class CoCom(Graal):
    """CoCom backend.

    This class extends the Graal backend. It gathers
    insights about code complexity, such as cyclomatic complexity,
    number of functions and lines of code of a several programming
    languages such as:
        C/C++ (works with C++14)
        Java
        C# (C Sharp)
        JavaScript
        Objective C
        Swift
        Python
        Ruby
        TTCN-3
        PHP
        Scala
        GDScript
        Golang
        Lua

    :param uri: URI of the Git repository
    :param git_path: path to the repository or to the log file
    :param worktreepath: the directory where to store the working tree
    :param exec_path: path of the executable to perform the analysis
    :param entrypoint: the entrypoint of the analysis
    :param in_paths: the target paths of the analysis
    :param out_paths: the paths to be excluded from the analysis
    :param details: if enable, it returns complexity data about each single function found
    :param tag: label used to mark the data
    :param archive: archive to store/retrieve items

    :raises RepositoryError: raised when there was an error cloning or
        updating the repository.
    """
    version = '0.5.1'

    CATEGORIES = [CATEGORY_COCOM_LIZARD_FILE,
                  CATEGORY_COCOM_LIZARD_REPOSITORY,
                  CATEGORY_COCOM_SCC_FILE,
                  CATEGORY_COCOM_SCC_REPOSITORY]

    def __init__(self, uri, git_path, worktreepath=DEFAULT_WORKTREE_PATH, exec_path=None,
                 entrypoint=None, in_paths=None, out_paths=None, details=False,
                 tag=None, archive=None):
        super().__init__(uri, git_path, worktreepath, exec_path=exec_path,
                         entrypoint=entrypoint, in_paths=in_paths, out_paths=out_paths, details=details,
                         tag=tag, archive=archive)

        self.analyzer = None
        self.analyzer_kind = None

    def fetch(self, category=CATEGORY_COCOM_LIZARD_FILE, paths=None,
              from_date=DEFAULT_DATETIME, to_date=DEFAULT_LAST_DATETIME,
              branches=None, latest_items=False):
        """Fetch commits and add code complexity information."""

        items = super().fetch(category,
                              from_date=from_date, to_date=to_date,
                              branches=branches, latest_items=latest_items)
        if category == CATEGORY_COCOM_LIZARD_FILE:
            self.analyzer_kind = LIZARD_FILE
        elif category == CATEGORY_COCOM_LIZARD_REPOSITORY:
            self.analyzer_kind = LIZARD_REPOSITORY
        elif category == CATEGORY_COCOM_SCC_FILE:
            self.analyzer_kind = SCC_FILE
        elif category == CATEGORY_COCOM_SCC_REPOSITORY:
            self.analyzer_kind = SCC_REPOSITORY
        else:
            raise GraalError(cause="Unknown category %s" % category)

        if "_file" in category:
            self.analyzer = FileAnalyzer(self.details, self.analyzer_kind)
        else:
            self.analyzer = RepositoryAnalyzer(self.details, self.analyzer_kind)

        return items

    @staticmethod
    def metadata_category(item):
        """Extracts the category from a Code item.

        This backend generates the following types of item:
        - 'code_complexity_lizard_file'
        - 'code_complexity_lizard_repository'
        - 'code_complexity_scc_file'
        - 'code_complexity_scc_repository'
        """
        if item['analyzer'] == LIZARD_FILE:
            return CATEGORY_COCOM_LIZARD_FILE
        elif item['analyzer'] == LIZARD_REPOSITORY:
            return CATEGORY_COCOM_LIZARD_REPOSITORY
        elif item['analyzer'] == SCC_FILE:
            return CATEGORY_COCOM_SCC_FILE
        elif item['analyzer'] == SCC_REPOSITORY:
            return CATEGORY_COCOM_SCC_REPOSITORY
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
        checkout version of the repository.

        :param commit: a Perceval commit item
        """
        analysis = []

        if self.analyzer_kind in [LIZARD_FILE, SCC_FILE]:
            for committed_file in commit['files']:

                file_path = committed_file['file']
                if self.in_paths:
                    found = [p for p in self.in_paths if file_path.endswith(p)]
                    if not found:
                        continue

                local_path = self.worktreepath + '/' + file_path
                if not GraalRepository.exists(local_path):
                    file_info = {
                        'blanks': None,
                        'comments': None,
                        'loc': None,
                        'ccn': None,
                        'avg_ccn': None,
                        'avg_loc': None,
                        'avg_tokens': None,
                        'num_funs': None,
                        'tokens': None,
                        'file_path': file_path,
                    }
                    if self.details:
                        file_info['funs'] = []

                    if committed_file.get("newfile", None):
                        file_path = committed_file["newfile"]
                        local_path = self.worktreepath + '/' + file_path
                        analysis.append(file_info)
                    elif committed_file.get("action", None) == "D":
                        analysis.append(file_info)
                        continue
                    else:
                        continue

                file_info = self.analyzer.analyze(local_path)
                file_info.update({'file_path': file_path})
                analysis.append(file_info)
        else:
            files_affected = [file_info['file'] for file_info in commit['files']]
            analysis = self.analyzer.analyze(self.worktreepath, files_affected)

        return analysis

    def _post(self, commit):
        """Remove attributes of the Graal item obtained

        :param commit: a Graal commit item
        """
        commit['files'] = [f.replace(self.worktreepath + '/', '') for f in GraalRepository.files(self.worktreepath)]
        commit.pop('refs', None)
        commit['analyzer'] = self.analyzer_kind

        return commit


class FileAnalyzer:
    """Class to analyse the content of files"""

    ALLOWED_EXTENSIONS = ['java', 'py', 'php', 'scala', 'js', 'rb', 'cs', 'cpp', 'c', 'lua', 'go', 'swift']
    FORBIDDEN_EXTENSIONS = ['tar', 'bz2', "gz", "lz", "apk", "tbz2",
                            "lzma", "tlz", "war", "xar", "zip", "zipx"]

    def __init__(self, details=False, kind=LIZARD_FILE):
        self.details = details
        self.kind = kind

        if self.kind == LIZARD_FILE:
            self.cloc = Cloc()
            self.lizard = Lizard()
        else:
            self.scc = SCC()

    def analyze(self, file_path):
        """Analyze the content of a file using CLOC, Lizard and SCC

        :param file_path: file path

        :returns a dict containing the results of the analysis, like the one below
        {
          'blanks': ..,
          'comments': ..,
          'loc': ..,
          'ccn': ..,
          'avg_ccn': ..,
          'avg_loc': ..,
          'avg_tokens': ..,
          'num_funs': ..,
          'tokens': ..,
          'funs': [..]
        }
        """
        kwargs = {'file_path': file_path}

        if self.kind == LIZARD_FILE:
            cloc_analysis = self.cloc.analyze(**kwargs)

            if GraalRepository.extension(file_path) not in self.ALLOWED_EXTENSIONS:
                return cloc_analysis

            kwargs['details'] = self.details
            file_analysis = self.lizard.analyze(**kwargs)
            # the LOC returned by CLOC is replaced by the one obtained with Lizard
            # for consistency purposes

            file_analysis['blanks'] = cloc_analysis['blanks']
            file_analysis['comments'] = cloc_analysis['comments']
        else:
            file_analysis = self.scc.analyze(**kwargs)

        return file_analysis


class RepositoryAnalyzer:
    """Class to analyse the content of a repository

    param kind: the analyzer kind (e.g., Lizard, SCC)
    """

    def __init__(self, details=False, kind=LIZARD_REPOSITORY):
        self.details = details
        self.kind = kind

        if kind == LIZARD_REPOSITORY:
            self.analyzer = Lizard()
        else:
            self.analyzer = SCC()

    def analyze(self, repository_path, files_affected):
        """Analyze the content of a repository using SCC or Lizard.

        :param repository_path: repository path

        :returns a list containing the results of the analysis
        [ {
          'loc': ..,
          'ccn': ..,
          'tokens': ..,
          'num_funs': ..,
          'file_path': ..,
          'in_commit': ..,
          'blanks': ..,
          'comments': ..,
          },
          ...
        ]
        """
        kwargs = {
            'repository_path': repository_path,
            'repository_level': True,
            'files_affected': files_affected,
            'details': self.details
        }

        repository_analysis = self.analyzer.analyze(**kwargs)

        return repository_analysis


class CoComCommand(GraalCommand):
    """Class to run CoCom backend from the command line."""

    BACKEND = CoCom

    @classmethod
    def setup_cmd_parser(cls):
        """Returns the CoCom argument parser."""

        parser = GraalCommand.setup_cmd_parser(cls.BACKEND)

        return parser
