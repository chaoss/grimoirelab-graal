
from graal.backends.core.analyzers.scc import SCC
from graal.backends.core.composer import Composer
from graal.graal import GraalRepository


class CompositionSccFile(Composer):
    """Analyzer Composition for Lizard Files."""

    SCC_FILE = 'scc_file'
    CATEGORY_COCOM_SCC_FILE = 'code_complexity_' + SCC_FILE

    def compose(self):
        """Creates composition"""

        file_analyzers = [SCC()]
        repo_analyzers = []

        return (file_analyzers, repo_analyzers)

    def get_key(self):
        """Returns project key"""

        return self.CATEGORY_COCOM_SCC_FILE

    def get_kind(self):
        """Returns project kind"""

        return self.SCC_FILE
