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

import json
import subprocess

from graal.graal import (GraalError,
                         GraalRepository)
from .analyzer import Analyzer


class ScanCode(Analyzer):
    """A wrapper for nexB/scancode-toolkit.

    This class allows to call scancode-toolkit over a file, parses
    the result of the analysis and returns it as a dict.

    :param exec_path: path of the scancode executable
    """
    version = '0.1.0'

    def __init__(self, exec_path):
        if not GraalRepository.exists(exec_path):
            raise GraalError(cause="executable path %s not valid" % exec_path)

        self.exec_path = exec_path

    def analyze(self, **kwargs):
        """Add information about license

        :param file_path: file path

        :returns result: dict of the results of the analysis
        """
        result = {'licenses': []}
        file_path = kwargs['file_path']

        try:
            msg = subprocess.check_output([self.exec_path, '--json-pp', '-', '--license', file_path]).decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise GraalError(cause="Scancode failed at %s, %s" % (file_path, e.output.decode("utf-8")))
        finally:
            subprocess._cleanup()

        licenses_raw = json.loads(msg)
        if 'files' not in licenses_raw:
            return result

        result['licenses'] = licenses_raw['files'][0]['licenses']

        return result
