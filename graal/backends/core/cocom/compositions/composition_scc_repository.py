from graal.backends.core.analyzers.scc import SCC
from graal.backends.core.composer import Composer

SCC_REPOSITORY = 'scc_repository'
CATEGORY_COCOM_SCC_REPOSITORY = 'code_complexity_' + SCC_REPOSITORY


class CompositionSccRepository(Composer):
    """Analyzer Composition for Lizard Files"""

    def get_composition(self):
        return [SCC()]

    def get_category(self):
        return CATEGORY_COCOM_SCC_REPOSITORY

    def get_kind(self):
        return SCC_REPOSITORY
