from graal.backends.core.analyzers.cloc import Cloc
from graal.backends.core.analyzers.lizard import Lizard
from graal.backends.core.composer import Composer

LIZARD_FILE = 'lizard_file'
CATEGORY_COCOM_LIZARD_FILE = 'code_complexity_' + LIZARD_FILE


class CompositionLizardFile(Composer):
    """Analyzer Composition for Lizard Files."""

    version = '0.1.0'

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
