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
#     Groninger Bugbusters <w.meijer.5@student.rug.nl>
#

from graal.backends.core.analyzers.flake8 import Flake8
from graal.backends.core.composer import Composer

FLAKE8 = "flake8"
CATEGORY_COQUA_FLAKE8 = 'code_quality_' + FLAKE8


class CompositionFlake8(Composer):
    """Analyzer Composition for Jadolint Dependencies."""

    version = '0.1.0'

    def get_category(self):
        return CATEGORY_COQUA_FLAKE8

    def get_kind(self):
        return FLAKE8

    def get_composition(self):
        return [Flake8()]

    def merge_results(self, results):
        return results[0]
