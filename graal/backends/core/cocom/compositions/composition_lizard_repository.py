import array

from graal.backends.core.analyzers.analyzer import Analyzer
from graal.backends.core.analyzers.lizard import Lizard
from graal.backends.core.composer import Composer

LIZARD_REPOSITORY = 'lizard_repository'
CATEGORY_COCOM_LIZARD_REPOSITORY = 'code_complexity_' + LIZARD_REPOSITORY


class CompositionLizardRepository(Composer):
    """Analyzer Composition for Lizard Files."""

    def get_composition(self) -> array[Analyzer]:
        return [Lizard(repository_level=True)]

    def get_key(self) -> str:
        return CATEGORY_COCOM_LIZARD_REPOSITORY

    def get_kind(self) -> str:
        return LIZARD_REPOSITORY
