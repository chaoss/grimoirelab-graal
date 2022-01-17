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

import subprocess
import os

from graal.graal import (GraalError, GraalRepository)
from .analyzer import Analyzer

DEFAULT_DIFF_TIMEOUT = 60


class Cloc(Analyzer):
    """A wrapper for Cloc.

    This class allows to call Cloc over a file, parses
    the result of the analysis and returns it as a dict.

    :param diff_timeout: max time to compute diffs of a given file
    """
    version = '0.3.1'

    def __init__(self, repository_level=False, diff_timeout=DEFAULT_DIFF_TIMEOUT):
        self.diff_timeout = diff_timeout
        self.analyze = self.__analyze_repository if repository_level else self.__analyze_files

    def __decode_cloc_command(self, **kwargs):
        """Decodes CLOC command"""

        file_path = kwargs['file_path']

        try:
            cloc_command = ['cloc', file_path, '--diff-timeout', str(self.diff_timeout)]
            message = subprocess.check_output(cloc_command).decode("utf-8")
            return message
        except subprocess.CalledProcessError as error:
            cause = f"Cloc failed at {file_path}, {error.output.decode('utf-8')}"
            raise GraalError(cause=cause) from error
        finally:
            subprocess._cleanup()

    def __analyze_files(self, **kwargs):
        """
        Add information about LOC, blank and 
        commented lines using CLOC for all files in the commit

        :returns result: dict of the results of the analysis over all files
        """

        results = []

        worktreepath = kwargs["worktreepath"]
        commit = kwargs["commit"]

        for commit_file in commit["files"]:
            file_path = commit_file['file']

            result = {
                'file_path': file_path,
                'ext': GraalRepository.extension(file_path)
            }

            results.append(result)

            # skips deleted files.
            if commit_file.get("action", None) == "D":
                continue

            # sets file path to the new file.
            new_file = commit_file.get("newfile", None)
            if new_file:
                file_path = new_file

            # performs analysis and updates result
            local_path = os.path.join(worktreepath, file_path)
            kwargs['file_path'] = local_path

            if GraalRepository.exists(local_path):

                message = self.__decode_cloc_command(**kwargs)
                analysis_result = self.__analyze_file(message)

                results[-1].update(analysis_result)

        return results

    def __analyze_file(self, message):
        """
        Add information about LOC, blank and
        commented lines using CLOC for a given file

        :param message: message from standard output after execution of cloc
        :returns result: dict of the results of the analysis over a file
        """

        flag = False
        results = {
            "blanks": 0,
            "comments": 0,
            "loc": 0
        }

        for line in message.strip().split("\n"):
            if flag:
                if not line.startswith("-----"):
                    file_info = line.split()[-3:]
                    blank_lines, commented_lines, loc = map(int, file_info)
                    results["blanks"] = blank_lines
                    results["comments"] = commented_lines
                    results["loc"] = loc
                    break

            if line.lower().startswith("language"):
                flag = True

        return results

    def __analyze_repository(self, **kwargs):
        """
        Add information LOC, total files, blank and commented lines
        using CLOC for the entire repository

        :param message: message from standard output after execution of cloc

        :returns result: dict of the results of the analysis over a repository
        """

        message = self.__decode_cloc_command(**kwargs)

        results = {}
        flag = False

        for line in message.strip().split("\n"):
            if flag:
                if line.lower().startswith("sum"):
                    break
                elif not line.startswith("-----"):
                    digested_split = line.split()
                    langauge, files_info = digested_split[:-4], digested_split[-4:]
                    language = " ".join(langauge)
                    total_files, blank_lines, commented_lines, loc = map(int, files_info)
                    language_result = {
                        "total_files": total_files,
                        "blanks": blank_lines,
                        "comments": commented_lines,
                        "loc": loc
                    }
                    results[language] = language_result

            if line.lower().startswith("language"):
                flag = True

        return results
