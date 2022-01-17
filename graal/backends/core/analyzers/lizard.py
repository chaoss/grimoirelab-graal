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
#     wmeijer221 <w.meijer.5@student.rug.nl>
#

import os
import warnings

from .analyzer import Analyzer
from graal.graal import GraalError, GraalRepository
import lizard


ALLOWED_EXTENSIONS = ['java', 'py', 'php', 'scala', 'js', 'rb', 'cs', 'cpp', 'c', 'lua', 'go', 'swift']

# TODO: split up file analyzer from repository analyzer? 
class Lizard(Analyzer):
    """A wrapper for Lizard, a code complexity analyzer, which is able
    to handle many imperative programming languages such as:
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
    """
    version = '0.3.2'

    def __init__(self, repository_level: bool):
        """
        Sets up Lizard analysis.

        :param repository_level: determines analysis method (repository- or file-level)
        """
        self.analyze = self.__analyze_repository if repository_level else self.__analyze_files

    def __do_file_analsysis(self, file_path, result): 
        # Filter DeprecationWarning from lizard_ext/auto_open.py line 26
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            analysis = lizard.analyze_file(file_path)

        result['ccn'] = analysis.CCN
        result['avg_ccn'] = analysis.average_cyclomatic_complexity
        result['avg_loc'] = analysis.average_nloc
        result['avg_tokens'] = analysis.average_token_count
        result['num_funs'] = len(analysis.function_list)
        result['loc'] = analysis.nloc
        result['tokens'] = analysis.token_count

        return result, analysis

    def __add_file_details(self, result, analysis):
        """
        Adds additional details to the results.

        :returns  result: dict of the results of the analysis
        """

        funs_data = []
        for fun in analysis.function_list:
            fun_data = {'ccn': fun.cyclomatic_complexity,
                        'tokens': fun.token_count,
                        'loc': fun.nloc,
                        'lines': fun.length,
                        'name': fun.name,
                        'args': fun.parameter_count,
                        'start': fun.start_line,
                        'end': fun.end_line}
            funs_data.append(fun_data)

        result['funs'] = funs_data

        return result

    def __analyze_file(self, file_path, details):
        """
        Analyzes a single file

        :params file_path: path of the file that is analyzed
        :params details: if True, it returns information about single functions

        :returns  result: dict of the results of the analysis
        """

        ext = GraalRepository.extension(file_path)
        result = {'ext': ext}

        if not ext in ALLOWED_EXTENSIONS:
            return result

        result, analysis = self.__do_file_analsysis(file_path, result)

        if details:
            self.__add_file_details(result, analysis)

        return result

    def __analyze_files(self, **kwargs):
        """Add code complexity information for a file using Lizard.

        Current information includes cyclomatic complexity (ccn),
        avg lines of code and tokens, number of functions and tokens.
        Optionally, the following information can be included for every function:
        ccn, tokens, LOC, lines, name, args, start, end

        :param file_path: file path
        :param details: if True, it returns information about single functions

        :returns  result: dict of the results of the analysis
        """

        commit = kwargs["commit"]
        in_paths = kwargs["in_paths"]
        details = kwargs["details"]
        worktreepath = kwargs['worktreepath']

        results = []

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

            if in_paths:
                found = [p for p in in_paths if file_path.endswith(p)]
                if not found:
                    continue

            local_path = os.path.join(worktreepath, file_path)

            if GraalRepository.exists(local_path):
                file_info = self.__analyze_file(local_path, details)
                file_info['file_path'] = file_path
                results.append(file_info)

        return results

    def __analyze_repository(self, **kwargs):
        """Add code complexity information for a given repository
        using Lizard and CLOC.

        Current information includes cyclomatic complexity (ccn),
        lines of code, number of functions, tokens, blanks and comments.

        :param repository_path: repository path
        :param details: if True, it returns fine-grained results

        :returns  result: list of the results of the analysis
        """

        repository_path = kwargs["repository_path"]
        files_affected = kwargs['files_affected']

        analysis_result = []

        repository_analysis = lizard.analyze(
            paths=[repository_path],
            threads=1,
            exts=lizard.get_extensions([]),
        )

        for analysis in repository_analysis:
            file_path = analysis.filename.replace(repository_path + "/", '')
            in_commit = True if file_path in files_affected else False

            result = {
                'loc': analysis.nloc,
                'ccn': analysis.CCN,
                'tokens': analysis.token_count,
                'num_funs': len(analysis.function_list),
                'file_path': file_path,
                'in_commit': in_commit,
            }
            analysis_result.append(result)

        # TODO: implement details option

        return analysis_result

    def analyze(self, **kwargs):
        """Add code complexity information using Lizard.

        :param file_path: file path
        :param repository_path: repository path
        :param details: if True, it returns detailed information about an analysis

        :returns  result: the results of the analysis
        """

        raise GraalError(cause=f"analysis sub-analysis method is not set for {__name__}")
