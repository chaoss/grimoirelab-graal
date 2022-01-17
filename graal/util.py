
import array
from inspect import isclass
from pkgutil import iter_modules
from importlib import import_module

from graal.graal import GraalRepository




# TODO: this doesn't work in Graal for some reason. Figure out why.
def create_instances(package_dir: str, super_class: type) -> array:
    """
    Returns list of instances of the super class contained in the package directory.

    :param package_dir: directory in which subclasses exist
    :param super_class: parent class of the subclasses. 
    """

    instances = []

    # iterate through the modules in the current package
    for _, module_name, _ in iter_modules([package_dir]):
        
        print(module_name)

        # import the module and iterate through its attributes
        module = import_module(f"{package_dir}.{module_name}")
        for klass_name in dir(module):
            klass = getattr(module, klass_name)

            # imports subclasses
            if isclass(klass) and klass != super_class and issubclass(klass, super_class):
                instance = klass()
                instances.append(instance)

    return instances
