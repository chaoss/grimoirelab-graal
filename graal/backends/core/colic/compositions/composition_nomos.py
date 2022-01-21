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

from graal.backends.core.analyzers.nomos import Nomos
from graal.backends.core.composer import Composer


NOMOS = 'nomos'
CATEGORY_COLIC_NOMOS = 'code_license_' + NOMOS


class CompositionNomos(Composer):
    """Analyzer Composition for Nomos security vulnerabilities."""

    version = '0.1.0'

    def get_composition(self):
        return [Nomos()]

    def get_category(self):
        return CATEGORY_COLIC_NOMOS

    def get_kind(self):
        return NOMOS

    def merge_results(self, results):
        return results[0]
