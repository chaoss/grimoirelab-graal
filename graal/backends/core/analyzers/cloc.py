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


class Cloc(Analyzer):
    """A wrapper for Cloc.

    This class allows to call Cloc over a file, parses
    the result of the analysis and returns it as a dict.
    """
    version = '0.1.1'

    def analyze(self, **kwargs):
        """Add information about LOC, blank and commented lines using CLOC

        :param file_path: file path

        :returns result: dict of the results of the analysis
        """
        result = {'blanks': 0,
                  'comments': 0,
                  'loc': 0
                  }
        file_path = kwargs['file_path']
        flag = False

        try:
            msg = subprocess.check_output(['cloc', file_path]).decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise GraalError(cause="Cloc failed at %s, %s" % (file_path, e.output.decode("utf-8")))
        finally:
            subprocess._cleanup()

        for line in msg.split("\n"):
            if flag:
                if not line.startswith("-----"):
                    digested = " ".join(line.split())
                    info_file = digested.split(" ")
                    blank_lines = int(info_file[2])
                    commented_lines = int(info_file[3])
                    loc = int(info_file[4])

                    result['blanks'] = blank_lines
                    result['comments'] = commented_lines
                    result['loc'] = loc
                    break

            if line.lower().startswith("language"):
                flag = True

        result['ext'] = file_path.split(".")[-1]
        return result
