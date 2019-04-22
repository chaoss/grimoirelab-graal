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
#     Valerio Cosentino <valcos@bitergia.com>
#

import subprocess

from graal.graal import (GraalError,
                         GraalRepository)
from .analyzer import Analyzer


class Cloc(Analyzer):
    """A wrapper for Cloc.

    This class allows to call Cloc over a file, parses
    the result of the analysis and returns it as a dict.
    """
    version = '0.2.0'

    def __analyze_file(self, message):
        """Add information about LOC, blank and commented lines using CLOC for a given file

        :param message: message from standard output after execution of cloc

        :returns result: dict of the results of the analysis over a file
        """

        flag = False
        results = {
            "blanks": 0,
            "comments": 0,
            "loc": 0
        }

        for line in message.strip().split("\n"):
            if flag:
                if not line.startswith("-----"):
                    digested = " ".join(line.split())
                    info_file = digested.split(" ")
                    blank_lines = int(info_file[2])
                    commented_lines = int(info_file[3])
                    loc = int(info_file[4])
                    results["blanks"] = blank_lines
                    results["comments"] = commented_lines
                    results["loc"] = loc
                    break

            if line.lower().startswith("language"):
                flag = True

        return results

    def __analyze_repository(self, message):
        """Add information LOC, total files, blank and commented lines using CLOC for the entire repository

        :param message: message from standard output after execution of cloc

        :returns result: dict of the results of the analysis over a repository
        """

        results = {}
        flag = False

        for line in message.strip().split("\n"):
            if flag:
                if line.lower().startswith("sum"):
                    break
                elif not line.startswith("-----"):
                    digested = " ".join(line.split())
                    info_file = digested.split(" ")
                    blank_lines = int(info_file[2])
                    commented_lines = int(info_file[3])
                    loc = int(info_file[4])
                    language = info_file[0]
                    language_result = {
                        "total_files": int(info_file[1]),
                        "blanks": blank_lines,
                        "comments": commented_lines,
                        "loc": loc
                    }
                    results[language] = language_result

            if line.lower().startswith("language"):
                flag = True

        return results

    def analyze(self, **kwargs):
        """Add information using CLOC

        :param file_path: file path
        :param repository_level: set to True if analysis has to be performed on a repository

        :returns result: dict of the results of the analysis
        """

        file_path = kwargs['file_path']
        repository_level = kwargs.get('repository_level', False)

        try:
            message = subprocess.check_output(['cloc', file_path]).decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise GraalError(cause="Cloc failed at %s, %s" % (file_path, e.output.decode("utf-8")))
        finally:
            subprocess._cleanup()

        if repository_level:
            results = self.__analyze_repository(message)
        else:
            results = self.__analyze_file(message)
            results['ext'] = GraalRepository.extension(file_path)

        return results
