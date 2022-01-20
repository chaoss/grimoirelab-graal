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

from graal.backends.core.colang.compositions.composition_cloc import CompositionCloc
from graal.backends.core.colang.compositions.composition_linguist import CompositionLinguist

from .base_analyzer import TestCaseAnalyzer


class TestCoComFactory(TestCaseAnalyzer):
    """Tests CoCom factory."""

    def test_cloc_merge(self):
        """Tests merge method of the Lizard File composition."""

        cloc = CompositionCloc()

        cloc_results = []

        for i in range(6):
            cloc_results.append({
                "file_path": f"graal/codecomplexity_{i}.py",
                "ext": "py",
                "blanks": i,
                "comments": 2 * i,
                "loc": 3 * i,
            })

        merged_results = cloc.merge_results([cloc_results])

        self.assertEqual(len(merged_results), 6)

        i = 0
        for result in merged_results:
            self.assertIn("file_path", result)
            self.assertEqual(type(result["file_path"]), str)
            self.assertEqual(result["file_path"], cloc_results[i]["file_path"])
            self.assertIn("ext", result)
            self.assertEqual(type(result["ext"]), str)
            self.assertEqual(result["ext"], cloc_results[i]["ext"])
            self.assertIn('blanks', result)
            self.assertEqual(type(result['blanks']), int)
            self.assertEqual(result["blanks"], cloc_results[i]["blanks"])
            self.assertIn('comments', result)
            self.assertEqual(type(result['comments']), int)
            self.assertEqual(result["comments"], cloc_results[i]["comments"])
            self.assertIn('loc', result)
            self.assertEqual(type(result['loc']), int)
            self.assertEqual(result["loc"], cloc_results[i]["loc"])

            i += 1

    def test_linguist_merge(self):
        """Tests merge method of the Linguist File composition."""

        linguist = CompositionLinguist()

        linguist_results = []

        for i in range(6):
            linguist_results.append({
                "file_path": f"graal/codecomplexity_{i}.py",
                "ext": "py",
                "blanks": i,
                "comments": 2 * i,
                "loc": 3 * i,
            })

        merged_results = linguist.merge_results([linguist_results])

        self.assertEqual(len(merged_results), 6)

        i = 0
        for result in merged_results:
            self.assertIn("file_path", result)
            self.assertEqual(type(result["file_path"]), str)
            self.assertEqual(result["file_path"], linguist_results[i]["file_path"])
            self.assertIn("ext", result)
            self.assertEqual(type(result["ext"]), str)
            self.assertEqual(result["ext"], linguist_results[i]["ext"])
            self.assertIn('blanks', result)
            self.assertEqual(type(result['blanks']), int)
            self.assertEqual(result["blanks"], linguist_results[i]["blanks"])
            self.assertIn('comments', result)
            self.assertEqual(type(result['comments']), int)
            self.assertEqual(result["comments"], linguist_results[i]["comments"])
            self.assertIn('loc', result)
            self.assertEqual(type(result['loc']), int)
            self.assertEqual(result["loc"], linguist_results[i]["loc"])

            i += 1


if __name__ == "__main__":
    unittest.main()
