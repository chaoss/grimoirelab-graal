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
#

import json
import subprocess
from graal.graal import (GraalError,
                         GraalRepository)
from .analyzer import Analyzer


SCANCODE_CLI_EXEC = "etc/scripts/scancli.py"
CONFIGURE_EXEC = 'configure'


class ScanCode(Analyzer):
    """A wrapper for nexB/scancode-toolkit.

    This class allows to call scancode-toolkit over a file, parses
    the result of the analysis and returns it as a dict.

    :param exec_path: path of the scancode executable
    :param cli: True, if scancode_cli is used
    """
    version = '0.2.0'

    def __init__(self, exec_path, cli=False):
        if not GraalRepository.exists(exec_path):
            raise GraalError(cause="executable path %s not valid" % exec_path)

        self.exec_path = exec_path
        self.cli = cli

        if self.cli:
            exec_path = self.exec_path.replace(SCANCODE_CLI_EXEC, CONFIGURE_EXEC)
            _ = subprocess.check_output([exec_path]).decode("utf-8")

    def __analyze_scancode(self, file_path):
        """Add information about license and copyright using scancode

        :param file_path: file path (in case of scancode)
        """
        result = {
            'licenses': [],
            'copyrights': [],
        }
        try:
            msg = subprocess.check_output(
                [self.exec_path, '--json-pp', '-', '--license', '--copyright', file_path]).decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise GraalError(cause="Scancode failed at %s, %s" % (file_path, e.output.decode("utf-8")))
        finally:
            subprocess._cleanup()

        scancode_raw = json.loads(msg)
        if 'files' in scancode_raw:
            result['licenses'] = scancode_raw['files'][0]['licenses']
            result['copyrights'] = scancode_raw['files'][0]['copyrights']

        return result

    def __analyze_scancode_cli(self, file_paths):
        """Add information about license using scancode-cli

        :param file_paths: file paths (in case of scancode_cli for concurrent execution on files)
        :returns result: list of the results of the analysis
        """
        result = []

        try:
            cmd_scancli = ['python3', self.exec_path]
            cmd_scancli.extend(file_paths)
            msg = subprocess.check_output(cmd_scancli).decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise GraalError(cause="Scancode failed at %s, %s" % (file_paths,
                                                                  e.output.decode("utf-8")))
        finally:
            subprocess._cleanup()

        output_content = ''
        outputs_json = []
        for line in msg.split('\n'):
            if line == '':
                if output_content:
                    output_json = json.loads(output_content)[1:]
                    outputs_json.append(output_json)
                    output_content = ''
            else:
                output_content += line

        if output_content:
            output_json = json.loads(output_content)[1:]
            outputs_json.append(output_json)

        for output_json in outputs_json:
            file_info = output_json[0]['files'][0]
            result.append(file_info)

        return result

    def analyze(self, **kwargs):
        """Add information about license

        :param file_path: file path (in case of scancode)
        :param file_paths: file paths ( in case of scancode_cli for concurrent execution on files )

        :returns result: the results of the analysis
        """
        if self.cli:
            result = self.__analyze_scancode_cli(kwargs['file_paths'])
        else:
            result = self.__analyze_scancode(kwargs['file_path'])

        return result
