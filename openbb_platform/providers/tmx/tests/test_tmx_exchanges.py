"""Tests for the exchange and symbol conventions."""

import pytest

from openbb_tmx.utils.exchanges import (
    EXCHANGE_SUFFIXES,
    NORTH_AMERICAN_EXCHANGES,
    describe_symbol,
)


class TestSymbolDescription:
    """How a symbol addresses the quote feed."""

    @pytest.mark.parametrize(
        ("symbol", "kind", "market"),
        [
            ("AC", "Equity or fund", "Canada"),
            ("^TSX", "Index", "Canada"),
            ("/CGB", "Future", "Canada"),
            ("$USDCAD", "Currency pair", "Canada"),
            ("IBM:US", "Equity or fund", "United States"),
            ("AIR:PA", "Equity or fund", "Paris, France"),
            ("ASML:AS", "Equity or fund", "Amsterdam"),
        ],
    )
    def test_describes_prefix_and_suffix(self, symbol, kind, market):
        described = describe_symbol(symbol)
        assert described["kind"] == kind
        assert described["market"] == market

    def test_lowercase_is_normalized(self):
        assert describe_symbol("air:pa")["symbol"] == "AIR:PA"

    def test_unknown_suffix_has_no_market(self):
        assert describe_symbol("XYZ:ZZ")["market"] is None


class TestExchangeTables:
    """The documented exchange tables."""

    def test_european_exchanges_are_present(self):
        for code in (
            "PA",
            "AS",
            "FF",
            "MA",
            "ST",
            "CO",
            "BR",
            "LS",
            "OS",
            "SM",
            "MI",
            "LN",
        ):
            assert code in EXCHANGE_SUFFIXES

    def test_asian_and_latam_exchanges_are_present(self):
        for code in ("HK", "AU", "NKK", "SH", "CZ", "MB", "BV", "MX", "CL", "AR"):
            assert code in EXCHANGE_SUFFIXES

    def test_canadian_venues_are_present(self):
        for code in ("TSX", "TSXV", "CSE", "ALPHA", "MOE", "CMF"):
            assert code in NORTH_AMERICAN_EXCHANGES
