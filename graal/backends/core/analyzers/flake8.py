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


class Flake8(Analyzer):
    """A wrapper for Flake8, a source code style checker for Python."""

    version = '0.1.0'

    def analyze(self, **kwargs):
        """Add quality checks data using Flake8.

        :param module_path: module path
        :param details: if True, it returns information about single commit

        :returns result: dict of the results of the analysis
        """
        module_path = kwargs['module_path']
        details = kwargs['details']
        worktree_path = kwargs['worktree_path']

        try:
            msg = subprocess.check_output(
                ['flake8', "--format='%(path)s::%(row)d::%(col)d::%(code)s::%(text)s'", module_path]).decode("utf-8")
        except subprocess.CalledProcessError as e:
            msg = e.output.decode("utf-8")
        finally:
            subprocess._cleanup()

        lines = msg.strip().split('\n') if msg else []

        result = {'warnings': len(lines)}

        if details:
            flake8_verbose = []
            for line in lines:
                path, row, column, type_of_warning, description = line.split("::")
                file_path = path[path.index(worktree_path) + 1:] if path.startswith(worktree_path) else path

                line_details = {
                    "file_path": file_path,
                    "type_of_warning": type_of_warning,
                    "line": row,
                    "column": column,
                    "description": description
                }
                flake8_verbose.append(line_details)

            result['lines'] = flake8_verbose

        return result
