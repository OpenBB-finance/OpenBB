"""Unit tests for the Federal Reserve Overnight Bank Funding Rate fetcher."""

# ruff: noqa: I001

from datetime import date as dateType, datetime
from unittest.mock import AsyncMock

import pytest

from openbb_core.provider.utils.errors import EmptyDataError
from openbb_federal_reserve.models.overnight_bank_funding_rate import (
    FederalReserveOvernightBankFundingRateData,
    FederalReserveOvernightBankFundingRateFetcher,
    FederalReserveOvernightBankFundingRateQueryParams,
)


def _ref_rate(**overrides) -> dict:
    """Return a single OBFR ``refRates`` row as the NY Fed API emits it."""
    row = {
        "effectiveDate": "2024-06-06",
        "type": "OBFR",
        "percentRate": 5.32,
        "percentPercentile1": 5.25,
        "percentPercentile25": 5.31,
        "percentPercentile75": 5.33,
        "percentPercentile99": 5.39,
        "volumeInBillions": 285,
        "revisionIndicator": "",
    }
    row.update(overrides)
    return row


class TestFederalReserveOvernightBankFundingRateData:
    """Tests for the OBFR data model and validators."""

    def test_normalize_percent_divides_by_100(self):
        """Non-zero, non-null percent values are divided by 100."""
        d = FederalReserveOvernightBankFundingRateData.model_validate(_ref_rate())
        assert d.rate == pytest.approx(0.0532)
        assert d.percentile_1 == pytest.approx(0.0525)
        assert d.percentile_99 == pytest.approx(0.0539)

    def test_normalize_percent_zero_stays_zero(self):
        """A zero percent value is preserved as zero."""
        d = FederalReserveOvernightBankFundingRateData.model_validate(
            _ref_rate(percentRate=0)
        )
        assert d.rate == 0

    def test_normalize_percent_none_passes_through(self):
        """A missing percent field stays ``None``."""
        d = FederalReserveOvernightBankFundingRateData.model_validate(
            _ref_rate(percentPercentile1=None)
        )
        assert d.percentile_1 is None

    def test_validate_revision_indicator_blanks_to_none(self):
        """Empty-string revision indicators normalize to ``None``."""
        d = FederalReserveOvernightBankFundingRateData.model_validate(
            _ref_rate(revisionIndicator="")
        )
        assert d.revision_indicator is None

    def test_validate_revision_indicator_keeps_value(self):
        """A real revision indicator is preserved."""
        d = FederalReserveOvernightBankFundingRateData.model_validate(
            _ref_rate(revisionIndicator="R")
        )
        assert d.revision_indicator == "R"


class TestFederalReserveOvernightBankFundingRateFetcher:
    """Tests for the OBFR fetcher methods."""

    def test_transform_query_defaults_dates(self):
        """Missing dates default to the 2016-03-01 anchor and today."""
        q = FederalReserveOvernightBankFundingRateFetcher.transform_query({})
        assert isinstance(q, FederalReserveOvernightBankFundingRateQueryParams)
        assert q.start_date == datetime(2016, 3, 1).date()
        assert q.end_date == datetime.now().date()

    def test_transform_query_respects_provided_dates(self):
        """Explicit start/end dates are passed through unchanged."""
        q = FederalReserveOvernightBankFundingRateFetcher.transform_query(
            {"start_date": dateType(2024, 6, 1), "end_date": dateType(2024, 6, 6)}
        )
        assert q.start_date == dateType(2024, 6, 1)
        assert q.end_date == dateType(2024, 6, 6)

    @pytest.mark.asyncio
    async def test_aextract_data_returns_ref_rates(self, monkeypatch):
        """A populated ``refRates`` list is returned and the URL is correct."""
        mock = AsyncMock(return_value={"refRates": [_ref_rate(), _ref_rate()]})
        monkeypatch.setattr("openbb_core.provider.utils.helpers.amake_request", mock)
        q = FederalReserveOvernightBankFundingRateQueryParams(
            start_date=dateType(2024, 6, 1), end_date=dateType(2024, 6, 6)
        )
        out = await FederalReserveOvernightBankFundingRateFetcher.aextract_data(q, None)
        assert len(out) == 2
        assert out[0]["type"] == "OBFR"
        assert "obfr/search.json" in mock.await_args.args[0]
        assert "startDate=2024-06-01" in mock.await_args.args[0]
        assert "endDate=2024-06-06" in mock.await_args.args[0]

    @pytest.mark.asyncio
    async def test_aextract_data_empty_ref_rates_raises(self, monkeypatch):
        """An empty ``refRates`` list raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request",
            AsyncMock(return_value={"refRates": []}),
        )
        q = FederalReserveOvernightBankFundingRateQueryParams()
        with pytest.raises(EmptyDataError):
            await FederalReserveOvernightBankFundingRateFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_aextract_data_missing_ref_rates_raises(self, monkeypatch):
        """A response without ``refRates`` raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request",
            AsyncMock(return_value={}),
        )
        q = FederalReserveOvernightBankFundingRateQueryParams()
        with pytest.raises(EmptyDataError):
            await FederalReserveOvernightBankFundingRateFetcher.aextract_data(q, None)

    def test_transform_data_sorts_and_strips_helper_keys(self):
        """``type`` / ``footnoteId`` / ``revisionIndicator`` drop; rows sort ascending."""
        q = FederalReserveOvernightBankFundingRateQueryParams()
        rows = [
            _ref_rate(effectiveDate="2024-06-06", footnoteId="1"),
            _ref_rate(effectiveDate="2024-06-03"),
        ]
        out = FederalReserveOvernightBankFundingRateFetcher.transform_data(q, rows)
        assert [d.date for d in out] == [
            dateType(2024, 6, 3),
            dateType(2024, 6, 6),
        ]
        assert all(
            isinstance(d, FederalReserveOvernightBankFundingRateData) for d in out
        )
        assert out[0].rate == pytest.approx(0.0532)
