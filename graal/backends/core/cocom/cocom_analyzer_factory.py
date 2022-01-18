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

from graal.backends.core.composer import Composer
from graal.graal import GraalError

from graal.backends.core.cocom.compositions.composition_lizard_file import *
from graal.backends.core.cocom.compositions.composition_lizard_repository import *
from graal.backends.core.cocom.compositions.composition_scc_file import *
from graal.backends.core.cocom.compositions.composition_scc_repository import *


class CoComAnalyzerFactory:
    """Factory class for Analyzer Compositions"""

    version = '0.1.0'

    def __init__(self):
        self._load_compositions()

    def _load_compositions(self):
        # TODO: add dynamic loading. Look at Graal, as it's used there for loading backends.
        # TODO: do something about kind + category.
        #       You shouldn't be able to load a composition with the composition kind.
        self.compositions = {
            CATEGORY_COCOM_LIZARD_FILE: CompositionLizardFile(),
            LIZARD_FILE: CompositionLizardFile(),
            CATEGORY_COCOM_LIZARD_REPOSITORY: CompositionLizardRepository(),
            LIZARD_REPOSITORY: CompositionLizardRepository(),
            CATEGORY_COCOM_SCC_FILE: CompositionSccFile(),
            SCC_FILE: CompositionSccFile(),
            SCC_REPOSITORY: CompositionSccRepository(),
            CATEGORY_COCOM_SCC_REPOSITORY: CompositionSccRepository()
        }

    def build(self, category):
        """Returns composition of analyzers"""

        composer: Composer = self.get_composer(category)
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

    def add(self, category, composer):
        """Adds composer to the factory"""

        self.compositions[category] = composer