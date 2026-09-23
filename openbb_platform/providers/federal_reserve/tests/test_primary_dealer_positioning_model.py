"""Unit tests for the Federal Reserve Primary Dealer Positioning model."""

# ruff: noqa: I001

from datetime import date as dateType
from unittest.mock import AsyncMock

import pytest

from openbb_core.provider.utils.errors import EmptyDataError
from openbb_federal_reserve.models.primary_dealer_positioning import (
    FederalReservePrimaryDealerPositioningData,
    FederalReservePrimaryDealerPositioningFetcher,
    FederalReservePrimaryDealerPositioningQueryParams,
)


def _rows(keyid: str, dates_values) -> list[dict]:
    """Return raw timeseries rows for a single keyid."""
    return [
        {"asofdate": asofdate, "keyid": keyid, "value": value}
        for asofdate, value in dates_values
    ]


class TestQueryParams:
    """Tests for ``FederalReservePrimaryDealerPositioningQueryParams``."""

    def test_default_category(self):
        """The default category is ``treasuries``."""
        q = FederalReservePrimaryDealerPositioningQueryParams()
        assert q.category == "treasuries"

    def test_transform_query(self):
        """``transform_query`` builds the params model from a dict."""
        q = FederalReservePrimaryDealerPositioningFetcher.transform_query(
            {"category": "cmbs"}
        )
        assert isinstance(q, FederalReservePrimaryDealerPositioningQueryParams)
        assert q.category == "cmbs"


class TestExtractData:
    """Tests for ``FederalReservePrimaryDealerPositioningFetcher.aextract_data``."""

    @pytest.mark.asyncio
    async def test_aggregates_series_for_category(self, monkeypatch):
        """Each series URL for the category is fetched and the rows are aggregated."""
        from openbb_core.provider.utils import helpers

        responses = {
            "PDPOSMBSFGS-C": {
                "pd": {"timeseries": _rows("PDPOSMBSFGS-C", [("2024-06-04", "10")])}
            },
            "PDPOSMBSNA-O": {
                "pd": {"timeseries": _rows("PDPOSMBSNA-O", [("2024-06-04", "20")])}
            },
        }

        async def _fake(url, *args, **kwargs):
            """Return the canned response keyed off the symbol in the URL."""
            for symbol, payload in responses.items():
                if f"/{symbol}.json" in url:
                    return payload
            return {"pd": {"timeseries": []}}

        monkeypatch.setattr(helpers, "amake_request", _fake)
        q = FederalReservePrimaryDealerPositioningQueryParams(category="cmbs")
        data = await FederalReservePrimaryDealerPositioningFetcher.aextract_data(
            q, None
        )
        assert len(data) == 2
        assert {r["keyid"] for r in data} == {"PDPOSMBSFGS-C", "PDPOSMBSNA-O"}

    @pytest.mark.asyncio
    async def test_non_dict_result_is_skipped(self, monkeypatch):
        """A non-dict response contributes no rows and raises when nothing remains."""
        from openbb_core.provider.utils import helpers

        monkeypatch.setattr(helpers, "amake_request", AsyncMock(return_value=None))
        q = FederalReservePrimaryDealerPositioningQueryParams(category="bills")
        with pytest.raises(EmptyDataError, match="returned empty"):
            await FederalReservePrimaryDealerPositioningFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_empty_timeseries_raises(self, monkeypatch):
        """An empty timeseries for every URL raises ``EmptyDataError``."""
        from openbb_core.provider.utils import helpers

        monkeypatch.setattr(
            helpers,
            "amake_request",
            AsyncMock(return_value={"pd": {"timeseries": []}}),
        )
        q = FederalReservePrimaryDealerPositioningQueryParams(category="bills")
        with pytest.raises(EmptyDataError, match="returned empty"):
            await FederalReservePrimaryDealerPositioningFetcher.aextract_data(q, None)


class TestTransformData:
    """Tests for ``FederalReservePrimaryDealerPositioningFetcher.transform_data``."""

    def test_pivots_series_to_wide_columns(self):
        """Each series name becomes a wide column keyed by date."""
        data = _rows("PDPOSGS-B", [("2024-06-04", "100"), ("2024-06-11", "200")])
        q = FederalReservePrimaryDealerPositioningQueryParams(category="bills")
        out = FederalReservePrimaryDealerPositioningFetcher.transform_data(q, data)
        assert len(out) == 2
        assert all(
            isinstance(r, FederalReservePrimaryDealerPositioningData) for r in out
        )
        first = out[0]
        assert first.date == dateType(2024, 6, 4)
        assert first.model_dump()["bills"] == 100

    def test_sorted_ascending_by_date(self):
        """Output rows are sorted ascending by date."""
        data = _rows("PDPOSGS-B", [("2024-06-11", "200"), ("2024-06-04", "100")])
        q = FederalReservePrimaryDealerPositioningQueryParams(category="bills")
        out = FederalReservePrimaryDealerPositioningFetcher.transform_data(q, data)
        assert [r.date for r in out] == [
            dateType(2024, 6, 4),
            dateType(2024, 6, 11),
        ]

    def test_start_and_end_date_filter(self):
        """``start_date`` and ``end_date`` bound the returned rows inclusively."""
        data = _rows(
            "PDPOSGS-B",
            [("2024-06-04", "100"), ("2024-06-11", "200"), ("2024-06-18", "300")],
        )
        q = FederalReservePrimaryDealerPositioningQueryParams(
            category="bills",
            start_date=dateType(2024, 6, 11),
            end_date=dateType(2024, 6, 11),
        )
        out = FederalReservePrimaryDealerPositioningFetcher.transform_data(q, data)
        assert [r.date for r in out] == [dateType(2024, 6, 11)]
