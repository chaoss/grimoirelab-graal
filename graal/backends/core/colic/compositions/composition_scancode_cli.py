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

from graal.backends.core.analyzers.scancode import ScanCode
from graal.backends.core.composer import Composer


SCANCODE_CLI = 'scancode_cli'
CATEGORY_COLIC_SCANCODE_CLI = 'code_license_' + SCANCODE_CLI


class CompositionScancodeCli(Composer):
    """Analyzer Composition for Scancode cli security vulnerabilities."""

    version = '0.1.0'

    def get_composition(self):
        return [ScanCode(cli=True)]

    def get_category(self):
        return CATEGORY_COLIC_SCANCODE_CLI

    def get_kind(self):
        return SCANCODE_CLI

    def merge_results(self, results):
        return results[0]
