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

import lizard
import os
import warnings

from .analyzer import Analyzer
from graal.graal import GraalError, GraalRepository


ALLOWED_EXTENSIONS = ['java', 'py', 'php', 'scala', 'js', 'rb', 'cs', 'cpp', 'c', 'lua', 'go', 'swift']


class Lizard(Analyzer):
    # TODO: split up file analyzer from repository analyzer?
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

    def __analyze_files(self, **kwargs):
        """Add code complexity information for a file using Lizard.

        Current information includes cyclomatic complexity (ccn),
        avg lines of code and tokens, number of functions and tokens.
        Optionally, the following information can be included for every function:
        ccn, tokens, LOC, lines, name, args, start, end

        :param commit: to-be-analyzed commit
        :param in_paths: the target paths of the analysis
        :param details: if True, it returns information about single functions
        :param worktreepath: the directory where to store the working tree

        :returns  result: dict of the results of the analysis
        """

        commit = kwargs["commit"]
        in_paths = kwargs["in_paths"]
        details = kwargs["details"]
        worktreepath = kwargs['worktreepath']

        results = []

        for commit_file in commit["files"]:
            # selects file path; source depends on whether it's new
            new_file = commit_file.get("newfile", None)
            file_path = new_file if new_file else commit_file['file']

            # sets file path to the new file.
            if in_paths:
                found = [p for p in in_paths if file_path.endswith(p)]
                if not found:
                    continue

            result = {
                'file_path': file_path,
                'ext': GraalRepository.extension(file_path)
            }

            # skips deleted and unsupported files.
            if commit_file.get("action", None) == "D" or not result['ext'] in ALLOWED_EXTENSIONS:
                results.append(result)
                continue

            # performs analysis and updates result
            local_path = os.path.join(worktreepath, file_path)
            if GraalRepository.exists(local_path):
                result = self.__analyze_file(local_path, details, result)
                results.append(result)

        return results

    def __analyze_file(self, file_path, details, result):
        """
        Analyzes a single file using lizard.

        :param file_path: path of the file that is analyzed
        :param details: if True, it returns information about single functions
        :param result: preliminary results of this module

        :returns  result: dict of the results of the analysis
        """

        analysis_result, analysis = self.__do_file_analsysis(file_path, result)
        result.update(analysis_result)

        if details:
            self.__add_file_details(result, analysis)

        return result

    def __do_file_analsysis(self, file_path, result):
        """
        Performs lizard file analysis

        :param file_path: path of the file that is analyzed
        :param result: preliminary results of this module

        :returns: result with lizard analysis fields added to it.
        """

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

        :param result: preliminary results of this module
        :param analysis: analysis object of lizard. 

        :returns: result with detailed lizard analysis fields added to it.
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
        details = kwargs["details"]

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

        if details:
            # TODO: implement details option
            pass

        return analysis_result

    def analyze(self, **kwargs):
        """Add code complexity information using Lizard.

        :returns  result: the results of the analysis
        """

        raise GraalError(cause=f"analysis sub-analysis method is not set for {__name__}")
