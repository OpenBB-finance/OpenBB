"""Tests for the bond prices model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_finra.models.bond_prices import (
    FinraBondPricesData,
    FinraBondPricesFetcher,
    FinraBondPricesQueryParams,
    _filters,
)

MONTH_NAMES = {
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
}


def _fetch(params):
    """Run the fetcher."""
    return asyncio.run(FinraBondPricesFetcher.fetch_data(params, {}))


class TestLookup:
    """CUSIPs and FINRA symbols resolve to their product before they are read."""

    def test_mixed_products(self, fake_session, response, trace_answer):
        """A corporate CUSIP, a Treasury CUSIP, and a symbol for the first bond."""
        session = fake_session("bond_prices_lookup")
        result = {
            row.cusip: row
            for row in _fetch({"cusip": "037833eh9,912810UG1,AAPL5231623"})
        }

        assert all(isinstance(row, FinraBondPricesData) for row in result.values())
        assert set(result) == {"037833EH9", "912810UG1"}

        apple = result["037833EH9"]

        assert apple.bond_type == "Corporate & Agency"
        assert apple.product_sub_type == "Corporate Bond"
        assert apple.symbol == "AAPL5231623"
        assert apple.coupon_type == "Fixed Plain Vanilla"
        assert apple.industry_group == "Electronics"
        assert apple.grade == "Investment Grade"
        assert apple.coupon_rate == 1.4
        assert result["912810UG1"].bond_type == "U.S. Treasury"
        assert session.closed

    def test_lookup_keeps_matured_bonds(self, fake_session, response, trace_answer):
        """A lookup is not limited to outstanding bonds."""
        session = fake_session("bond_prices_lookup")
        _fetch({"cusip": "037833EH9,912810UG1,AAPL5231623"})
        bodies = [call["json"] for call in session.calls if call["method"] == "POST"]

        assert all("orFilters" not in body for body in bodies)

    def test_bond_type_mismatch(self, fake_session, response, trace_answer):
        """A lookup restricted to another product is empty."""
        rows = [{"cusip": "037833EH9", "bondType": "CA"}]
        fake_session(
            responder=lambda call: (
                response(400, "{}") if call["method"] == "GET" else trace_answer(rows)
            )
        )

        with pytest.raises(EmptyDataError):
            _fetch({"cusip": "037833EH9", "bond_type": "TS"})


@pytest.mark.freeze_time("2026-09-23")
class TestSearch:
    """Bonds are searched with filters pushed to TRACE."""

    def test_issuer(self, fake_session, response, trace_answer):
        """Every word of the issuer matches, on outstanding bonds only."""
        session = fake_session("bond_prices_issuer")
        result = _fetch({"issuer_name": "apple inc"})

        assert result
        assert all("APPLE" in (row.issuer_name or "") for row in result)
        assert len({row.finra_security_id for row in result}) == len(result)
        assert session.calls[1]["json"]["orFilters"]

    def test_treasury_window(self, fake_session, response, trace_answer):
        """Treasury maturities are bounded on the server."""
        fake_session("bond_prices_treasury")
        result = _fetch(
            {
                "bond_type": "TS",
                "maturity_date_min": "2030-01-01",
                "maturity_date_max": "2031-12-31",
            }
        )

        assert result
        assert all(row.bond_type == "U.S. Treasury" for row in result)
        assert all(
            "2030-01-01" <= str(row.maturity_date) <= "2031-12-31" for row in result
        )

    def test_tba(self, fake_session, response, trace_answer):
        """TBA contracts match on the issuing agency and have no maturity filter."""
        session = fake_session("bond_prices_tba")
        result = _fetch({"bond_type": "TBA", "issuer_name": "ginnie", "limit": 5})
        body = session.calls[1]["json"]

        assert len(result) == 5
        assert all("Ginnie" in (row.issuing_agency or "") for row in result)
        assert all(row.settlement_month in MONTH_NAMES for row in result)
        assert all(row.product_sub_type == "To-Be-Announced" for row in result)
        assert "orFilters" not in body
        assert body["multiFieldMatchFilters"][0]["fields"] == [
            {"name": "issuingAgency", "boost": 1}
        ]

    def test_abs(self, fake_session, response, trace_answer):
        """Asset-backed stubs are excluded and coupons bounded."""
        session = fake_session("bond_prices_abs")
        result = _fetch(
            {"bond_type": "ABS", "coupon_min": 3, "coupon_max": 4, "limit": 5}
        )
        compare = session.calls[1]["json"]["compareFilters"]

        assert len(result) == 5
        assert all(3 <= (row.coupon_rate or 0) <= 4 for row in result)
        assert result[0].sub_product_type == "Student Loan"
        assert result[0].product_sub_type == "Asset-Backed Security"
        assert {
            "fieldName": "finraSecurityIdentifier",
            "fieldValue": None,
            "compareType": "NOT_EQUAL",
        } in compare

    def test_mbs(self, fake_session, response, trace_answer):
        """A filtered mortgage search is allowed."""
        fake_session("bond_prices_mbs")
        result = _fetch(
            {"bond_type": "MBS", "issuer_name": "ginnie", "coupon_min": 7, "limit": 5}
        )

        assert len(result) == 5
        assert all(row.bond_type == "Mortgage-Backed Securities" for row in result)
        assert all(
            row.mortgage_product in {"Single Family", "Multi-Family"} for row in result
        )
        assert all(len(row.amortization_type or "") > 1 for row in result)


class TestGuards:
    """Queries TRACE cannot serve are refused before any request."""

    def test_unfiltered_mortgages(self, fake_session, response, trace_answer):
        """An unfiltered mortgage universe is refused."""
        fake_session(responder=lambda call: response(400, "{}"))

        with pytest.raises(OpenBBError, match="Mortgage-Backed Securities universe"):
            _fetch({"bond_type": "MBS"})

    def test_one_unsupported_parameter(self):
        """A single unsupported parameter is named."""
        with pytest.raises(OpenBBError, match="does not publish isin. Remove it."):
            FinraBondPricesFetcher.transform_query({"isin": "US037833EH90"})

    def test_several_unsupported_parameters(self):
        """Several unsupported parameters are named together."""
        with pytest.raises(OpenBBError, match="country, lei. Remove them."):
            FinraBondPricesFetcher.transform_query({"country": "US", "lei": "X"})

    def test_empty_result(self, fake_session, response, trace_answer):
        """No matching bond is empty."""
        fake_session(
            responder=lambda call: (
                response(400, "{}") if call["method"] == "GET" else trace_answer([])
            )
        )

        with pytest.raises(EmptyDataError):
            _fetch({"issuer_name": "zzzz"})


class TestFilters:
    """The query translates to TRACE filters."""

    @pytest.mark.freeze_time("2026-09-23")
    def test_all_bounds(self):
        """Coupon, yield, and maturity bounds and the outstanding filter."""
        query = FinraBondPricesQueryParams(
            coupon_min=1,
            coupon_max=5,
            ytm_min=2,
            ytm_max=6,
            maturity_date_min="2030-01-01",
            maturity_date_max="2040-01-01",
        )
        payload = _filters(query, "CA", False)

        assert payload["compareFilters"] == [
            {"fieldName": "couponRate", "fieldValue": "1.0", "compareType": "GTE"},
            {"fieldName": "couponRate", "fieldValue": "5.0", "compareType": "LTE"},
            {"fieldName": "lastSaleYield", "fieldValue": "2.0", "compareType": "GTE"},
            {"fieldName": "lastSaleYield", "fieldValue": "6.0", "compareType": "LTE"},
            {
                "fieldName": "maturityDate",
                "fieldValue": "2030-01-01",
                "compareType": "GTE",
            },
            {
                "fieldName": "maturityDate",
                "fieldValue": "2040-01-01",
                "compareType": "LTE",
            },
        ]
        assert (
            payload["orFilters"][0]["compareFilters"][0]["fieldValue"] == "2026-09-23"
        )

    def test_include_matured(self):
        """Including matured bonds drops the outstanding filter."""
        payload = _filters(
            FinraBondPricesQueryParams(include_matured=True), "CA", False
        )

        assert payload == {}

    def test_upper_cased_identifiers(self):
        """Identifiers are upper-cased."""
        assert FinraBondPricesQueryParams(cusip="037833eh9").cusip == "037833EH9"
