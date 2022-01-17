from asyncore import file_dispatcher
from graal.backends.core.analyzers.cloc import Cloc
from graal.backends.core.analyzers.lizard import Lizard
from graal.backends.core.composer import Composer
import array

LIZARD_FILE = 'lizard_file'
CATEGORY_COCOM_LIZARD_FILE = 'code_complexity_' + LIZARD_FILE


class CompositionLizardFile(Composer):
    """Analyzer Composition for Lizard Files."""

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

    def get_category(self):
        return CATEGORY_COCOM_LIZARD_FILE

    def get_kind(self):
        return LIZARD_FILE

    def get_composition(self):
        return [Cloc(repository_level=False), Lizard(repository_level=False)]

    def merge_results(self, results):
        merged = {}

        for result in results:
            for entry in result:
                file_path = entry['file_path']

                if not file_path in merged:
                    merged[file_path] = entry
                else:
                    merged[file_path].update(entry)
        
        return list(merged.values())
