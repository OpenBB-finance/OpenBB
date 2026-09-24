"""Tests for the conditional provider registration."""

from importlib import reload
from unittest.mock import patch

import openbb_cboe


def _reload_with(installed: set[str]):
    """Reload the package with a controlled set of installed extensions."""
    with patch(
        "importlib.util.find_spec",
        side_effect=lambda name: object() if name in installed else None,
    ):
        return reload(openbb_cboe)


class TestFetcherKeys:
    """The fetcher_dict keys track which OpenBB extensions are installed."""

    def test_standalone_aliases_when_nothing_installed(self):
        """With no standard extensions, every model registers under a Cboe alias."""
        module = _reload_with(set())

        try:
            keys = set(module.cboe_provider.fetcher_dict)

            assert "CboeIndexSnapshots" in keys
            assert "CboeEquityQuote" in keys
            assert "CboeOptionsChains" in keys
            assert "CboeFuturesCurve" in keys
            assert "CboeIndexDocuments" in keys
            assert "EtfHistorical" not in keys
            assert not {"IndexSnapshots", "EquityQuote", "OptionsChains"} & keys
        finally:
            reload(openbb_cboe)

    def test_standard_keys_when_everything_installed(self):
        """With the standard extensions present, the standard keys are used."""
        module = _reload_with(
            {
                "openbb_equity",
                "openbb_etf",
                "openbb_index",
                "openbb_derivatives",
                "openbb_charting",
            }
        )

        try:
            keys = set(module.cboe_provider.fetcher_dict)

            assert {
                "AvailableIndices",
                "EquityHistorical",
                "EquityQuote",
                "EquitySearch",
                "EtfHistorical",
                "FuturesCurve",
                "IndexConstituents",
                "IndexHistorical",
                "IndexSearch",
                "IndexSnapshots",
                "OptionsChains",
            } <= keys
            assert module.CHARTING_INSTALLED is True
        finally:
            reload(openbb_cboe)

    def test_etf_only(self):
        """``EtfHistorical`` registers whenever ``openbb-etf`` is present."""
        module = _reload_with({"openbb_etf"})

        try:
            keys = set(module.cboe_provider.fetcher_dict)

            assert "EtfHistorical" in keys
            assert "CboeEquityHistorical" in keys
        finally:
            reload(openbb_cboe)

    def test_key_helper(self):
        """``_key`` picks the standard name only when the owner is installed."""
        assert openbb_cboe._key("IndexSnapshots", "CboeIndexSnapshots", True) == (
            "IndexSnapshots"
        )
        assert openbb_cboe._key("IndexSnapshots", "CboeIndexSnapshots", False) == (
            "CboeIndexSnapshots"
        )
