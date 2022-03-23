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
#     Groninger Bugbusters <w.meijer.5@student.rug.nl>
#

import importlib
import inspect

from graal.graal import GraalError
from graal.backends.core.composer import Composer


class AnalyzerCompositionFactory:
    """Factory class for Analyzer Composers"""

    def __init__(self, target_package):
        try:
            self.__composers, self.__kind_to_category = _load_composers_in_package(target_package)
        except Exception as error:
            raise GraalError(cause="Error while loading composers.") from error

    def get_composer(self, category):
        """Returns composer object corresponding with category"""

        if category not in self.__composers:
            raise GraalError(cause=f"Unknown category {category}")

        return self.__composers[category]

    def get_categories(self):
        """Returns all considered categories"""

        return self.__composers.keys()

    def get_category_from_kind(self, kind):
        """Returns the category corresponding with the provided kind."""

        if kind not in self.__kind_to_category:
            raise GraalError(cause=f"Unknown category {kind}")

        return self.__kind_to_category[kind]


def _load_composers_in_package(target_package):
    """
    Loads composer objects from target package.

    :param target_package: package from which composers are loaded.

    :returns: tuple
        dictionary of (category, composer) pairs \\
        dictionary of (kind, category) pairs
    """

    composers = {}
    kind_to_category = {}

    # iterates through all submodules contained in target
    target_module = importlib.import_module(target_package)
    for name, klass in target_module.__dict__.items():
        if name.startswith("_") \
                or not inspect.isclass(klass) \
                or not issubclass(klass, Composer) \
                or klass is Composer:
            continue

        composer = klass()
        composers[composer.get_category()] = composer
        kind_to_category[composer.get_kind()] = composer.get_category()

    return composers, kind_to_category
