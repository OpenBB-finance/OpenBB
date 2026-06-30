"""Unit tests for ``openbb_ecb`` provider registration and ``_installed``."""

import openbb_ecb.assets  # noqa: F401  (cover the assets package marker)
from openbb_ecb import _installed, ecb_provider


def test_provider_metadata():
    """The provider exposes its identity and fetchers."""
    assert ecb_provider.name == "ECB"
    assert ecb_provider.website == "https://data.ecb.europa.eu"
    # ECB-specific models are always registered, regardless of owners.
    keys = set(ecb_provider.fetcher_dict)
    assert {"EcbMfiInterestRates", "EcbReleases", "EcbEligibleAssets"} <= keys
    # 12 model fetchers in total.
    assert len(ecb_provider.fetcher_dict) == 12


def test_key_helpers_both_branches(monkeypatch):
    """Each key helper returns the standard name when installed, else the alias."""
    for flag, helper in (
        ("ECONOMY_INSTALLED", _installed.economy_key),
        ("CURRENCY_INSTALLED", _installed.currency_key),
        ("FIXEDINCOME_INSTALLED", _installed.fixedincome_key),
    ):
        monkeypatch.setattr(_installed, flag, True)
        assert helper("Standard", "Alias") == "Standard"
        monkeypatch.setattr(_installed, flag, False)
        assert helper("Standard", "Alias") == "Alias"
