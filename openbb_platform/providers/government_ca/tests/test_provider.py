"""Tests for ``openbb_government_ca.__init__`` — provider registration."""

from __future__ import annotations

from openbb_core.provider.abstract.provider import Provider

import openbb_government_ca as pkg


class TestProviderRegistration:
    """The provider is registered with the right name and metadata."""

    def test_provider_object_exists(self):
        """``government_ca_provider`` is a ``Provider`` instance."""
        assert isinstance(pkg.government_ca_provider, Provider)

    def test_provider_name(self):
        """The provider is registered under the ``government_ca`` name."""
        assert pkg.government_ca_provider.name == "government_ca"

    def test_provider_repr_name(self):
        """The human-readable name mentions both BoC and StatsCan."""
        repr_name = pkg.government_ca_provider.repr_name
        assert "Bank of Canada" in repr_name
        assert "Statistics Canada" in repr_name

    def test_fetcher_dict_is_dict(self):
        """The fetcher dict is a dict — populated with Fase 4 fetchers."""
        assert isinstance(pkg.government_ca_provider.fetcher_dict, dict)

    def test_fetcher_dict_contains_economic_indicators(self):
        """The fetcher dict contains the StatsCan economic indicators fetcher.

        Registered under either the standard key ``EconomicIndicators``
        (when openbb-economy is installed) or the local alias
        ``StatsCanEconomicIndicators`` (standalone mode).
        """
        fetcher_dict = pkg.government_ca_provider.fetcher_dict
        assert (
            "EconomicIndicators" in fetcher_dict
            or "StatsCanEconomicIndicators" in fetcher_dict
        )


class TestKeyHelper:
    """The ``_key`` alias helper mirrors the OECD V5 pattern."""

    def test_key_returns_standard_when_economy_installed(self, monkeypatch):
        """When ``openbb-economy`` is installed, the standard key is returned."""
        monkeypatch.setattr(pkg, "ECONOMY_INSTALLED", True)
        assert pkg._key("CurrencyHistorical", "BoCFX") == "CurrencyHistorical"

    def test_key_returns_alias_when_economy_missing(self, monkeypatch):
        """When ``openbb-economy`` is NOT installed, the local alias is returned."""
        monkeypatch.setattr(pkg, "ECONOMY_INSTALLED", False)
        assert pkg._key("CurrencyHistorical", "BoCFX") == "BoCFX"
