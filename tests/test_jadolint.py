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
#

import os
import shutil
import subprocess
import unittest.mock

from graal.backends.core.analyzers.jadolint import (Jadolint,
                                                    DEPENDENCIES,
                                                    SMELLS)
from graal.graal import GraalError
from base_analyzer import (ANALYZER_TEST_FOLDER,
                           ANALYZER_TEST_FILE,
                           DOCKERFILE_TEST,
                           get_file_path,
                           TestCaseAnalyzer)
from utils import JADOLINT_PATH


class TestJadolint(TestCaseAnalyzer):
    """Jadolint tests"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        test_analyzer = get_file_path(ANALYZER_TEST_FOLDER + DOCKERFILE_TEST)
        shutil.copy2(test_analyzer, cls.tmp_path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_path)

    def test_init(self):
        """Test whether Jadolint is correctly initialized"""

        jadolint = Jadolint(JADOLINT_PATH, analysis=SMELLS)
        self.assertEqual(jadolint.analysis, SMELLS)

        jadolint = Jadolint(JADOLINT_PATH, analysis=DEPENDENCIES)
        self.assertEqual(jadolint.analysis, DEPENDENCIES)

    def test_init_error(self):
        """Test whether an error is thrown when the exec path is None"""

        with self.assertRaises(GraalError):
            Jadolint("unknown", DEPENDENCIES)

    def test_analyze_smells(self):
        """Test whether Jadolint returns the expected fields data"""

        jadolint = Jadolint(JADOLINT_PATH, analysis=SMELLS)
        kwargs = {
            'file_path': os.path.join(self.tmp_path, DOCKERFILE_TEST)
        }
        result = jadolint.analyze(**kwargs)

        expected = [
            'Dockerfile 5 DL4000 MAINTAINER is deprecated',
            'Dockerfile 5 DL4000 MAINTAINER is deprecated',
            'Dockerfile 5 DL4000 MAINTAINER is deprecated',
            'Dockerfile 5 DL4000 MAINTAINER is deprecated',
            'Dockerfile 5 DL4000 MAINTAINER is deprecated',
            'Dockerfile 13 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 16 DL3008 Pin versions in apt-get install',
            'Dockerfile 16 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 16 DL3014 Use the -y switch',
            'Dockerfile 16 DL3015 Avoid additional packages by specifying --no-install-recommends',
            'Dockerfile 32 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 34 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 34 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 37 DL3020 Use COPY instead of ADD for files and folders',
            'Dockerfile 38 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 40 DL3009 Delete the apt-get lists after installing something',
            'Dockerfile 55 DL3000 Use absolute WORKDIR',
            'Dockerfile 57 DL3025 Use arguments JSON notation for CMD and ENTRYPOINT arguments'
        ]

        self.assertIn(SMELLS, result)

        for i in range(len(result[SMELLS])):
            self.assertRegex(result[SMELLS][i], expected[i])

    def test_analyze_dependencies(self):
        """Test whether Jadolint returns the expected fields data"""

        jadolint = Jadolint(JADOLINT_PATH, analysis=DEPENDENCIES)
        kwargs = {
            'file_path': os.path.join(self.tmp_path, DOCKERFILE_TEST)
        }
        result = jadolint.analyze(**kwargs)

        expected = [
            'debian stretch-slim',
            'bash',
            'locales',
            'gcc',
            'git',
            'git-core',
            'python3',
            'python3-pip',
            'python3-venv',
            'python3-dev',
            'python3-gdbm',
            'mariadb-client',
            'unzip',
            'curl',
            'wget',
            'sudo',
            'ssh'
        ]

        self.assertIn(DEPENDENCIES, result)
        self.assertListEqual(result[DEPENDENCIES], expected)

    def test_analyze_empty(self):
        """Test whether Jadolint returns empty results if the file isn't a Dockerfile"""

        jadolint = Jadolint(JADOLINT_PATH, analysis=DEPENDENCIES)
        kwargs = {
            'file_path': os.path.join(self.tmp_path, ANALYZER_TEST_FILE)
        }
        result = jadolint.analyze(**kwargs)

        self.assertIn('dependencies', result)
        self.assertListEqual(result['dependencies'], [])

    @unittest.mock.patch('subprocess.check_output')
    def test_analyze_error(self, check_output_mock):
        """Test whether an exception is thrown in case of errors"""

        check_output_mock.side_effect = subprocess.CalledProcessError(
            -1, "command", output=b'output')

        jadolint = Jadolint(JADOLINT_PATH, analysis=DEPENDENCIES)
        kwargs = {
            'file_path': os.path.join(self.repo_path, DOCKERFILE_TEST)
        }
        with self.assertRaises(GraalError):
            _ = jadolint.analyze(**kwargs)


if __name__ == "__main__":
    unittest.main()
