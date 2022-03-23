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
#     James Walden <james.walden@acm.org>
#     Valerio Cosentino <valcos@bitergia.com>
#     inishchith <inishchith@gmail.com>
#

import subprocess
from pathlib import Path
from statistics import mean, median, stdev

from graal.graal import (GraalError,
                         GraalRepository)
from .analyzer import Analyzer

class QMCalc(Analyzer):
    """A wrapper for QMCalc (cqmetrics)

    This class allows to call QMCalc with a file, parses
    the result of the analysis and returns it as a dict.

    :param diff_timeout: max time to compute diffs of a given file
    """
    version = '0.0.1'
    metrics_names_file = 'cqmetrics-names.tsv'
    metrics_names_path = Path(__file__).parent.absolute().joinpath(metrics_names_file)

    def __init__(self):
        try:
            with open(QMCalc.metrics_names_path) as f:
                name_string = f.read().rstrip()
        except:
            raise GraalError(cause="Error on reading cqmetrics metric names from %" % metrics_names_path)
            
        self.metrics_names = name_string.split("\t")

    def __analyze_file(self, message, file_path, relative_path):
        """Convert tab-separated metrics values from qmcalc into a dictionary

        :param message: message from standard output after execution of qmcalc

        :returns result: dict of the results of qmcalc analysis of a file
        """

        value_strings = message.rstrip().split("\t")
        results = dict(zip(self.metrics_names, value_strings))

        # Coerce each metric value to correct type or NA
        for metric in results:
            if results[metric] == '':
                results[metric] = 'NA'
            else:
                if (metric[0] == 'n' or metric.endswith("_length_min") or 
                        metric.endswith("_length_max") or 
                        metric.endswith("_nesting_min") or 
                        metric.endswith("_nesting_max")):
                    results[metric] = int(results[metric])
                else:
                    results[metric] = float(results[metric])

        path = Path(file_path)
        results['file_path'] = path.relative_to(relative_path).as_posix()
        results['file_extension'] = path.suffix

        return results

    def __analyze_repository(self, message, file_paths, relative_path):
        """Return metrics for all files in repository.

        :param message: message from standard output after execution of qmcalc
        :param file_paths: array of paths to C source and header files
        :param relative_path: path to repository containing source files

        :returns result: dict of the results of the analysis over a repository
        """

        # Create array of file metric dictionaries
        file_metrics = []
        i = 0
        for line in message.strip().split("\n"):
            file_results = self.__analyze_file(line, file_paths[i], relative_path)
            file_metrics.append(file_results)
            i = i + 1

        # Build results dictionary with summary data and file_metrics
        results = { 
                    'nfiles': len(file_metrics),
                    'files': file_metrics
                  }
        for metric_name in self.metrics_names:
            metrics = [ file[metric_name] for file in file_metrics ]
            metrics = list(filter(lambda x: x != 'NA', metrics))

            if metric_name == 'filename':
                continue
            elif metric_name.endswith('min'):
                results[metric_name] = min(metrics)
            elif metric_name.endswith('max'):
                results[metric_name] = max(metrics)
            elif metric_name.endswith('mean'):
                results[metric_name] = mean(metrics)
            elif metric_name.endswith('median'):
                results[metric_name] = median(metrics)
            elif metric_name.endswith('sd'):
                mean_metric = metric_name.replace('sd', 'mean')
                mean_metrics = [ file[mean_metric] for file in file_metrics ]
                mean_metrics = list(filter(lambda x: x != 'NA', mean_metrics))
                results[metric_name] = stdev(mean_metrics)
            else:
                results[metric_name] = sum(metrics)

        return results

    def analyze(self, **kwargs):
        """Add information using qmcalc

        :param file_path: path of a single C source or header file to analyze
        :param repository_level: set to True if analysis has to be performed on a repository

        :returns result: dict of the results of the analysis
        """

        repository_level = kwargs.get('repository_level', False)
        if repository_level:
            file_paths = list(Path(kwargs['repository_path']).glob('**/*.[ch]'))
        else:
            file_paths = [ kwargs['file_path'] ]

        # If no C source/header files exist, return empty array for results
        if len(file_paths) == 0:
            return []

        # Run qmcalc to compute metrics for all file paths
        try:
            qmcalc_command = ['qmcalc'] + file_paths
            message = subprocess.check_output(qmcalc_command).decode('utf-8')
        except subprocess.CalledProcessError as e:
            raise GraalError(cause="QMCalc failed at %s, %s" % (file_path, e.output.decode('utf-8')))
        finally:
            subprocess._cleanup()

        if repository_level:
            results = self.__analyze_repository(message, file_paths, kwargs['repository_path'])
        else:
            results = self.__analyze_file(message, file_paths[0], kwargs['file_path'])

        return results
