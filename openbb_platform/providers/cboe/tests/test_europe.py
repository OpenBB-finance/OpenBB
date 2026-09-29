"""Tests for the Cboe Europe symbology and book transport."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_cboe.utils import europe


class TestEuSymbolDirectory:
    """Per-venue symbology listing."""

    def test_maps_listings_and_skips_unnamed(self):
        """Listings are mapped to symbol/name/isin and unnamed rows dropped."""
        payload = {
            "symbolsLookupData": [
                {"name": "SHEL", "company_name": "Shell PLC", "isin": "GB00BP6MXD84"},
                {"name": "", "company_name": "Ghost Row", "isin": "XX0000000000"},
            ]
        }

        with patch(
            "openbb_cboe.utils.helpers.get_cboe_data",
            new=AsyncMock(return_value=payload),
        ):
            listings = asyncio.run(europe.get_eu_symbol_directory("bxe"))

        assert listings == [
            {
                "symbol": "SHEL",
                "name": "Shell PLC",
                "isin": "GB00BP6MXD84",
                "market": "BXE",
            }
        ]

    def test_empty_symbology_raises(self):
        """A venue with no symbology raises."""
        with (
            patch(
                "openbb_cboe.utils.helpers.get_cboe_data",
                new=AsyncMock(return_value={}),
            ),
            pytest.raises(OpenBBError, match="No symbology was returned for CXE"),
        ):
            asyncio.run(europe.get_eu_symbol_directory())


class TestEuCompanyNames:
    """Cross-venue company name map."""

    def test_first_venue_wins_and_failures_are_skipped(self):
        """Names merge across venues, first listing first, failed venues skipped."""
        directories = {
            "bxe": [
                {"symbol": "SHEL", "name": "Shell PLC", "isin": "x", "market": "BXE"},
                {"symbol": "NONAME", "name": "", "isin": "x", "market": "BXE"},
            ],
            "cxe": [
                {"symbol": "SHEL", "name": "Shell Again", "isin": "x", "market": "CXE"}
            ],
        }

        async def directory(market, use_cache=True):
            if market not in directories:
                raise OpenBBError(f"No symbology was returned for {market.upper()}.")
            return directories[market]

        with patch.object(europe, "get_eu_symbol_directory", new=directory):
            names = asyncio.run(europe.get_eu_company_names())

        assert names == {"SHEL": "Shell PLC"}


class TestEuBook:
    """Per-venue order book."""

    def test_returns_the_data_block(self):
        """A successful response hands back its data block."""
        payload = {
            "success": True,
            "data": {"company": "Shell PLC", "last": 25.0, "orders": []},
        }

        with patch(
            "openbb_cboe.utils.helpers.get_cboe_data",
            new=AsyncMock(return_value=payload),
        ):
            book = asyncio.run(europe.get_eu_book("SHEL", "cxe"))

        assert book["company"] == "Shell PLC"

    def test_unsuccessful_response_raises(self):
        """A response without success raises."""
        with (
            patch(
                "openbb_cboe.utils.helpers.get_cboe_data",
                new=AsyncMock(return_value={"success": False}),
            ),
            pytest.raises(OpenBBError, match="No book was returned for SHEL on CXE"),
        ):
            asyncio.run(europe.get_eu_book("SHEL"))

    def test_unlisted_symbol_raises(self):
        """A success payload with no company and no last price is unlisted."""
        payload = {"success": True, "data": {"company": "", "last": 0}}

        with (
            patch(
                "openbb_cboe.utils.helpers.get_cboe_data",
                new=AsyncMock(return_value=payload),
            ),
            pytest.raises(OpenBBError, match="NOPE is not listed on DXE"),
        ):
            asyncio.run(europe.get_eu_book("NOPE", "dxe"))
