import fnmatch
import glob
import importlib
import inspect
import os
import unittest
from typing import Dict, List, Type

import providers
from openbb_provider import standard_models
from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


def get_module(file_path: str, package_name: str):
    """
    Given a file path and its package, loads the module.

    Parameters
    ----------
        file_path (str): The path to the file.
        package (str): The package where the module is located.

    Returns
    -------
        module: The loaded module.
    """
    # Get the module name by removing the file extension and getting the basename
    module_name = os.path.splitext(os.path.basename(file_path))[0]

    # Import the module using the package name and the module name
    return importlib.import_module(f"{package_name}.{module_name}")


def get_subclasses_w_keys(module: object, cls: Type) -> Dict[Type, List[str]]:
    """Given a module and a class, return the subclasses of the class and their fields.

    Parameters
    ----------
        module (object): The module containing the classes.
        cls (Type): The base class.

    Returns
    -------
        Dict[Type, List[str]]: A dictionary mapping each subclass to a list of its field names.
    """
    subclasses = {}
    module_members = inspect.getmembers(module)

    for _, obj in module_members:
        if inspect.isclass(obj) and issubclass(obj, cls) and obj != cls:
            subclasses[obj] = list(obj.__fields__.keys())
    return subclasses


def get_subclasses(
    python_files: List[str], package_name: str, cls: Type
) -> Dict[Type, List[str]]:
    """
    Given a list of python files, and a class, return a dictionary of
    subclasses of that class that are defined in those files.

    Parameters
    ----------
        python_files (List[str]): A list of file paths to Python files.
        package_name (str): The name of the package.
        cls (Type): The base class.

    Returns
    -------
        Dict[str, Type]: A dictionary where the keys are the subclass names
        and the values are the subclasses themselves.
    """
    subclasses = {}

    for file_path in python_files:
        module = get_module(file_path, package_name)

        subclasses.update(get_subclasses_w_keys(module, cls))

    return subclasses


def child_parent_map(map_: Dict, parents: Dict, module: object) -> None:
    """
    Generate a mapping of child classes to their parent classes and provider fields.

    Parameters
    ----------
        map_ (dict): The dict to append to.
        parents (dict): A dictionary of parent classes and their standard fields.
        module (module): The module containing the classes.
    """
    for cls, std_fields in parents.items():
        # Check if class name is not already in the map
        if cls.__name__ not in map_:
            map_[cls.__name__] = []

        # Get the first subclass and its provider fields
        sub_w_keys = get_subclasses_w_keys(module, cls)
        if sub_w_keys:
            subclass = list(sub_w_keys.keys())[0]
            provider_fields = list(sub_w_keys.values())[0]

            # Remove standard fields from provider fields
            provider_fields = [
                field for field in provider_fields if field not in std_fields
            ]

            # If there are provider fields, add them to the map
            if provider_fields:
                map_[cls.__name__].append({subclass.__name__: provider_fields})


def get_path_components(path: str):
    """Given a path, return a list of path components"""

    path_components = []
    head, tail = os.path.split(path)

    while tail:
        path_components.append(tail)
        head, tail = os.path.split(head)

    return path_components


def build_provider_module_path(module_name: str, file_path: str):
    """Given a module name and a file path, return the full path to the module"""

    splited_path = get_path_components(file_path)
    file = splited_path[0].split(".")[0]
    models_dir = splited_path[1]
    openbb_provider = splited_path[2]
    provider = splited_path[3]

    return f"{module_name}.{provider}.{openbb_provider}.{models_dir}.{file}"


class ProviderFieldDupesTest(unittest.TestCase):
    """Test for common fields in the provider models that should be standard."""

    def test_provider_field_dupes(self):
        """
        This function checks for duplicate fields in the provider models
        and identifies the fields that should be standardized.
        """

        standard_models_directory = os.path.dirname(standard_models.__file__)
        standard_models_files = glob.glob(
            os.path.join(standard_models_directory, "*.py")
        )

        standard_query_classes = get_subclasses(
            standard_models_files, standard_models.__name__, QueryParams
        )
        standard_data_classes = get_subclasses(
            standard_models_files, standard_models.__name__, Data
        )

        provider_model_files = []
        providers_path = providers.__path__[0]

        # Walk through the directory tree
        for root, _, files in os.walk(providers_path):
            if "models" not in root:
                continue

            # Use fnmatch to find .py files
            for filename in fnmatch.filter(files, "*.py"):
                provider_model_files.append(os.path.join(root, filename))

        child_parent_dict = {}

        for file in provider_model_files:
            module_path = build_provider_module_path(providers.__name__, file)
            provider_module = importlib.import_module(module_path)

            # query classes
            child_parent_map(child_parent_dict, standard_query_classes, provider_module)

            # data classes
            child_parent_map(child_parent_dict, standard_data_classes, provider_module)

        # remove keys with no values
        child_parent_dict = {k: v for k, v in child_parent_dict.items() if v}

        for std_cls in child_parent_dict:
            with self.subTest(i=std_cls):
                providers_w_fields = child_parent_dict[std_cls]

                fields = []
                provider_models = []

                for provider_cls in providers_w_fields:
                    provider_models.extend(list(provider_cls.keys()))
                    fields.extend(list(provider_cls.values())[0])

                seen = set()
                dupes = (x for x in fields if x in seen or seen.add(x))

                assert not dupes, (
                    f"The following fields are common among models and should be standardized: {dupes}.\n"
                    f"Standard model: {std_cls}, Provider models: {', '.join(provider_models)}\n"
                )
