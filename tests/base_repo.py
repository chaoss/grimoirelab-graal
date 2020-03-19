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
import tempfile
import unittest.mock


def get_file_path(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


class TestCaseRepo(unittest.TestCase):
    """Base class to test Graal on a Git repo"""

    repo_name = 'graaltest'

    def setUp(self):
        self.tmp_path = tempfile.mkdtemp(prefix='graal_')
        self.tmp_repo_path = os.path.join(self.tmp_path, 'repos')
        os.mkdir(self.tmp_repo_path)

        self.git_path = os.path.join(self.tmp_path, self.repo_name)
        self.worktree_path = os.path.join(self.tmp_path, 'graal_worktrees')

        data_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(data_path, 'data')

        fdout, _ = tempfile.mkstemp(dir=self.tmp_path)

        zip_path = os.path.join(data_path, self.repo_name + '.zip')
        subprocess.check_call(['unzip', '-qq', zip_path, '-d', self.tmp_repo_path])

        origin_path = os.path.join(self.tmp_repo_path, 'graaltest')
        subprocess.check_call(['git', 'clone', '-q', '--bare', origin_path, self.git_path],
                              stderr=fdout)

    def tearDown(self):
        shutil.rmtree(self.tmp_path)


if __name__ == "__main__":
    unittest.main()
