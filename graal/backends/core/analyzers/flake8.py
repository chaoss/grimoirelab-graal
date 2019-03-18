# -*- coding: utf-8 -*- the Graal backend.
#
# Copyright (C) 2015-2019 Bitergia
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
#     Nishchith Shetty <inishchith@gmail.com>
#

import subprocess

from .analyzer import Analyzer


class Flake8(Analyzer):
    """A wrapper for Flake8, a source code style checker for Python."""

    version = '0.2.0'

    def analyze(self, **kwargs):
        """Add quality checks data using Flake8.

        :param module_path: module path
        :param details: if True, it returns information about single commit

        :returns result: dict of the results of the analysis
        """
        module_path = kwargs['module_path']
        details = kwargs['details']

        try:
            msg = subprocess.check_output(['flake8', module_path]).decode("utf-8")
        except subprocess.CalledProcessError as e:
            msg = e.output.decode("utf-8")
        finally:
            subprocess._cleanup()

        lines = msg.split('\n')

        result = {'warnings': len(lines)}

        if details:
            result['lines'] = lines

        return result
