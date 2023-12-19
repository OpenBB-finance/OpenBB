"""Test for common fields in the provider models that should be standard."""
import glob
import importlib
import inspect
import os
import unittest
from typing import Dict, List, Type

import pytest
from openbb_core.provider import standard_models
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.registry import RegistryLoader


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
    """Get the subclasses of a class defined in a list of python files.

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
    """Given a path, return a list of path components."""
    path_components = []
    head, tail = os.path.split(path)

    while tail:
        path_components.append(tail)
        head, tail = os.path.split(head)

    return path_components


def match_provider_and_fields(
    providers_w_fields: List[Dict[str, List[str]]], duplicated_fields: List[str]
) -> List[str]:
    """Get the provider and fields that match the duplicated fields.

    Given a list of providers with fields and duplicated fields,
    return a list of matching "Provider:'dup_field'".
    """
    matching_provider_fields = []

    for item in providers_w_fields:
        for model, fields in item.items():
            for f in duplicated_fields:
                if f in fields:
                    matching_provider_fields.append(f"{model}:'{f}'")

    return matching_provider_fields


def get_provider_modules():
    """Get provider modules."""
    registry = RegistryLoader.from_extensions()
    modules = []
    for _, provider in registry.providers.items():
        for _, fetcher in provider.fetcher_dict.items():
            modules.append(fetcher.__module__)
    return modules


class ProviderFieldDupesTest(unittest.TestCase):
    """Test for common fields in the provider models that should be standard."""

    @pytest.mark.skip(reason="Need to fix the duplicated fields first.")
    def test_provider_field_dupes(self):
        """Check for duplicate fields in the provider models.

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

        provider_modules = get_provider_modules()

        child_parent_dict = {}

        for module in provider_modules:
            provider_module = importlib.import_module(module)

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
                dupes = [x for x in fields if x in seen or seen.add(x)]

                dupes_str = ", ".join([f"'{x}'" for x in set(dupes)])
                provider_str = (
                    ", ".join(match_provider_and_fields(providers_w_fields, set(dupes)))
                    if dupes
                    else ""
                )

                assert not dupes, (
                    f"The following fields are common among models and should be standardized: {dupes_str}.\n"
                    f"Standard model: {std_cls}, Provider models: {provider_str}\n"
                )
