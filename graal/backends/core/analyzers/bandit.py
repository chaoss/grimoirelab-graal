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

from collections import Counter
import subprocess

from graal.graal import GraalError
from .analyzer import Analyzer


class Bandit(Analyzer):
    """A wrapper for Bandit, a tool designed to find common security issues in Python code.
    To do this Bandit processes each file, builds an AST from it, and runs appropriate plugins against the AST nodes.
    Once Bandit has finished scanning all the files it generates a report.
    """

    version = '0.2.2'

    def analyze(self, **kwargs):
        """Add security issue data using Bandit.

        :param worktreepath: folder path
        :param details: if True, it returns information about single vulnerabilities

        :returns result: dict of the results of the analysis
        """
        folder_path = kwargs['worktreepath']
        details = kwargs['details']

        try:
            msg = subprocess.check_output(['bandit', '-r', folder_path]).decode("utf-8")
        except subprocess.CalledProcessError as e:
            msg = e.output.decode("utf-8")
            if not msg.startswith("Run started:"):
                raise GraalError(cause="Bandit failed at %s, %s" % (folder_path, msg))
        finally:
            subprocess._cleanup()

        vulns = []
        severities = []
        confidences = []
        loc = None
        descr = None
        severity = None
        confidence = None
        in_issue = False
        in_overview = False
        lines = msg.lower().split('\n')
        for line in lines:
            if line.startswith(">> issue: "):
                descr = line.replace(">> issue: ", "")
                in_issue = True
            elif line.startswith("code scanned:"):
                in_overview = True
            else:
                if in_issue:
                    line = line.strip()
                    if line.startswith("severity:"):
                        tokens = [t.strip(":") for t in line.split(" ")]
                        severity = tokens[1]
                        confidence = tokens[-1]
                        severities.append(severity)
                        confidences.append(confidence)
                    elif line.startswith("location:"):
                        location = line.replace("location: ", "").replace(folder_path, "")
                        line = location.split(":")[-1]
                        file = location.replace(":" + line, "")
                        vuln = {"file": file,
                                "line": int(line),
                                "severity": severity,
                                "confidence": confidence,
                                "descr": descr}
                        vulns.append(vuln)
                        severity = None
                        confidence = None
                        descr = None
                        in_issue = False
                elif in_overview:
                    if line.startswith("\ttotal lines of code:"):
                        loc = line.split(":")[1].strip()
                        loc = int(loc)
                        break
                else:
                    continue

        result = {'loc_analyzed': loc,
                  'num_vulns': len(vulns),
                  'by_severity': self.__create_ranked_dict(severities),
                  'by_confidence': self.__create_ranked_dict(confidences)}

        if details:
            result['vulns'] = vulns

        return result

    @staticmethod
    def __create_ranked_dict(lst):
        output = {
            "undefined": 0,
            "low": 0,
            "medium": 0,
            "high": 0
        }

        if not lst:
            return output

        counted = Counter(lst)
        for k in counted.keys():
            output[k] = counted[k]

        return output
