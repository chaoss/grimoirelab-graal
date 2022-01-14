from graal.backends.core.analyzers.analyzer import Analyzer
from graal.backends.core.cocom.compositions import CocomComposition


class CoComAnalyzerFactory:
    """Factory class for Analyzer Compositions"""

    def __init__(self):
        self.compositions = {
        }

    def build(self, category):
        """
        Returns composition of analyzers corresponding
        with the provided category
        """

        composition = self.compositions[category]
        composition.compose()

        return composition

    def get_composer(self, category):
        """Returns composer object corresponding with category"""

        return self.compositions[category]

    def add(self, category, composer):
        """Adds composer to the factory"""

        self.compositions[category] = composer

    def exists(self, category):
        """Returns true if the category has a composition"""

        return category in self.compositions
