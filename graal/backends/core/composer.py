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
#     wmeijer221 <w.meijer.5@student.rug.nl>
#

class Composer:
    """Template class for composition of analyzers"""

    def get_kind(self):
        """Returns more readable name of this composition"""

        raise NotImplementedError

    def get_category(self):
        """Returns the category of this composition"""

        raise NotImplementedError

    def get_composition(self):
        """Returns the corresponding composition"""

        raise NotImplementedError

    def merge_results(self, results):
        """Merges the results of the composition's analyzers"""

        raise NotImplementedError


def merge_with_file_name(results):
    """
    Utility method; merges the results using their file names.

    :param results: Results that are to be merged.
                    These should be on a file-level.

    :returns: merged results

    """

    merged = {}

    for result in results:
        for entry in result:
            file_path = entry['file_path']

            if file_path in merged:
                merged[file_path].update(entry)
            else:
                merged[file_path] = entry

    return list(merged.values())
