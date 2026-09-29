"""Tests for the conditional provider registration."""

from importlib import reload
from unittest.mock import patch

import openbb_deribit

STANDARD_KEYS = {
    "FuturesCurve",
    "FuturesHistorical",
    "FuturesInfo",
    "FuturesInstruments",
    "OptionsChains",
}
ALIAS_KEYS = {
    "DeribitFuturesCurve",
    "DeribitFuturesHistorical",
    "DeribitFuturesInfo",
    "DeribitFuturesInstruments",
    "DeribitOptionsChains",
}
PROVIDER_KEYS = {
    "DeribitAnnouncements",
    "DeribitAprHistory",
    "DeribitBlockRfqTrades",
    "DeribitBookSummary",
    "DeribitCombos",
    "DeribitCurrencies",
    "DeribitDeliveryPrices",
    "DeribitExpirations",
    "DeribitFundingChart",
    "DeribitFundingRateHistory",
    "DeribitHistoricalVolatility",
    "DeribitIndexHistorical",
    "DeribitIndexPrice",
    "DeribitInstruments",
    "DeribitOrderBook",
    "DeribitSettlements",
    "DeribitTicker",
    "DeribitTradeVolumes",
    "DeribitTrades",
    "DeribitVolatilityIndex",
}


def _reload_with(installed: set):
    """Reload the package with a controlled set of installed extensions."""
    with patch(
        "importlib.util.find_spec",
        side_effect=lambda name: object() if name in installed else None,
    ):
        return reload(openbb_deribit)


class TestFetcherKeys:
    """The fetcher_dict keys track which OpenBB extensions are installed."""

    def test_standalone_aliases_when_nothing_installed(self):
        """With no standard extensions, the shared models take a Deribit alias."""
        module = _reload_with(set())

        try:
            keys = set(module.deribit_provider.fetcher_dict)

            assert keys >= ALIAS_KEYS
            assert not STANDARD_KEYS & keys
            assert module.DERIVATIVES_INSTALLED is False
            assert module.CHARTING_INSTALLED is False
        finally:
            reload(openbb_deribit)

    def test_standard_keys_when_derivatives_installed(self):
        """With openbb-derivatives present, the standard keys are used."""
        module = _reload_with({"openbb_derivatives", "openbb_charting"})

        try:
            keys = set(module.deribit_provider.fetcher_dict)

            assert keys >= STANDARD_KEYS
            assert not ALIAS_KEYS & keys
            assert module.DERIVATIVES_INSTALLED is True
            assert module.CHARTING_INSTALLED is True
        finally:
            reload(openbb_deribit)

    def test_provider_models_never_alias(self):
        """The Deribit-only models keep their key whatever is installed."""
        for installed in (set(), {"openbb_derivatives"}):
            module = _reload_with(installed)

            try:
                assert set(module.deribit_provider.fetcher_dict) >= PROVIDER_KEYS
            finally:
                reload(openbb_deribit)

    def test_key_helper(self):
        """``_key`` picks the standard name only when the owner is installed."""
        assert openbb_deribit._key("FuturesCurve", "DeribitFuturesCurve", True) == (
            "FuturesCurve"
        )
        assert openbb_deribit._key("FuturesCurve", "DeribitFuturesCurve", False) == (
            "DeribitFuturesCurve"
        )


class TestProvider:
    """The provider advertises itself as public and credential-free."""

    def test_metadata(self):
        """The provider needs no credentials and names itself Deribit."""
        provider = openbb_deribit.deribit_provider

        assert provider.name == "deribit"
        assert provider.credentials == []
        assert "deribit.com" in provider.website
        assert len(provider.fetcher_dict) == 25
