"""Tests for the Federal Reserve Central Bank Holdings Fetcher."""

# ruff: noqa: I001

import asyncio
from datetime import date as dateType

import pytest

from openbb_federal_reserve.utils import ny_fed_api
from openbb_federal_reserve.models.central_bank_holdings import (
    FederalReserveCentralBankHoldingsData,
    FederalReserveCentralBankHoldingsFetcher,
    FederalReserveCentralBankHoldingsQueryParams,
)


class _FakeSoma:
    """Recording stand-in for ``SomaHoldings`` whose methods return canned rows."""

    calls: list[tuple[str, dict]] = []

    @classmethod
    def reset(cls):
        """Clear the recorded call log."""
        cls.calls = []

    async def get_agency_holdings(self, **kwargs):
        """Record an agency-holdings call and return one canned row."""
        type(self).calls.append(("agency", kwargs))
        return [{"asOfDate": "2024-01-03", "securityDescription": "AGY", "cusip": "X"}]

    async def get_treasury_holdings(self, **kwargs):
        """Record a treasury-holdings call and return one canned row."""
        type(self).calls.append(("treasury", kwargs))
        return [{"asOfDate": "2024-01-03", "securityTypes": "Bills"}]

    async def get_summary(self):
        """Record a summary call and return one canned row."""
        type(self).calls.append(("summary", {}))
        return [{"asOfDate": "2024-01-03", "total": 100}]


@pytest.fixture()
def fake_soma(monkeypatch):
    """Patch ``SomaHoldings`` with the recording fake and reset its call log."""
    _FakeSoma.reset()
    monkeypatch.setattr(ny_fed_api, "SomaHoldings", _FakeSoma)
    return _FakeSoma


def _extract(query):
    """Run the async ``aextract_data`` to completion and return its rows."""
    return asyncio.run(
        FederalReserveCentralBankHoldingsFetcher.aextract_data(query, {})
    )


class TestQueryParams:
    """Tests for ``FederalReserveCentralBankHoldingsQueryParams``."""

    def test_defaults(self):
        """The default holding type is ``all_treasury`` with flags off."""
        q = FederalReserveCentralBankHoldingsQueryParams()
        assert q.holding_type == "all_treasury"
        assert q.summary is False
        assert q.wam is False
        assert q.monthly is False

    def test_transform_query_builds_params(self):
        """``transform_query`` constructs the params model from a dict."""
        q = FederalReserveCentralBankHoldingsFetcher.transform_query(
            {"holding_type": "mbs", "summary": True}
        )
        assert isinstance(q, FederalReserveCentralBankHoldingsQueryParams)
        assert q.holding_type == "mbs"
        assert q.summary is True


class TestExtractData:
    """Tests for ``FederalReserveCentralBankHoldingsFetcher.aextract_data``."""

    def test_default_treasury(self, fake_soma):
        """A treasury holding type routes to ``get_treasury_holdings``."""
        _extract(FederalReserveCentralBankHoldingsQueryParams(holding_type="bills"))
        assert fake_soma.calls[-1] == (
            "treasury",
            {"as_of": None, "holding_type": "bills"},
        )

    def test_default_agency(self, fake_soma):
        """``all_agency`` routes to ``get_agency_holdings`` with ``all``."""
        _extract(
            FederalReserveCentralBankHoldingsQueryParams(holding_type="all_agency")
        )
        assert fake_soma.calls[-1] == ("agency", {"as_of": None, "holding_type": "all"})

    def test_agency_subtype(self, fake_soma):
        """A specific agency type (``cmbs``) maps to security type ``agency``."""
        _extract(FederalReserveCentralBankHoldingsQueryParams(holding_type="cmbs"))
        assert fake_soma.calls[-1] == (
            "agency",
            {"as_of": None, "holding_type": "cmbs"},
        )

    def test_date_as_of_passed_through(self, fake_soma):
        """A ``date`` query param is formatted and forwarded as ``as_of``."""
        _extract(
            FederalReserveCentralBankHoldingsQueryParams(
                holding_type="notesbonds", date=dateType(2024, 1, 2)
            )
        )
        assert fake_soma.calls[-1] == (
            "treasury",
            {"as_of": "2024-01-02", "holding_type": "notesbonds"},
        )

    def test_summary_takes_priority(self, fake_soma):
        """``summary=True`` routes to ``get_summary``."""
        _extract(FederalReserveCentralBankHoldingsQueryParams(summary=True))
        assert fake_soma.calls[-1] == ("summary", {})

    def test_monthly_treasury(self, fake_soma):
        """``monthly=True`` requests monthly treasury holdings."""
        _extract(
            FederalReserveCentralBankHoldingsQueryParams(
                holding_type="all_treasury", monthly=True
            )
        )
        assert fake_soma.calls[-1] == (
            "treasury",
            {"monthly": True, "holding_type": "all"},
        )

    def test_treasury_wam(self, fake_soma):
        """``wam=True`` on a treasury type requests the treasury WAM."""
        _extract(
            FederalReserveCentralBankHoldingsQueryParams(
                holding_type="all_treasury", wam=True
            )
        )
        assert fake_soma.calls[-1] == ("treasury", {"wam": True, "as_of": None})

    def test_agency_wam(self, fake_soma):
        """``wam=True`` on an agency type requests the agency WAM."""
        _extract(
            FederalReserveCentralBankHoldingsQueryParams(
                holding_type="all_agency", wam=True
            )
        )
        assert fake_soma.calls[-1] == ("agency", {"wam": True, "as_of": None})

    def test_cusip_agency(self, fake_soma):
        """A CUSIP with an agency type routes to ``get_agency_holdings`` by cusip."""
        _extract(
            FederalReserveCentralBankHoldingsQueryParams(
                holding_type="all_agency", cusip="AAA,BBB", date=dateType(2024, 1, 2)
            )
        )
        assert fake_soma.calls[-1] == (
            "agency",
            {"cusip": "AAA,BBB", "as_of": "2024-01-02"},
        )

    def test_cusip_treasury(self, fake_soma):
        """A CUSIP with a treasury type routes to ``get_treasury_holdings`` by cusip."""
        _extract(
            FederalReserveCentralBankHoldingsQueryParams(
                holding_type="all_treasury", cusip="CCC"
            )
        )
        assert fake_soma.calls[-1] == ("treasury", {"cusip": "CCC", "as_of": None})


class TestTransformData:
    """Tests for ``FederalReserveCentralBankHoldingsFetcher.transform_data``."""

    def test_validates_rows_into_models(self):
        """Each raw dict becomes a validated data model with aliases applied."""
        rows = [{"asOfDate": "2024-01-03", "securityTypes": "Bills", "cusip": "X"}]
        out = FederalReserveCentralBankHoldingsFetcher.transform_data(
            FederalReserveCentralBankHoldingsQueryParams(), rows
        )
        assert len(out) == 1
        assert out[0].date == dateType(2024, 1, 3)
        assert out[0].security_type == "Bills"
        assert out[0].cusip == "X"

    def test_empty_input_yields_empty_output(self):
        """An empty raw list transforms into an empty result list."""
        out = FederalReserveCentralBankHoldingsFetcher.transform_data(
            FederalReserveCentralBankHoldingsQueryParams(), []
        )
        assert out == []


class TestData:
    """Tests for ``FederalReserveCentralBankHoldingsData`` validators."""

    def test_security_type_empty_is_none(self):
        """An empty ``security_type`` normalises to ``None``."""
        d = FederalReserveCentralBankHoldingsData.model_validate(
            {"asOfDate": "2024-01-03", "securityTypes": ""}
        )
        assert d.security_type is None

    def test_security_type_list_is_joined(self):
        """A list ``security_type`` is joined into a comma-separated string."""
        d = FederalReserveCentralBankHoldingsData.model_validate(
            {"asOfDate": "2024-01-03", "securityTypes": ["Bills", "Notes"]}
        )
        assert d.security_type == "Bills,Notes"

    def test_security_type_string_passes_through(self):
        """A scalar ``security_type`` string passes through unchanged."""
        d = FederalReserveCentralBankHoldingsData.model_validate(
            {"asOfDate": "2024-01-03", "securityTypes": "TIPs"}
        )
        assert d.security_type == "TIPs"

    def test_percent_normalization(self):
        """``coupon`` and ``spread`` are divided by 100 when present."""
        d = FederalReserveCentralBankHoldingsData.model_validate(
            {"asOfDate": "2024-01-03", "coupon": "2.5", "spread": "0.5"}
        )
        assert d.coupon == 0.025
        assert d.spread == 0.005

    def test_percent_sentinel_is_none(self):
        """The ``''`` sentinel coupon normalises to ``None``."""
        d = FederalReserveCentralBankHoldingsData.model_validate(
            {"asOfDate": "2024-01-03", "coupon": "''"}
        )
        assert d.coupon is None

    def test_empty_strings_cleared(self):
        """Empty-string, ``''`` and ``'0'`` sentinels become ``None``."""
        d = FederalReserveCentralBankHoldingsData.model_validate(
            {
                "asOfDate": "2024-01-03",
                "issuer": "",
                "term": "''",
                "securityDescription": "0",
            }
        )
        assert d.issuer is None
        assert d.term is None
        assert d.description is None

    def test_non_dict_payload_passes_through(self):
        """A non-dict payload bypasses the empty-string cleanup validator."""
        d = FederalReserveCentralBankHoldingsData.model_validate(
            FederalReserveCentralBankHoldingsData(asOfDate="2024-01-03")
        )
        assert d.date == dateType(2024, 1, 3)
