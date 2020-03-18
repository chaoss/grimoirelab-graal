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

import warnings

import lizard
from graal.backends.core.analyzers.cloc import Cloc
from .analyzer import Analyzer


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
    version = '0.3.1'

    def __analyze_file(self, file_path, details):
        """Add code complexity information for a file using Lizard.

        Current information includes cyclomatic complexity (ccn),
        avg lines of code and tokens, number of functions and tokens.
        Optionally, the following information can be included for every function:
        ccn, tokens, LOC, lines, name, args, start, end

        :param file_path: file path
        :param details: if True, it returns information about single functions

        :returns  result: dict of the results of the analysis
        """
        result = {}

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
        result['ext'] = file_path.split(".")[-1]

        if not details:
            return result

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

    def __analyze_repository(self, repository_path, files_affected, details):
        """Add code complexity information for a given repository
        using Lizard and CLOC.

        Current information includes cyclomatic complexity (ccn),
        lines of code, number of functions, tokens, blanks and comments.

        :param repository_path: repository path
        :param details: if True, it returns fine-grained results

        :returns  result: list of the results of the analysis
        """
        analysis_result = []

        repository_analysis = lizard.analyze(
            paths=[repository_path],
            threads=1,
            exts=lizard.get_extensions([]),
        )
        cloc = Cloc()

        for analysis in repository_analysis:
            cloc_analysis = cloc.analyze(file_path=analysis.filename)
            file_path = analysis.filename.replace(repository_path + "/", '')
            in_commit = True if file_path in files_affected else False

            result = {
                'loc': analysis.nloc,
                'ccn': analysis.CCN,
                'tokens': analysis.token_count,
                'num_funs': len(analysis.function_list),
                'file_path': file_path,
                'in_commit': in_commit,
                'blanks': cloc_analysis['blanks'],
                'comments': cloc_analysis['comments']
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

        details = kwargs['details']

        if kwargs.get('repository_level', False):
            files_affected = kwargs['files_affected']
            result = self.__analyze_repository(kwargs["repository_path"], files_affected, details)
        else:
            result = self.__analyze_file(kwargs['file_path'], details)

        return result
