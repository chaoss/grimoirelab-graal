from graal.backends.core.analyzers.analyzer import Analyzer


class Composer:
    """Template class for composition of analyzers"""

    def get_composition(self):
        """Returns the corresponding composition"""

        raise NotImplementedError

    def get_key(self) -> str:
        """Returns key used to identify this composition"""

        raise NotImplementedError

    def get_kind(self) -> str: 
        """Returns more readable name of this composition"""

        # TODO: is this really necessary? 
        raise NotImplementedError
