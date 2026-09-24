"""Tests for the bond list model."""

import asyncio
from urllib.parse import urlparse

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_finra.models.bond_list import FinraBondListData, FinraBondListFetcher


def _fetch(params):
    """Run the fetcher."""
    return asyncio.run(FinraBondListFetcher.fetch_data(params, {}))


@pytest.mark.freeze_time("2026-09-23")
class TestBondList:
    """Every bond of one TRACE product is listed."""

    def test_treasury_list(self, fake_session):
        """Every outstanding Treasury note and bond is returned once."""
        session = fake_session("bond_list_treasury")
        result = _fetch({"bond_type": "TS"})

        assert all(isinstance(row, FinraBondListData) for row in result)
        assert len(result) == 150
        assert {row.bond_type for row in result} == {"U.S. Treasury"}
        assert {row.product_sub_type for row in result} == {"Notes, Bonds"}
        assert {row.price_type for row in result} <= {None, "Decimal"}
        assert len({row.cusip for row in result}) == len(result)

        body = session.calls[1]["json"]

        assert "multiFieldMatchFilters" not in body
        assert "domainFilters" not in body
        assert body["orFilters"][0]["compareFilters"][0]["fieldValue"] == "2026-09-23"

    def test_include_matured(self, fake_session, response, trace_answer):
        """Matured bonds are listed when asked for, without the outstanding filter."""
        session = fake_session(
            responder=lambda call: (
                response(400, "{}")
                if call["method"] == "GET"
                else trace_answer([{"cusip": "X", "finraSecurityIdentifier": 1}])
            )
        )
        result = _fetch({"bond_type": "MBS", "include_matured": True})

        assert [row.cusip for row in result] == ["X"]
        assert "orFilters" not in session.calls[1]["json"]
        assert urlparse(session.calls[1]["url"]).path.endswith(
            "/mortgageBackedSecurities"
        )

    def test_empty(self, fake_session, response, trace_answer):
        """A product with no bonds is empty."""
        fake_session(
            responder=lambda call: (
                response(400, "{}") if call["method"] == "GET" else trace_answer([])
            )
        )

        with pytest.raises(EmptyDataError, match="no TBA bonds"):
            _fetch({"bond_type": "TBA"})
