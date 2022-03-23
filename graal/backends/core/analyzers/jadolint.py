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
#     Groninger Bugbusters <w.meijer.5@student.rug.nl>
#

import subprocess

from graal.graal import (GraalError,
                         GraalRepository)
from .analyzer import Analyzer, is_in_paths


DEPENDENCIES = 'dependencies'
SMELLS = 'smells'


class Jadolint(Analyzer):
    """A wrapper for Jadolint, a tool to extract dependencies and smells from Dockerfiles."""

    version = '0.2.1'

    def __init__(self, analysis):
        self.analysis = analysis

    def analyze(self, **kwargs):
        """Get Jadolint results for a Dockerfile.
        :param exec_path: path of the executable to perform the analysis
        :param commit: a Graal commit item
        :param in_paths: the target paths of the analysis
        :param worktreepath: the directory where the working tree is stored
        :param result: dict of the results of the analysis
        """

        exec_path = kwargs["exec_path"]
        commit = kwargs["commit"]
        in_paths = kwargs["in_paths"]
        worktreepath = kwargs["worktreepath"]

        if not exec_path or not GraalRepository.exists(exec_path):
            raise GraalError(cause="executable path %s not valid" % exec_path)

        analysis = {}

        for committed_file in commit['files']:
            file_path = committed_file['file']
            if not is_in_paths(in_paths, file_path):
                continue

            local_path = worktreepath + '/' + file_path

            if self.analysis == DEPENDENCIES:
                if not GraalRepository.exists(local_path):
                    analysis.update({file_path: {DEPENDENCIES: []}})
                    continue

                dependencies = self.analyze_file(local_path, exec_path)
                analysis.update({file_path: dependencies})
            else:
                if not GraalRepository.exists(local_path):
                    analysis.update({file_path: {SMELLS: []}})
                    continue

                smells = self.analyze_file(local_path, exec_path)
                digested_smells = {SMELLS: [smell.replace(worktreepath, '') for smell in smells[SMELLS]]}
                analysis.update({file_path: digested_smells})

        return analysis

    def analyze_file(self, file_path, exec_path):
        """Get Jadolint results for a Dockerfile.
        :param file_path: file path
        :param exec_path: path of the executable to perform the analysis
        :param result: dict of the results of the analysis
        """
        results = []
        result = {self.analysis: results}

        if self.analysis == DEPENDENCIES:
            cmd = ['java', '-jar', exec_path, file_path, '--deps']
        else:
            cmd = ['java', '-jar', exec_path, file_path, '--smells']

        try:
            msg = subprocess.check_output(cmd).decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise GraalError(cause="Jadolint failed at %s, %s" % (file_path, e.output.decode("utf-8")))
        finally:
            subprocess._cleanup()

        results_raw = msg.split('\n')
        for res_raw in results_raw:
            res = res_raw.strip()
            if res:
                results.append(res)

        return result
