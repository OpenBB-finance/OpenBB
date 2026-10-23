"""Unit tests for the Federal Reserve SOFR fetcher."""

# ruff: noqa: I001

from datetime import date as dateType, datetime
from unittest.mock import AsyncMock

import pytest

from openbb_core.provider.utils.errors import EmptyDataError
from openbb_federal_reserve.models.sofr import (
    FederalReserveSOFRData,
    FederalReserveSOFRFetcher,
    FederalReserveSOFRQueryParams,
)


def _ref_rate(**overrides) -> dict:
    """Return a single SOFR ``refRates`` row as the NY Fed API emits it."""
    row = {
        "effectiveDate": "2024-06-06",
        "type": "SOFR",
        "percentRate": 5.33,
        "percentPercentile1": 5.29,
        "percentPercentile25": 5.32,
        "percentPercentile75": 5.4,
        "percentPercentile99": 5.44,
        "volumeInBillions": 2008,
        "revisionIndicator": "",
    }
    row.update(overrides)
    return row


class TestFederalReserveSOFRData:
    """Tests for the SOFR data model and percent validator."""

    def test_normalize_percent_divides_by_100(self):
        """A real numeric rate is cast to float and divided by 100."""
        d = FederalReserveSOFRData.model_validate(_ref_rate())
        assert d.rate == pytest.approx(0.0533)
        assert d.percentile_1 == pytest.approx(0.0529)
        assert d.percentile_99 == pytest.approx(0.0544)

    def test_normalize_percent_string_value_casts(self):
        """A numeric string rate is parsed via ``float`` before scaling."""
        d = FederalReserveSOFRData.model_validate(_ref_rate(percentRate="5.33"))
        assert d.rate == pytest.approx(0.0533)

    def test_normalize_percent_zero_stays_zero(self):
        """A zero rate is preserved as zero, not divided."""
        d = FederalReserveSOFRData.model_validate(_ref_rate(percentRate=0))
        assert d.rate == 0

    @pytest.mark.parametrize("sentinel", [None, "", "''", "NA"])
    def test_normalize_percent_sentinels_become_none(self, sentinel):
        """Null-like sentinels normalize to ``None``."""
        d = FederalReserveSOFRData.model_validate(
            _ref_rate(percentPercentile1=sentinel)
        )
        assert d.percentile_1 is None


class TestFederalReserveSOFRFetcher:
    """Tests for the SOFR fetcher methods."""

    def test_transform_query_defaults_dates(self):
        """Missing dates default to the 2018-04-02 anchor and today."""
        q = FederalReserveSOFRFetcher.transform_query({})
        assert isinstance(q, FederalReserveSOFRQueryParams)
        assert q.start_date == datetime(2018, 4, 2).date()
        assert q.end_date == datetime.now().date()

    def test_transform_query_respects_provided_dates(self):
        """Explicit start/end dates are passed through unchanged."""
        q = FederalReserveSOFRFetcher.transform_query(
            {"start_date": dateType(2024, 6, 1), "end_date": dateType(2024, 6, 6)}
        )
        assert q.start_date == dateType(2024, 6, 1)
        assert q.end_date == dateType(2024, 6, 6)

    @pytest.mark.asyncio
    async def test_aextract_data_returns_ref_rates(self, monkeypatch):
        """A populated ``refRates`` list is returned and the URL is correct."""
        mock = AsyncMock(return_value={"refRates": [_ref_rate(), _ref_rate()]})
        monkeypatch.setattr("openbb_core.provider.utils.helpers.amake_request", mock)
        q = FederalReserveSOFRQueryParams(
            start_date=dateType(2024, 6, 1), end_date=dateType(2024, 6, 6)
        )
        out = await FederalReserveSOFRFetcher.aextract_data(q, None)
        assert len(out) == 2
        assert out[0]["type"] == "SOFR"
        assert "sofr/search.json" in mock.await_args.args[0]
        assert "startDate=2024-06-01" in mock.await_args.args[0]
        assert "endDate=2024-06-06" in mock.await_args.args[0]

    @pytest.mark.asyncio
    async def test_aextract_data_empty_ref_rates_raises(self, monkeypatch):
        """An empty ``refRates`` list raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request",
            AsyncMock(return_value={"refRates": []}),
        )
        q = FederalReserveSOFRQueryParams()
        with pytest.raises(EmptyDataError):
            await FederalReserveSOFRFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_aextract_data_missing_ref_rates_raises(self, monkeypatch):
        """A response without ``refRates`` raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request",
            AsyncMock(return_value={}),
        )
        q = FederalReserveSOFRQueryParams()
        with pytest.raises(EmptyDataError):
            await FederalReserveSOFRFetcher.aextract_data(q, None)

    def test_transform_data_sorts_and_strips_helper_keys(self):
        """``type`` / ``footnoteId`` / ``revisionIndicator`` drop; rows sort ascending."""
        q = FederalReserveSOFRQueryParams()
        rows = [
            _ref_rate(effectiveDate="2024-06-06", footnoteId="1"),
            _ref_rate(effectiveDate="2024-06-03"),
        ]
        out = FederalReserveSOFRFetcher.transform_data(q, rows)
        assert [d.date for d in out] == [
            dateType(2024, 6, 3),
            dateType(2024, 6, 6),
        ]
        assert all(isinstance(d, FederalReserveSOFRData) for d in out)
        assert out[0].rate == pytest.approx(0.0533)
