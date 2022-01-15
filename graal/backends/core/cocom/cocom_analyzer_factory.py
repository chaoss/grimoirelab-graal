from graal.backends.core.composer import Composer
from graal.graal import GraalError
from graal.util import create_instances


class CoComAnalyzerFactory:
    """Factory class for Analyzer Compositions"""

    def __init__(self):
        self._load_compositions()

    def _load_compositions(self): 
        self.compositions = {}
        for composition in create_instances("graal.backends.core.cocom.compositions"): 
            self.compositions[composition.get_category()] = composition

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

    def add(self, category, composer):
        """Adds composer to the factory"""

        self.compositions[category] = composer
