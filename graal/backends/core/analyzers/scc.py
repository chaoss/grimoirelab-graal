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
#

import subprocess

from graal.graal import GraalRepository
from .analyzer import Analyzer


class SCC(Analyzer):
    """A wrapper for SCC.

    This class allows to call SCC over a file, parses
    the result of the analysis and returns it as a dict.
    """
    version = '0.1.0'

    def __init__(self):
        pass

    def __analyze_file(self, message):
        """Add information about LOC, blank and commented lines using SCC for a given file

        :param message: message from standard output after execution of SCC
        :returns result: dict of the results of the analysis over a file
        """
        flag = False
        results = {
            "blanks": 0,
            "comments": 0,
            "loc": 0,
            "ccn": 0
        }

        for line in message.strip().split("\n"):
            if flag:
                if not line.startswith("────────"):
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

    def __analyze_repository(self, message):
        """Add information LOC, total files, blank, commented lines and code complexity using SCC for
           the entire repository

        :param message: message from standard output after execution of SCC
        :returns result: dict of the results of the analysis over a repository
        """
        results = {}
        flag = False

        for line in message.strip().split("\n"):
            if flag:
                if line.lower().startswith("total"):
                    break
                elif not line.startswith("────────"):
                    digested_split = line.split()
                    langauge, files_info = digested_split[:-6], digested_split[-6:]
                    language = " ".join(langauge)
                    total_files, total_lines, blank_lines, commented_lines, loc, complexity = map(int, files_info)
                    language_result = {
                        "total_files": total_files,
                        "blanks": blank_lines,
                        "comments": commented_lines,
                        "loc": loc,
                        "ccn": complexity
                    }
                    results[language] = language_result

            if line.lower().startswith("language"):
                flag = True

        return results

    def analyze(self, **kwargs):
        """Add information using SCC

        :param file_path: file path
        :param repository_level: set to True if analysis has to be performed on a repository
        :returns result: dict of the results of the analysis
        """
        repository_level = kwargs.get('repository_level', False)

        if repository_level:
            file_path = kwargs['repository_path']
        else:
            file_path = kwargs['file_path']

        try:
            scc_command = ['scc', file_path]
            message = subprocess.check_output(scc_command).decode("utf-8")
        except subprocess.CalledProcessError as e:
            message = e.output.decode("utf-8")
        finally:
            subprocess._cleanup()

        if repository_level:
            results = self.__analyze_repository(message)
        else:
            results = self.__analyze_file(message)
            results['ext'] = GraalRepository.extension(file_path)

        return results
