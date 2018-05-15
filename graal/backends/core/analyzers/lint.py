# -*- coding: utf-8 -*- the Graal backend.
#
# Copyright (C) 2015-2018 Bitergia
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
# along with this program; if not, write to the Free Software
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1335, USA.
#
# Authors:
#     Valerio Cosentino <valcos@bitergia.com>
#

import subprocess

from graal.graal import GraalError
from .analyzer import Analyzer


class Lint(Analyzer):
    """A wrapper for Pylint, a source code, bug and quality checker for Python."""

    version = '0.1.0'

    def analyze(self, **kwargs):
        """Add quality checks data using Pylint.

        :param module_path: module path
        :param result: dict of the results of the analysis
        """
        module_path = kwargs['module_path']

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
        details = []
        module_name = ""
        lines = msg.split('\n')
        modules = {}
        for line in lines:
            if line.startswith("***"):
                if details:
                    modules.update({module_name: details})
                module_name = line.strip("*").strip().replace("Module ", "")
                details = []
            elif line.strip() == "":
                continue
            elif line.startswith("----"):
                modules.update({module_name: details})
                end = True
            else:
                if end:
                    code_quality = line.split("/")[0].split(" ")[-1]
                    break
                else:
                    details.append(line)

        result = {'quality': code_quality,
                  'affected_modules': len(modules),
                  'warnings': sum([len(mod) for mod in modules]),
                  'modules': modules}

        return result