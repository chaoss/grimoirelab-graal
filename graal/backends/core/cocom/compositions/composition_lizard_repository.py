
from graal.backends.core.analyzers.cloc import Cloc
from graal.backends.core.analyzers.lizard import Lizard
from graal.backends.core.composer import Composer
from graal.graal import GraalRepository


class CompositionLizardRepository(Composer):
    """Analyzer Composition for Lizard Files."""

    LIZARD_REPOSITORY = 'lizard_repository'
    CATEGORY_COCOM_LIZARD_REPOSITORY = 'code_complexity_' + LIZARD_REPOSITORY

    def compose(self):
        """Creates composition"""

        file_analyzers = []
        repo_analyzers = [Lizard()]

        return (file_analyzers, repo_analyzers)

    def get_key(self):
        """Returns project key"""

        return self.CATEGORY_COCOM_LIZARD_REPOSITORY

    def get_kind(self):
        """Returns project kind"""

        return self.LIZARD_REPOSITORY
