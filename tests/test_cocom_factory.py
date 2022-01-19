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

import unittest
import random

from graal.backends.core.composer import Composer
from graal.backends.core.cocom.cocom_analyzer_factory import CoComAnalyzerFactory
from graal.backends.core.cocom.compositions.composition_lizard_file import CompositionLizardFile
from graal.backends.core.cocom.compositions.composition_lizard_repository import CompositionLizardRepository
from graal.backends.core.cocom.compositions.composition_scc_file import CompositionSccFile
from graal.backends.core.cocom.compositions.composition_scc_repository import CompositionSccRepository
from graal.graal import GraalError

from .base_analyzer import TestCaseAnalyzer


class TestCoComFactory(TestCaseAnalyzer):
    """Tests CoCom factory."""

    def test_constructor(self):
        """Tests constructor"""

        fac = CoComAnalyzerFactory()
        self.assertGreater(len(fac.compositions), 0)

    def test_get_composer_and_build(self):
        """Tests Get Composer method and the returned compositions."""

        fac = CoComAnalyzerFactory()
        cats = fac.get_categories()

        self.assertEqual(len(cats), len(fac.compositions))

        for cat in cats:
            composer = fac.get_composer(cat)

            self.assertTrue(composer)
            self.assertTrue(type(composer), Composer)

            self.assertEqual(type(composer.get_kind()), str)
            self.assertEqual(type(composer.get_category()), str)
            self.assertEqual(type(composer.get_composition()), list)

            c_composition = composer.get_composition()
            f_composition = fac.build(cat)

            self.assertEqual(len(c_composition), len(f_composition))

            for i in range(len(c_composition)):
                self.assertEqual(type(c_composition[i]), type(f_composition[i]))

    def test_unknown(self):
        """Tests methods with unknown category."""

        fac = CoComAnalyzerFactory()

        with self.assertRaises(GraalError):
            fac.get_composer("unknown")

        with self.assertRaises(GraalError):
            fac.build("unknown")

    def test_lizard_file_merge(self):
        """Tests merge method of the Lizard File composition."""

        liz = CompositionLizardFile()

        cloc_results = []
        lizard_results = []

        for i in range(6):
            file_name = f"graal/codecomplexity_{i}.py"

            cloc_results.append({
                "file_path": file_name,
                "ext": "py",
                "blanks": i,
                "comments": 2 * i,
                "loc": 3 * i,
            })

            lizard_results.append({
                "file_path": file_name,
                "ext": "py",
                "num_funs": i,
                "ccn": i * 2,
                "tokens": i * 3,
                "avg_ccn": i,
                "avg_loc": i * 2,
                "avg_tokens": i * 3
            })

        merged_results = liz.merge_results([cloc_results, lizard_results])
        self.assertEqual(type(merged_results), list)

        for i in range(len(merged_results)):
            merged = merged_results[i]
            results_cloc = cloc_results[i]
            results_lizard = lizard_results[i]

            self.assertIn("file_path", merged)
            self.assertEqual(merged["file_path"], results_cloc["file_path"])
            self.assertIn("ext", merged)
            self.assertEqual(merged["ext"], results_cloc["ext"])
            self.assertIn("blanks", merged)
            self.assertEqual(merged["blanks"], results_cloc["blanks"])
            self.assertIn("comments", merged)
            self.assertEqual(merged["comments"], results_cloc["comments"])
            self.assertIn("loc", merged)
            self.assertEqual(merged["loc"], results_cloc["loc"])

            self.assertIn("num_funs", merged)
            self.assertEqual(merged["num_funs"], results_lizard["num_funs"])
            self.assertIn("ccn", merged)
            self.assertEqual(merged["ccn"], results_lizard["ccn"])
            self.assertIn("tokens", merged)
            self.assertEqual(merged["tokens"], results_lizard["tokens"])
            self.assertIn("avg_ccn", merged)
            self.assertEqual(merged["avg_ccn"], results_lizard["avg_ccn"])
            self.assertIn("avg_loc", merged)
            self.assertEqual(merged["avg_loc"], results_lizard["avg_loc"])
            self.assertIn("avg_tokens", merged)
            self.assertEqual(merged["avg_tokens"], results_lizard["avg_tokens"])

    def test_lizard_repository_merge(self):
        """Tests merge method of the Lizard Repository composition."""

        liz = CompositionLizardRepository()

        cloc_results = []
        lizard_results = []

        for i in range(6):
            file_name = f"graal/codecomplexity_{i}.py"

            cloc_results.append({
                "file_path": file_name,
                "ext": "py",
                "blanks": i,
                "comments": 2 * i,
                "loc": 3 * i,
            })

            lizard_results.append({
                "file_path": file_name,
                "ext": "py",
                "num_funs": i,
                "ccn": i * 2,
                "tokens": i * 3,
                "avg_ccn": i,
                "avg_loc": i * 2,
                "avg_tokens": i * 3
            })

        merged_results = liz.merge_results([cloc_results, lizard_results])
        self.assertEqual(type(merged_results), list)

        for i in range(len(merged_results)):
            merged = merged_results[i]
            results_cloc = cloc_results[i]
            results_lizard = lizard_results[i]

            self.assertIn("file_path", merged)
            self.assertEqual(merged["file_path"], results_cloc["file_path"])
            self.assertIn("ext", merged)
            self.assertEqual(merged["ext"], results_cloc["ext"])
            self.assertIn("blanks", merged)
            self.assertEqual(merged["blanks"], results_cloc["blanks"])
            self.assertIn("comments", merged)
            self.assertEqual(merged["comments"], results_cloc["comments"])
            self.assertIn("loc", merged)
            self.assertEqual(merged["loc"], results_cloc["loc"])

            self.assertIn("num_funs", merged)
            self.assertEqual(merged["num_funs"], results_lizard["num_funs"])
            self.assertIn("ccn", merged)
            self.assertEqual(merged["ccn"], results_lizard["ccn"])
            self.assertIn("tokens", merged)
            self.assertEqual(merged["tokens"], results_lizard["tokens"])
            self.assertIn("avg_ccn", merged)
            self.assertEqual(merged["avg_ccn"], results_lizard["avg_ccn"])
            self.assertIn("avg_loc", merged)
            self.assertEqual(merged["avg_loc"], results_lizard["avg_loc"])
            self.assertIn("avg_tokens", merged)
            self.assertEqual(merged["avg_tokens"], results_lizard["avg_tokens"])

    def test_scc_file_merge(self):
        """Tests merge method of the SCC File composition."""

        scc_results = []
        for i in range(6):
            scc_results.append({
                "file_path": f"file_path_{i}.py",
                "ext": "py",
                "blanks": 12,
                "comments": 41,
                "loc": 169,
                "ccn": 5
            })

        scc = CompositionSccFile()
        merged_results = scc.merge_results([scc_results])

        for i in range(len(merged_results)):
            merged = merged_results[i]
            results_scc = scc_results[i]
            self.assertIn("file_path", merged)
            self.assertEqual(merged["file_path"], results_scc["file_path"])
            self.assertIn("ext", merged)
            self.assertEqual(merged["ext"], results_scc["ext"])
            self.assertIn("blanks", merged)
            self.assertEqual(merged["blanks"], results_scc["blanks"])
            self.assertIn("comments", merged)
            self.assertEqual(merged["comments"], results_scc["comments"])
            self.assertIn("loc", merged)
            self.assertEqual(merged["loc"], results_scc["loc"])
            self.assertIn("ccn", merged)
            self.assertEqual(merged["ccn"], results_scc["ccn"])

    def test_scc_repository_merge(self):
        """Tests merge method of the SCC File composition."""

        scc_results = {
            "Python": {
                "total_files": 4,
                "total_lines": 674,
                "blanks": 121,
                "comments": 15,
                "loc": 568,
                "ccn": 6
            },
            "gitignore": {
                "total_files": 6,
                "total_lines": 800,
                "blanks": 123,
                "comments": 30,
                "loc": 953,
                "ccn": 7
            }}

        scc = CompositionSccRepository()
        merged_results = scc.merge_results([scc_results])

        self.assertEqual(len(merged_results), 2)

        for lang, metric in merged_results.items():
            self.assertIn(lang, scc_results)
            orig = scc_results[lang]

            for key, value in metric.items():
                self.assertIn(key, orig)
                self.assertEqual(value, orig[key])


if __name__ == "__main__":
    unittest.main()
