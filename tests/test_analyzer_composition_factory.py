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

import unittest

from graal.backends.core.colic.colic import CATEGORY_PACKAGE
from graal.backends.core.colic.compositions.composition_nomos import CATEGORY_COLIC_NOMOS, NOMOS
from graal.backends.core.colic.compositions.composition_scancode import CATEGORY_COLIC_SCANCODE, SCANCODE
from graal.backends.core.colic.compositions.composition_scancode_cli import CATEGORY_COLIC_SCANCODE_CLI, SCANCODE_CLI

from graal.backends.core.composer import Composer
from graal.backends.core.analyzer_composition_factory import AnalyzerCompositionFactory
from graal.graal import GraalError

from base_analyzer import TestCaseAnalyzer


class TestAnalyzerCompositionFactory(TestCaseAnalyzer):
    """Tests AnalyzerCompositionFactory"""

    target_package = CATEGORY_PACKAGE

    def test_constructor(self):
        """Tests constructor"""

        fac = AnalyzerCompositionFactory(self.target_package)
        self.assertGreater(len(fac.get_categories()), 0)

        with self.assertRaises(GraalError):
            fac = AnalyzerCompositionFactory("unknown.package")

    def test_get_categories(self):
        """Tests get categories."""

        fac = AnalyzerCompositionFactory(self.target_package)

        cats = fac.get_categories()
        self.assertEqual(len(cats), 4)
        self.assertIn(CATEGORY_COLIC_NOMOS, cats)
        self.assertIn(CATEGORY_COLIC_SCANCODE, cats)
        self.assertIn(CATEGORY_COLIC_SCANCODE_CLI, cats)

    def test_get_composer(self):
        """Tests Get Composer method and the returned compositions."""

        fac = AnalyzerCompositionFactory(self.target_package)
        cats = fac.get_categories()

        for cat in cats:
            composer = fac.get_composer(cat)

            self.assertTrue(composer)
            self.assertTrue(issubclass(type(composer), Composer))

            self.assertEqual(type(composer.get_kind()), str)
            self.assertEqual(type(composer.get_category()), str)
            self.assertEqual(type(composer.get_composition()), list)

    def test_category_from_kind(self):
        """Test get category from kind method."""

        fac = AnalyzerCompositionFactory(self.target_package)

        self.assertEqual(fac.get_category_from_kind(NOMOS), CATEGORY_COLIC_NOMOS)
        self.assertEqual(fac.get_category_from_kind(SCANCODE), CATEGORY_COLIC_SCANCODE)
        self.assertEqual(fac.get_category_from_kind(SCANCODE_CLI), CATEGORY_COLIC_SCANCODE_CLI)

    def test_unknown(self):
        """Tests methods with unknown category."""

        fac = AnalyzerCompositionFactory(self.target_package)

        with self.assertRaises(GraalError):
            fac.get_composer("unknown")

        with self.assertRaises(GraalError):
            fac.get_category_from_kind("unknown")


if __name__ == "__main__":
    unittest.main()
