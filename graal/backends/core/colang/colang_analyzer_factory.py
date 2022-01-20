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
#     wmeijer221 <w.meijer.5@student.rug.nl>
#

from graal.graal import GraalError

from graal.backends.core.colang.compositions.composition_cloc import *
from graal.backends.core.colang.compositions.composition_linguist import *


class CoLangAnalyzerFactory:
    """Factory class for Analyzer Compositions"""

    version = '0.1.0'

    def __init__(self):
        self.__load_compositions()

    def __load_compositions(self):
        # TODO: add dynamic loading. Look at Graal, as it's used there for loading backends.
        #       when doing so, the factory can be completely abstracted (i.e. one factory
        #       can be used for all backends; have them load the concrete analyzers).
        # TODO: do something about kind + category.
        #       You shouldn't be able to load a composition with the composition kind.
        self.compositions = {}
        self.__add(CompositionLinguist())
        self.__add(CompositionCloc())

    def __add(self, composer):
        """Adds composer to the factory"""

        self.compositions[composer.get_category()] = composer
        self.compositions[composer.get_kind()] = composer

    def build(self, category):
        """Returns composition of analyzers"""

        composer = self.get_composer(category)
        composition = composer.get_composition()

        return composition

    def get_composer(self, category):
        """Returns composer object corresponding with category"""

        if not category in self.compositions:
            raise GraalError(cause=f"Unknown category {category}")

        return self.compositions[category]

    def get_categories(self):
        """Returns all considered categories"""

        return self.compositions.keys()
