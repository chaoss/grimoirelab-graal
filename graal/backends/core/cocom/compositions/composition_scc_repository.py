from graal.backends.core.analyzers.scc import SCC
from graal.backends.core.composer import Composer
from graal.graal import GraalRepository


class CompositionSccRepository(Composer):
    """Analyzer Composition for Lizard Files."""

    SCC_REPOSITORY = 'scc_repository'
    CATEGORY_COCOM_SCC_REPOSITORY = 'code_complexity_' + SCC_REPOSITORY

    def compose(self):
        """Creates composition"""

        file_analyzers = []
        repo_analyzers = [SCC()]

        return (file_analyzers, repo_analyzers)

    def get_key(self):
        """Returns project key"""

        return self.CATEGORY_COCOM_SCC_REPOSITORY

    def get_kind(self):
        """Returns project kind"""

        return self.SCC_REPOSITORY
