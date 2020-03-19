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
#     Valerio Cosentino <valcos@bitergia.com>
#

import subprocess

from .analyzer import Analyzer


class Linguist(Analyzer):
    """A wrapper for GitHub Linguist.

    This class allows to call github-linguist over a repository,
    parses the result of the analysis and returns it as a dict.
    """

    version = '0.1.0'

    def analyze(self, **kwargs):
        """Add information about code language distribution

        :param repository_path: repository path
        :param details: if True, it returns detailed information about single commit

        :returns result: dict of the results of the analysis
        """
        repository_path = kwargs['repository_path']
        details = kwargs['details']

        try:
            message = subprocess.check_output(
                ['github-linguist', repository_path]).decode("utf-8")
        except subprocess.CalledProcessError as e:
            message = e.output.decode("utf-8")
        finally:
            subprocess._cleanup()

        lines = message.strip().split('\n') if message else []
        results = {}

        for line in lines:
            if "%" in line:
                percentage, language = line.split()
                results[language] = float(percentage[:-1])

        if details:
            results["breakdown"] = {}
            '''
            TODO: add details of breakdown at directory level
            using --breakdown
            '''
            pass

        return results
