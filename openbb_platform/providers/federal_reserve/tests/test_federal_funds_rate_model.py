"""Unit tests for the Federal Reserve Federal Funds Rate fetcher."""

# ruff: noqa: I001

from datetime import date as dateType, datetime
from unittest.mock import AsyncMock

import pytest

from openbb_core.provider.utils.errors import EmptyDataError
from openbb_federal_reserve.models.federal_funds_rate import (
    FederalReserveFederalFundsRateData,
    FederalReserveFederalFundsRateFetcher,
    FederalReserveFederalFundsRateQueryParams,
)


def _ref_rate(**overrides) -> dict:
    """Return a single EFFR ``refRates`` row as the NY Fed API emits it."""
    row = {
        "effectiveDate": "2023-06-06",
        "type": "EFFR",
        "percentRate": 5.08,
        "percentPercentile1": 5.05,
        "percentPercentile25": 5.06,
        "percentPercentile75": 5.08,
        "percentPercentile99": 5.3,
        "targetRateFrom": 5.0,
        "targetRateTo": 5.25,
        "volumeInBillions": 144,
        "revisionIndicator": "",
    }
    row.update(overrides)
    return row


class TestFederalReserveFederalFundsRateData:
    """Tests for the Federal Funds Rate data model and validators."""

    def test_normalize_percent_divides_by_100(self):
        """Non-zero, non-null rate values are divided by 100."""
        d = FederalReserveFederalFundsRateData.model_validate(_ref_rate())
        assert d.rate == pytest.approx(0.0508)
        assert d.target_range_upper == pytest.approx(0.0525)
        assert d.target_range_lower == pytest.approx(0.05)
        assert d.percentile_1 == pytest.approx(0.0505)

    def test_normalize_percent_zero_stays_zero(self):
        """A zero rate is preserved as zero, not divided."""
        d = FederalReserveFederalFundsRateData.model_validate(_ref_rate(percentRate=0))
        assert d.rate == 0

    def test_normalize_percent_none_passes_through(self):
        """A missing percent field stays ``None``."""
        d = FederalReserveFederalFundsRateData.model_validate(
            _ref_rate(percentPercentile1=None)
        )
        assert d.percentile_1 is None

    def test_validate_revision_indicator_blanks_to_none(self):
        """Empty-string revision indicators normalize to ``None``."""
        d = FederalReserveFederalFundsRateData.model_validate(
            _ref_rate(revisionIndicator="")
        )
        assert d.revision_indicator is None

    def test_validate_revision_indicator_keeps_value(self):
        """A real revision indicator is preserved."""
        d = FederalReserveFederalFundsRateData.model_validate(
            _ref_rate(revisionIndicator="R")
        )
        assert d.revision_indicator == "R"


class TestFederalReserveFederalFundsRateFetcher:
    """Tests for the Federal Funds Rate fetcher methods."""

    def test_transform_query_defaults_dates(self):
        """Missing dates default to the 2016-03-01 anchor and today."""
        q = FederalReserveFederalFundsRateFetcher.transform_query({})
        assert isinstance(q, FederalReserveFederalFundsRateQueryParams)
        assert q.start_date == datetime(2016, 3, 1).date()
        assert q.end_date == datetime.now().date()

    def test_transform_query_respects_provided_dates(self):
        """Explicit start/end dates are passed through unchanged."""
        q = FederalReserveFederalFundsRateFetcher.transform_query(
            {"start_date": dateType(2023, 1, 1), "end_date": dateType(2023, 6, 6)}
        )
        assert q.start_date == dateType(2023, 1, 1)
        assert q.end_date == dateType(2023, 6, 6)

    @pytest.mark.asyncio
    async def test_aextract_data_returns_ref_rates(self, monkeypatch):
        """A populated ``refRates`` list is returned verbatim."""
        mock = AsyncMock(return_value={"refRates": [_ref_rate(), _ref_rate()]})
        monkeypatch.setattr("openbb_core.provider.utils.helpers.amake_request", mock)
        q = FederalReserveFederalFundsRateQueryParams(
            start_date=dateType(2023, 1, 1), end_date=dateType(2023, 6, 6)
        )
        out = await FederalReserveFederalFundsRateFetcher.aextract_data(q, None)
        assert len(out) == 2
        assert out[0]["type"] == "EFFR"
        assert "effr/search.json" in mock.await_args.args[0]
        assert "startDate=2023-01-01" in mock.await_args.args[0]
        assert "endDate=2023-06-06" in mock.await_args.args[0]

    @pytest.mark.asyncio
    async def test_aextract_data_empty_ref_rates_raises(self, monkeypatch):
        """An empty ``refRates`` list raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request",
            AsyncMock(return_value={"refRates": []}),
        )
        q = FederalReserveFederalFundsRateQueryParams()
        with pytest.raises(EmptyDataError):
            await FederalReserveFederalFundsRateFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_aextract_data_missing_ref_rates_raises(self, monkeypatch):
        """A response without ``refRates`` raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request",
            AsyncMock(return_value={}),
        )
        q = FederalReserveFederalFundsRateQueryParams()
        with pytest.raises(EmptyDataError):
            await FederalReserveFederalFundsRateFetcher.aextract_data(q, None)

    def test_transform_data_sorts_and_strips_helper_keys(self):
        """``type`` / ``footnoteId`` are dropped and rows sort by date ascending."""
        q = FederalReserveFederalFundsRateQueryParams()
        rows = [
            _ref_rate(effectiveDate="2023-06-06", footnoteId="1"),
            _ref_rate(effectiveDate="2023-01-03"),
        ]
        out = FederalReserveFederalFundsRateFetcher.transform_data(q, rows)
        assert [d.date for d in out] == [
            dateType(2023, 1, 3),
            dateType(2023, 6, 6),
        ]
        assert all(isinstance(d, FederalReserveFederalFundsRateData) for d in out)
        assert out[0].rate == pytest.approx(0.0508)
