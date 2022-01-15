import array

from graal.backends.core.analyzers.analyzer import Analyzer
from graal.backends.core.analyzers.scc import SCC
from graal.backends.core.composer import Composer
from graal.graal import GraalRepository

SCC_REPOSITORY = 'scc_repository'
CATEGORY_COCOM_SCC_REPOSITORY = 'code_complexity_' + SCC_REPOSITORY


class CompositionSccRepository(Composer):
    """Analyzer Composition for Lizard Files"""

    def get_composition(self) -> array[Analyzer]:
        return [SCC()]

    def get_key(self) -> str:
        return CATEGORY_COCOM_SCC_REPOSITORY

    def get_kind(self) -> str:
        return SCC_REPOSITORY
