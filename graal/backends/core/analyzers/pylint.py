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
#     inishchith <inishchith@gmail.com>
#     Valerio Cosentino <valcos@bitergia.com>
#

import subprocess

from graal.graal import GraalError
from .analyzer import Analyzer


class PyLint(Analyzer):
    """A wrapper for Pylint, a source code, bug and quality checker for Python."""

    version = '0.2.1'

    def analyze(self, **kwargs):
        """Add quality checks data using Pylint.

        :param module_path: module path
        :param details: if True, it returns information about single modules

        :returns result: dict of the results of the analysis
        """
        module_path = kwargs['module_path']
        details = kwargs['details']

        try:
            msg = subprocess.check_output(['pylint', '-rn', '--output-format=text', module_path]).decode("utf-8")
        except subprocess.CalledProcessError as e:
            msg = e.output.decode("utf-8")
            if not msg.startswith("***"):
                raise GraalError(cause="Pylint failed at %s, %s" % (module_path, msg))
        finally:
            subprocess._cleanup()

        end = False
        code_quality = None
        mod_details = []
        module_name = ""
        lines = msg.split('\n')
        modules = {}
        for line in lines:
            if line.startswith("***"):
                if mod_details:
                    modules.update({module_name: mod_details})
                module_name = line.strip("*").strip().replace("Module ", "")
                mod_details = []
            elif line.strip() == "":
                continue
            elif line.startswith("----"):
                modules.update({module_name: mod_details})
                end = True
            else:
                if end:
                    code_quality = line.split("/")[0].split(" ")[-1]
                    break
                else:
                    mod_details.append(line)

        result = {'quality': code_quality,
                  'num_modules': len(modules),
                  'warnings': sum([len(mod) for mod in modules])}

        if details:
            result['modules'] = modules

        return result
