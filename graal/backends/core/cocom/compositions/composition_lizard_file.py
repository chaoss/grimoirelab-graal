
from graal.backends.core.analyzers.cloc import Cloc
from graal.backends.core.analyzers.lizard import Lizard
from graal.backends.core.composer import Composer
from graal.graal import GraalRepository


class CompositionLizardFile(Composer):
    """Analyzer Composition for Lizard Files."""

    LIZARD_FILE = 'lizard_file'
    CATEGORY_COCOM_LIZARD_FILE = 'code_complexity_' + LIZARD_FILE

    ALLOWED_EXTENSIONS = ['java', 'py', 'php', 'scala', 'js', 'rb', 'cs', 'cpp', 'c', 'lua', 'go', 'swift']

    def compose(self):
        """Creates composition"""

        file_analyzers = [Cloc(), Lizard()]
        repo_analyzers = []

        return (file_analyzers, repo_analyzers)

    # def analyze(self, **kwargs):
    #     """Performs analysis"""

    #     kwargs = {'file_path': file_path}

    #     cloc_analysis = self.cloc.analyze(**kwargs)

    #     if GraalRepository.extension(file_path) not in self.ALLOWED_EXTENSIONS:
    #         return cloc_analysis

    #     kwargs['details'] = self.details
    #     file_analysis = self.lizard.analyze(**kwargs)
    #     # the LOC returned by CLOC is replaced by the one obtained with Lizard
    #     # for consistency purposes

    #     file_analysis['blanks'] = cloc_analysis['blanks']
    #     file_analysis['comments'] = cloc_analysis['comments']

    #     return file_analysis

    def get_key(self):
        """Returns project key"""

        return self.CATEGORY_COCOM_LIZARD_FILE

    def get_kind(self):
        """Returns project kind"""

        return self.LIZARD_FILE
