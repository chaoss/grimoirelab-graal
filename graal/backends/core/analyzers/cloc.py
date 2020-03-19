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

from graal.graal import (GraalError,
                         GraalRepository)
from .analyzer import Analyzer

DEFAULT_DIFF_TIMEOUT = 60


class Cloc(Analyzer):
    """A wrapper for Cloc.

    This class allows to call Cloc over a file, parses
    the result of the analysis and returns it as a dict.

    :param diff_timeout: max time to compute diffs of a given file
    """
    version = '0.3.0'

    def __init__(self, diff_timeout=DEFAULT_DIFF_TIMEOUT):
        self.diff_timeout = diff_timeout

    def __analyze_file(self, message):
        """Add information about LOC, blank and commented lines using CLOC for a given file

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

    def __analyze_repository(self, message):
        """Add information LOC, total files, blank and commented lines using CLOC for the entire repository

        :param message: message from standard output after execution of cloc

        :returns result: dict of the results of the analysis over a repository
        """

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

    def analyze(self, **kwargs):
        """Add information using CLOC

        :param file_path: file path
        :param repository_level: set to True if analysis has to be performed on a repository

        :returns result: dict of the results of the analysis
        """

        file_path = kwargs['file_path']
        repository_level = kwargs.get('repository_level', False)

        try:
            cloc_command = ['cloc', file_path, '--diff-timeout', str(self.diff_timeout)]
            message = subprocess.check_output(cloc_command).decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise GraalError(cause="Cloc failed at %s, %s" % (file_path, e.output.decode("utf-8")))
        finally:
            subprocess._cleanup()

        if repository_level:
            results = self.__analyze_repository(message)
        else:
            results = self.__analyze_file(message)
            results['ext'] = GraalRepository.extension(file_path)

        return results
