"""Tests for cryptocurrency provider extension metadata."""

import json
import unittest
from pathlib import Path


PROVIDER_FILE = Path(__file__).parents[2] / "assets" / "extensions" / "provider.json"


class TestCryptoProviderMetadata(unittest.TestCase):
    """Validate metadata for the requested cryptocurrency providers."""

    @classmethod
    def setUpClass(cls):
        """Load provider metadata once for all tests."""
        cls.providers = json.loads(PROVIDER_FILE.read_text(encoding="utf-8"))
        cls.providers_by_package = {
            provider["packageName"]: provider for provider in cls.providers
        }

    def test_provider_package_names_are_unique(self):
        """Provider packages must have unambiguous registry entries."""
        package_names = [provider["packageName"] for provider in self.providers]

        self.assertEqual(len(package_names), len(set(package_names)))

    def test_requested_crypto_providers_are_registered(self):
        """All providers requested by issue 7177 should be discoverable."""
        expected_packages = {
            "openbb-coingecko",
            "openbb-cryptocompare",
            "openbb-messari",
        }

        self.assertTrue(expected_packages.issubset(self.providers_by_package))

    def test_requested_crypto_provider_credentials(self):
        """Each provider should expose its documented credential name."""
        expected_credentials = {
            "openbb-coingecko": ["coingecko_api_key"],
            "openbb-cryptocompare": ["cryptocompare_api_key"],
            "openbb-messari": ["messari_api_key"],
        }

        for package_name, credentials in expected_credentials.items():
            with self.subTest(package_name=package_name):
                self.assertEqual(
                    self.providers_by_package[package_name]["credentials"],
                    credentials,
                )

    def test_requested_crypto_provider_metadata_is_complete(self):
        """Extension clients need complete display and setup metadata."""
        package_names = (
            "openbb-coingecko",
            "openbb-cryptocompare",
            "openbb-messari",
        )

        for package_name in package_names:
            with self.subTest(package_name=package_name):
                provider = self.providers_by_package[package_name]
                self.assertTrue(provider["optional"])
                self.assertTrue(provider["reprName"].strip())
                self.assertTrue(provider["description"].strip())
                self.assertTrue(provider["website"].startswith("https://"))
                self.assertIn(provider["credentials"][0], provider["instructions"])


if __name__ == "__main__":
    unittest.main()
