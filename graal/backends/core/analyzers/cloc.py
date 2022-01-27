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
#     Groninger Bugbusters <w.meijer.5@student.rug.nl>
#

import os
import subprocess

from graal.graal import (GraalError, GraalRepository)
from .analyzer import Analyzer, is_in_paths

DEFAULT_DIFF_TIMEOUT = 60


class Cloc(Analyzer):
    """A wrapper for Cloc.

    This class allows to call Cloc over a file, parses
    the result of the analysis and returns it as a dict.

    :param diff_timeout: max time to compute diffs of a given file
    """
    version = '0.3.1'

    def __init__(self, repository_level, diff_timeout=DEFAULT_DIFF_TIMEOUT):
        self.diff_timeout = diff_timeout
        self.analyze = self.analyze_repository if repository_level else self.analyze_files

    def analyze_repository(self, **kwargs):
        """
        Add information LOC, total files, blank and commented lines
        using CLOC for the entire repository

        :param worktreepath: the directory where to store the working tree
        :param in_paths: the target paths of the analysis

        :returns result: dict of the results of the analysis over a repository
        """

        worktreepath = kwargs["worktreepath"]
        in_paths = kwargs["in_paths"]

        results = []
        for file_path in GraalRepository.files(worktreepath):
            if in_paths:
                found = [p for p in in_paths if file_path.endswith(p)]
                if not found:
                    continue

            result = {
                'file_path': os.path.relpath(file_path, worktreepath),
                'ext': GraalRepository.extension(file_path)
            }

            message = self.__decode_cloc_command(file_path=file_path)
            result = self.__do_cloc_analysis(message, result)
            results.append(result)

        return results

    def analyze_files(self, **kwargs):
        """
        Add information about LOC, blank and
        commented lines using CLOC for all files in the commit.

        :param commit: to-be-analyzed commit
        :param in_paths: the target paths of the analysis
        :param worktreepath: the directory where to store the working tree

        :returns result: dict of the results of the analysis over all files
        """

        results = []

        commit = kwargs["commit"]
        in_paths = kwargs["in_paths"]
        worktreepath = kwargs["worktreepath"]

        for commit_file in commit["files"]:
            # selects file path; source depends on whether it's new
            new_file = commit_file.get("newfile", None)
            file_path = new_file if new_file else commit_file['file']

            if not is_in_paths(in_paths, file_path):
                continue

            result = {
                'file_path': file_path,
                'ext': GraalRepository.extension(file_path)
            }

            # skips deleted files.
            if commit_file.get("action", None) == "D":
                results.append(result)
                continue

            # performs analysis and updates result
            local_path = os.path.join(worktreepath, file_path)
            if GraalRepository.exists(local_path):
                message = self.__decode_cloc_command(file_path=local_path)
                result = self.__do_cloc_analysis(message, result)
                results.append(result)

        return results

    def __do_cloc_analysis(self, message, results):
        """
        Add information about LOC, blank and
        commented lines using CLOC for a given file.

        :param message: message from standard output after execution of cloc
        :param worktreepath: the directory where to store the working tree

        :returns result: dict of the results of the analysis over a file
        """

        flag = False
        results.update({
            "blanks": 0,
            "comments": 0,
            "loc": 0
        })

        for line in message.strip().split("\n"):
            if not line.startswith("-----") and flag:
                file_info = line.split()[-3:]
                blank_lines, commented_lines, loc = map(int, file_info)
                results.update({
                    "blanks": blank_lines,
                    "comments": commented_lines,
                    "loc": loc
                })
                break

            if line.lower().startswith("language"):
                flag = True

        return results

    def __decode_cloc_command(self, file_path):
        """
        Decodes CLOC command.

        :param target_path: targeted file/directory

        :returns: SCC output message
        """

        try:
            cloc_command = ['cloc', file_path, '--diff-timeout', str(self.diff_timeout)]
            message = subprocess.check_output(cloc_command).decode("utf-8")
            return message
        except subprocess.CalledProcessError as error:
            cause = f"Cloc failed at {file_path}, {error.output.decode('utf-8')}"
            raise GraalError(cause=cause) from error
        finally:
            subprocess._cleanup()
