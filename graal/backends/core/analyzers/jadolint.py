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

import subprocess

from graal.graal import (GraalError,
                         GraalRepository)
from .analyzer import Analyzer


DEPENDENCIES = 'dependencies'
SMELLS = 'smells'


class Jadolint(Analyzer):
    """A wrapper for Jadolint, a tool to extract dependencies and smells from Dockerfiles."""

    version = '0.2.0'

    def __init__(self, exec_path, analysis):
        if not GraalRepository.exists(exec_path):
            raise GraalError(cause="executable path %s not valid" % exec_path)

        self.exec_path = exec_path
        self.analysis = analysis

    def analyze(self, **kwargs):
        """Get Jadolint results for a Dockerfile.

        :param file_path: file path
        :param result: dict of the results of the analysis
        """
        results = []
        result = {self.analysis: results}
        file_path = kwargs['file_path']

        if self.analysis == DEPENDENCIES:
            cmd = ['java', '-jar', self.exec_path, file_path, '--deps']
        else:
            cmd = ['java', '-jar', self.exec_path, file_path, '--smells']

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
