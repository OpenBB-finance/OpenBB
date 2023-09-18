import os

import unittest
from importlib import import_module

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.registry import RegistryLoader
from typing import Dict


# TODO : this should be imported from utils
def get_provider_fetchers() -> Dict[str, Dict[str, Fetcher]]:
    """Get the fetchers from the provider registry."""
    registry = RegistryLoader.from_extensions()
    provider_fetcher_map: Dict[str, Dict[str, Fetcher]] = {}
    for provider_name, provider_cls in registry.providers.items():
        provider_fetcher_map[provider_name] = {}
        for fetcher_name, fetcher_cls in provider_cls.fetcher_dict.items():
            provider_fetcher_map[provider_name][fetcher_name] = fetcher_cls
    return provider_fetcher_map


# TODO : this should be imported from utils
def check_pattern_in_file(file_path: str, pattern: str) -> bool:
    """Check if a pattern is in a file."""
    with open(file_path) as f:
        lines = f.readlines()
        for line in lines:
            if pattern in line:
                return True
    return False


def get_providers():
    """Get the providers from the provider registry."""
    providers = {}
    registry = RegistryLoader.from_extensions()
    for provider_name, provider_cls in registry.providers.items():
        providers[provider_name] = provider_cls
    return providers


def get_provider_test_files(provider):
    """Given a provider, return the path to the test file."""
    fetchers_dict = provider.fetcher_dict
    fetcher_module_name = fetchers_dict[list(fetchers_dict.keys())[0]].__module__
    parent_module = import_module(fetcher_module_name.split(".")[0])
    parent_module_path = os.path.dirname(parent_module.__file__)
    root_provider_path = os.path.dirname(parent_module_path)

    return os.path.join(
        root_provider_path, "tests", f"test_{provider.name}_fetchers.py"
    )


class ProviderFetcherTest(unittest.TestCase):
    """Tests for providers and fetchers"""

    def test_provider_w_tests(self):
        """Test the provider fetchers - ensure all providers have tests"""
        providers = get_providers()

        for provider_name, provider_cls in providers.items():
            with self.subTest(i=provider_name):
                path = get_provider_test_files(provider_cls)

                self.assertTrue(os.path.exists(path))

    def test_provider_fetchers_w_tests(self):
        """Ensure all the fetchers in each provider have tests."""
        providers = get_providers()

        provider_fetchers = get_provider_fetchers()

        for provider_name, fetcher_dict in provider_fetchers.items():
            for _, fetcher_cls in fetcher_dict.items():
                path = get_provider_test_files(providers[provider_name])

                # check that fetcher_cls is being instantiated in path
                with self.subTest(i=fetcher_cls):
                    self.assertTrue(
                        check_pattern_in_file(path, f"{fetcher_cls.__name__}()")
                    )
