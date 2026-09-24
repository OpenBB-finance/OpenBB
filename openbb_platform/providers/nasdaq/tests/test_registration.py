"""Tests for the Nasdaq provider registration."""

import pytest

import openbb_nasdaq
from openbb_nasdaq import _key, nasdaq_provider


class TestProvider:
    """Cover the provider object."""

    def test_identity(self):
        """The provider is registered under its own name."""
        assert nasdaq_provider.name == "nasdaq"
        assert nasdaq_provider.repr_name == "Nasdaq"
        assert nasdaq_provider.website == "https://www.nasdaq.com"

    def test_requires_no_credentials(self):
        """Every dataset reads the public Nasdaq website API."""
        assert not nasdaq_provider.credentials

    def test_every_fetcher_is_a_fetcher(self):
        """Each registered entry is a fetcher class."""
        from openbb_core.provider.abstract.fetcher import Fetcher

        for name, fetcher in nasdaq_provider.fetcher_dict.items():
            assert issubclass(fetcher, Fetcher), name

    def test_fetcher_names_are_unique(self):
        """No model name is registered twice."""
        assert len(nasdaq_provider.fetcher_dict) == len(
            set(nasdaq_provider.fetcher_dict)
        )

    def test_provider_owned_models_are_always_present(self):
        """Datasets no OpenBB extension claims are always registered."""
        for model in (
            "MarketMovers",
            "NasdaqMarketStatus",
            "NasdaqPriceQuote",
            "NasdaqNordicScreener",
            "NasdaqNordicInfo",
            "NasdaqNordicFundamentals",
            "NasdaqNordicDividends",
            "NasdaqNordicHistorical",
            "NasdaqNordicHistoricalTrades",
            "NasdaqNordicMovers",
            "NasdaqNordicNews",
        ):
            assert model in nasdaq_provider.fetcher_dict


class TestKeyResolution:
    """Cover the standard-versus-standalone model key."""

    def test_installed_extension_keeps_the_standard_key(self):
        """The standard model name is used when its extension is installed."""
        assert _key("EtfHoldings", "NasdaqEtfHoldings", True) == "EtfHoldings"

    def test_absent_extension_uses_the_alias(self):
        """The Nasdaq alias is used when the extension is absent."""
        assert _key("EtfHoldings", "NasdaqEtfHoldings", False) == "NasdaqEtfHoldings"


class TestInstallFlags:
    """Cover the extension detection flags."""

    @pytest.mark.parametrize(
        "flag",
        [
            "EQUITY_INSTALLED",
            "ETF_INSTALLED",
            "INDEX_INSTALLED",
            "CRYPTO_INSTALLED",
            "DERIVATIVES_INSTALLED",
            "ECONOMY_INSTALLED",
            "NEWS_INSTALLED",
        ],
    )
    def test_flags_are_boolean(self, flag):
        """Every namespace flag resolves to a boolean."""
        assert isinstance(getattr(openbb_nasdaq, flag), bool)

    def test_standard_models_track_their_flag(self):
        """A standard key is present exactly when its extension is installed."""
        registered = nasdaq_provider.fetcher_dict

        assert ("EtfHoldings" in registered) is openbb_nasdaq.ETF_INSTALLED
        assert ("NasdaqEtfHoldings" in registered) is not openbb_nasdaq.ETF_INSTALLED
