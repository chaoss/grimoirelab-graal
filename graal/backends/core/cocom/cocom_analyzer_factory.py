from socket import IPPORT_RESERVED
from graal.backends.core.composer import Composer
from graal.graal import GraalError
from graal.util import create_instances

from graal.backends.core.cocom.compositions.composition_lizard_file import *
from graal.backends.core.cocom.compositions.composition_lizard_repository import *
from graal.backends.core.cocom.compositions.composition_scc_file import *
from graal.backends.core.cocom.compositions.composition_scc_repository import *


class CoComAnalyzerFactory:
    """Factory class for Analyzer Compositions"""

    def __init__(self):
        self._load_compositions()

    def _load_compositions(self):
        # TODO: add dynamic loading.
        self.compositions = {
            CATEGORY_COCOM_LIZARD_FILE: CompositionLizardFile(),
            CATEGORY_COCOM_LIZARD_REPOSITORY: CompositionLizardRepository(),
            CATEGORY_COCOM_SCC_FILE: CompositionSccFile(),
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
            raise GraalError(cause="Unknown category %s" % category)

        return self.compositions[category]

    def get_categories(self): 
        """Returns all considered categories"""

        return self.compositions.keys()

    def add(self, category, composer):
        """Adds composer to the factory"""

        self.compositions[category] = composer
