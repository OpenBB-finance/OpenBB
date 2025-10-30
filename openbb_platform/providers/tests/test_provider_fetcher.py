"""Test if providers and fetchers are covered by tests."""

import os
import unittest
from importlib import import_module

from openbb_core.provider.abstract.provider import Provider
from openbb_core.provider.registry import RegistryLoader

from providers.tests.utils.unit_tests_generator import (
    check_pattern_in_file,
    get_provider_fetchers,
)


def get_provider_test_files(provider: Provider):
    """Given a provider, return the path to the test file."""
    fetchers_dict = provider.fetcher_dict
    fetcher_module_name = fetchers_dict[list(fetchers_dict.keys())[0]].__module__
    parent_module = import_module(fetcher_module_name.split(".")[0])
    parent_module_path = os.path.dirname(parent_module.__file__)  # type: ignore
    root_provider_path = os.path.dirname(parent_module_path)
    provider_name = provider.name.lower()

    return os.path.join(
        root_provider_path, "tests", f"test_{provider_name}_fetchers.py"
    )


class ProviderFetcherTest(unittest.TestCase):
    """Tests for providers and fetchers."""

    providers: dict[str, Provider] = RegistryLoader.from_extensions().providers

    def test_provider_w_tests(self):
        """Test the provider fetchers and ensure all providers have tests."""

        for provider_name, provider_cls in self.providers.items():
            with self.subTest(i=provider_name):
                path = get_provider_test_files(provider_cls)

                self.assertTrue(os.path.exists(path))

    def test_provider_fetchers_w_tests(self):
        """Ensure all the fetchers in each provider have tests."""

        provider_fetchers = get_provider_fetchers()

        for provider_name, fetcher_dict in provider_fetchers.items():
            for _, fetcher_cls in fetcher_dict.items():
                path = get_provider_test_files(self.providers[provider_name])

                # check that fetcher_cls is being instantiated in path
                with self.subTest(i=fetcher_cls):
                    self.assertTrue(check_pattern_in_file(path, f"{fetcher_cls.__name__}()"))  # type: ignore
