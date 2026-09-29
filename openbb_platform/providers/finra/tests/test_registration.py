"""Tests for the conditional provider registration."""

from importlib import reload
from unittest.mock import patch

import openbb_finra

EQUITY_KEYS = {"EquityInfo", "EquitySearch", "EquityShortInterest", "OTCAggregate"}
EQUITY_ALIASES = {
    "FinraEquityInfo",
    "FinraEquitySearch",
    "FinraEquityShortInterest",
    "FinraOTCAggregate",
}

PROVIDER_KEYS = {"FinraBondHistorical", "FinraBondList", "FinraEquityList"}


def _reload_with(installed: set):
    """Reload the package with a controlled set of installed extensions."""
    with patch(
        "importlib.util.find_spec",
        side_effect=lambda name: object() if name in installed else None,
    ):
        return reload(openbb_finra)


class TestFetcherKeys:
    """The fetcher keys track which OpenBB extensions are installed."""

    def test_standalone_aliases(self):
        """With no owner extensions, every shared model takes a FINRA alias."""
        module = _reload_with(set())

        try:
            keys = set(module.finra_provider.fetcher_dict)

            assert keys == EQUITY_ALIASES | {"FinraBondPrices"} | PROVIDER_KEYS
            assert module.EQUITY_INSTALLED is False
            assert module.FIXEDINCOME_INSTALLED is False
        finally:
            reload(openbb_finra)

    def test_standard_keys(self):
        """With the owners installed, the standard keys are used."""
        module = _reload_with({"openbb_equity", "openbb_fixedincome"})

        try:
            keys = set(module.finra_provider.fetcher_dict)

            assert keys == EQUITY_KEYS | {"BondPrices"} | PROVIDER_KEYS
            assert module.EQUITY_INSTALLED is True
            assert module.FIXEDINCOME_INSTALLED is True
        finally:
            reload(openbb_finra)

    def test_key_helper(self):
        """The standard name is used only when its owner is installed."""
        assert openbb_finra._key("BondPrices", "FinraBondPrices", True) == "BondPrices"
        assert openbb_finra._key("BondPrices", "FinraBondPrices", False) == (
            "FinraBondPrices"
        )


class TestProvider:
    """The provider is public and needs no credentials."""

    def test_metadata(self):
        """The provider is named finra and has no credentials."""
        provider = openbb_finra.finra_provider

        assert provider.name == "finra"
        assert provider.credentials == []
        assert provider.website == "https://www.finra.org/finra-data"
        assert len(provider.fetcher_dict) == 8
