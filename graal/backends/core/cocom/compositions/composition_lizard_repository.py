from graal.backends.core.analyzers.lizard import Lizard
from graal.backends.core.analyzers.cloc import Cloc
from graal.backends.core.composer import Composer

LIZARD_REPOSITORY = 'lizard_repository'
CATEGORY_COCOM_LIZARD_REPOSITORY = 'code_complexity_' + LIZARD_REPOSITORY


class CompositionLizardRepository(Composer):
    """Analyzer Composition for Lizard Files."""

    def get_composition(self):
        return [Cloc(repository_level=True), Lizard(repository_level=True)]

    def get_key(self):
        return CATEGORY_COCOM_LIZARD_REPOSITORY

    def get_kind(self):
        return LIZARD_REPOSITORY
