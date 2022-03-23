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


class Analyzer:
    """Abstract class for analyzer.

    Base class to perform analysis on software artifacts.

    Derivated classes have to implement the method
    `analyze(self, **kwargs)`.

    :raises NotImplementedError: raised when `analyze`
        is not defined
    """
    version = '0.1.1'

    def analyze(self, **kwargs):
        raise NotImplementedError


def is_in_paths(in_paths, file_path):
    """
    Returns true if the file path is in in_paths.

    :param in_paths: the list of in_paths
    :param file_path: to-be-tested file path

    :returns: boolean value
    """

    if in_paths:
        found = [p for p in in_paths if file_path.endswith(p)]

        if not found:
            return False

    return True
