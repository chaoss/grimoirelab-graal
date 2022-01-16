from graal.backends.core.analyzers.cloc import Cloc
from graal.backends.core.analyzers.lizard import Lizard
from graal.backends.core.composer import Composer

LIZARD_FILE = 'lizard_file'
CATEGORY_COCOM_LIZARD_FILE = 'code_complexity_' + LIZARD_FILE


class CompositionLizardFile(Composer):
    """Analyzer Composition for Lizard Files."""

    ALLOWED_EXTENSIONS = ['java', 'py', 'php', 'scala', 'js', 'rb', 'cs', 'cpp', 'c', 'lua', 'go', 'swift']

    def get_composition(self):
        return [Cloc(), Lizard(repository_level=False)]

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

    def get_key(self) -> str:
        return CATEGORY_COCOM_LIZARD_FILE

    def get_kind(self) -> str:
        return LIZARD_FILE
