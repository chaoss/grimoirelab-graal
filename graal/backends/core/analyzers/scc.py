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
#     wmeijer221 <w.meijer.5@student.rug.nl>
#

import os
import subprocess

from graal.graal import GraalRepository
from .analyzer import Analyzer, is_in_paths


class SCC(Analyzer):
    """
    A wrapper for SCC.

    This class allows to call SCC over a file, parses
    the result of the analysis and returns it as a dict.
    """
    version = '0.1.1'

    def __init__(self, repository_level):
        """
        Sets up SCC analysis.

        :param repository_level: determines analysis method (repository- or file-level)
        """

        self.analyze = self.analyze_repository if repository_level else self.analyze_files

    def analyze_repository(self, **kwargs):
        """
        Add information LOC, total files, blank, commented lines and code
        complexity using SCC for the entire repository.

        :param worktreepath: the directory where to store the working tree

        :returns result: dict of the results of the analysis over a repository
        """

        worktreepath = kwargs['worktreepath']
        message = self.__decode_scc_command(worktreepath)

        results = {}
        flag = False

        for line in message.strip().split("\n"):
            if flag:
                if line.lower().startswith("total"):
                    break

                elif not line.startswith("────────"):
                    digested_split = line.split()
                    language, files_info = digested_split[:-6], digested_split[-6:]
                    language = " ".join(language)
                    total_files, total_lines, blank_lines, commented_lines, loc, complexity = map(int, files_info)

                    language_result = {
                        "total_files": total_files,
                        "total_lines": total_lines,
                        "blanks": blank_lines,
                        "comments": commented_lines,
                        "loc": loc,
                        "ccn": complexity
                    }
                    results[language] = language_result

            if line.lower().startswith("language"):
                flag = True

        return results

    def analyze_files(self, **kwargs):
        """
        Performs SCC analysis on all changed files in the repository.

        :param commit: the changed files of this commit are analyzed
        :param in_paths: the target paths of the analysis
        :param worktreepath: the directory where to store the working tree
        
        :returns: array of dictionaries with SCC analysis results.
        """

        commit = kwargs["commit"]
        in_paths = kwargs["in_paths"]
        worktreepath = kwargs["worktreepath"]

        results = []
        for commit_file in commit['files']:
            file_path = commit_file['file']

            if not is_in_paths(in_paths, file_path):
                continue

            result = self.__analyze_file(worktreepath, file_path)
            results.append(result)

        return results

    def __analyze_file(self, worktreepath, file_path):
        """Add information about LOC, blank and commented lines using SCC for a given file

        :param worktreepath: the directory where to store the working tree
        :param file_path: path of the file that is analyzed

        :returns result: dict of the results of the analysis over a file
        """

        target_path = os.path.join(worktreepath, file_path)
        message = self.__decode_scc_command(target_path)

        flag = False
        results = {
            "file_path": file_path,
            "ext": GraalRepository.extension(file_path),
            "blanks": 0,
            "comments": 0,
            "loc": 0,
            "ccn": 0
        }

        for line in message.strip().split("\n"):
            if flag and not line.startswith("────────"):
                file_info = line.split()[-4:]
                blank_lines, commented_lines, loc, complexity = map(int, file_info)
                results["blanks"] = blank_lines
                results["comments"] = commented_lines
                results["loc"] = loc
                results["ccn"] = complexity
                break

            if line.lower().startswith("language"):
                flag = True

        return results

    def __decode_scc_command(self, target_path):
        """
        Decodes SCC command and returns its message.

        :param target_path: targeted file/directory

        :returns: SCC output message
        """

        try:
            scc_command = ['scc', target_path]
            message = subprocess.check_output(scc_command).decode("utf-8")
        except subprocess.CalledProcessError as error:
            message = error.output.decode("utf-8")
        finally:
            subprocess._cleanup()

        return message
