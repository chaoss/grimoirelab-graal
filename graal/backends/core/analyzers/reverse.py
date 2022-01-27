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
#     inishchith <inishchith@gmail.com>
#     Groninger Bugbusters <w.meijer.5@student.rug.nl>
#

import logging
import os
import subprocess
import tempfile

import networkx as nx
from networkx.drawing.nx_pydot import read_dot
from networkx.readwrite import json_graph

from graal.graal import GraalError, GraalRepository
from .analyzer import Analyzer

CLASSES_FILE_NAME = "classes.dot"
PACKAGES_FILE_NAME = "packages.dot"

logger = logging.getLogger(__name__)


class Reverse(Analyzer):
    """A wrapper for Pyreverse, a tool to extract UML class diagrams and package
    dependencies from Python projects.
    """
    version = '0.1.1'

    def __init__(self):
        self.tmp_path = tempfile.mkdtemp(prefix='codep_graal_')
        os.chdir(self.tmp_path)

    def analyze(self, **kwargs):
        """Get a UML class diagrams from a Python project.
        :param worktreepath: the directory where to store the working tree
        :param entrypoint: the entrypoint of the analysis
        :param result: dict of the results of the analysis
        """
        result = {}

        worktreepath = kwargs['worktreepath']
        entrypoint = kwargs['entrypoint']

        if not worktreepath or not entrypoint:
            raise GraalError(cause="no valid entrypoint given")

        module_path = os.path.join(worktreepath, entrypoint)

        if not GraalRepository.exists(module_path):
            logger.warning("module path %s does not exist at commit %s, analysis will be skipped"
                           % (module_path, kwargs['commit']['commit']))
            return {}

        try:
            subprocess.check_output(['pyreverse', module_path]).decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise GraalError(cause="Pyreverse failed at %s, %s" % (module_path, e.output.decode("utf-8")))
        finally:
            subprocess._cleanup()

        class_diagram = os.path.join(self.tmp_path, CLASSES_FILE_NAME)
        if os.path.exists(class_diagram):
            graph_classes = self.__dotfile2json(class_diagram)
            result['classes'] = graph_classes

        package_diagram = os.path.join(self.tmp_path, PACKAGES_FILE_NAME)
        if os.path.exists(package_diagram):
            graph_packages = self.__dotfile2json(package_diagram)
            result['packages'] = graph_packages

        return result

    def __dotfile2json(self, dot_file):
        g = nx.Graph(read_dot(dot_file))
        json_data = json_graph.node_link_data(g)

        return json_data
