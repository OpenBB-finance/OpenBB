"""Tests for the security list model."""

import asyncio

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_finra.models.equity_list import FinraEquityListData, FinraEquityListFetcher

ROWS = [
    {"symbol": "AAPL", "security_type": "ST", "tier": "T1"},
    {"symbol": "ACHR.W", "tier": "OTCE"},
    {"symbol": "PDI", "security_type": "FC", "tier": "T2"},
    {"symbol": "SPY", "security_type": "FE", "tier": "T1"},
    {"symbol": "VFIAX", "security_type": "FO"},
]


@pytest.fixture
def listed(monkeypatch):
    """Serve a fixed list of securities."""

    async def _list():
        return [dict(row) for row in ROWS]

    monkeypatch.setattr("openbb_finra.utils.directory.list_securities", _list)


def _fetch(params):
    """Run the fetcher."""
    return asyncio.run(FinraEquityListFetcher.fetch_data(params, {}))


class TestSecurityList:
    """The list is filtered to the requested security type."""

    @pytest.mark.parametrize(
        ("security_type", "symbols"),
        [
            ("all", ["AAPL", "ACHR.W", "PDI", "SPY", "VFIAX"]),
            ("stock", ["AAPL"]),
            ("etf", ["SPY"]),
            ("closed_end_fund", ["PDI"]),
            ("other", ["ACHR.W", "VFIAX"]),
        ],
    )
    def test_types(self, listed, security_type, symbols):
        """Each type keeps only its securities."""
        result = _fetch({"security_type": security_type})

        assert all(isinstance(row, FinraEquityListData) for row in result)
        assert [row.symbol for row in result] == symbols

    def test_codes_are_translated(self, monkeypatch):
        """Security types, product types, and exchange ids are named."""

        async def _list():
            return [
                {
                    "symbol": "SPY",
                    "security_type": "FE",
                    "product_type": "CTS",
                    "listing_market_id": "16",
                    "composite_exchange_id": "126",
                }
            ]

        monkeypatch.setattr("openbb_finra.utils.directory.list_securities", _list)
        row = _fetch({})[0].model_dump()

        assert row["security_type"] == "ETF"
        assert row["product_type"] == "NYSE and Regional Exchange-Listed (CTA Plan)"
        assert row["listing_market"] == "NYSE Arca"
        assert row["composite_market"] == "USCOMP"
        assert "listing_market_id" not in row
        assert "composite_exchange_id" not in row

    def test_default_is_all(self, listed):
        """Every security is listed by default."""
        assert len(_fetch({})) == len(ROWS)

    def test_empty(self, monkeypatch):
        """A type with no securities is empty."""

        async def _list():
            return [{"symbol": "AAPL", "security_type": "ST"}]

        monkeypatch.setattr("openbb_finra.utils.directory.list_securities", _list)

        with pytest.raises(EmptyDataError, match="No etf securities"):
            _fetch({"security_type": "etf"})
