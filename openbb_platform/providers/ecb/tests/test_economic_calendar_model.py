"""Unit tests for the ECB economic (release) calendar model."""

import asyncio
from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_ecb.models.economic_calendar import (
    ECBEconomicCalendarFetcher as Fetcher,
)
from openbb_ecb.utils import non_sdmx

_ROWS = [
    {
        "date": "2026-06-24T10:00:00",
        "country": "Euro Area",
        "category": "BSI",
        "event": "Monetary developments",
        "source": "European Central Bank",
    },
    {
        "date": "2026-07-01T10:00:00",
        "country": "Euro Area",
        "category": "HICP",
        "event": "HICP flash",
        "source": "European Central Bank",
    },
]


def _patch(monkeypatch):
    async def _cal():
        return list(_ROWS)

    monkeypatch.setattr(non_sdmx, "fetch_release_calendar", _cal)


def test_aextract_returns_raw(monkeypatch):
    """Extract returns the unfiltered scraped rows."""
    _patch(monkeypatch)
    raw = asyncio.run(Fetcher.aextract_data(Fetcher.transform_query({}), None))
    assert len(raw) == 2


def test_transform_filters_and_sorts(monkeypatch):
    """Transform filters by date range and sorts."""
    query = Fetcher.transform_query(
        {"start_date": date(2026, 6, 1), "end_date": date(2026, 6, 30)}
    )
    out = Fetcher.transform_data(query, list(_ROWS))
    assert [r.category for r in out] == ["BSI"]


def test_transform_empty_raises():
    """An empty filtered set raises."""
    query = Fetcher.transform_query({"start_date": date(2030, 1, 1)})
    with pytest.raises(EmptyDataError):
        Fetcher.transform_data(query, list(_ROWS))


def test_transform_aliases_dataflow_codes():
    """Statscal domain abbreviations are canonicalized to the SDMX dataflow id."""
    rows = [
        {
            "date": "2026-06-10T10:00:00",
            "country": "Euro Area",
            "category": "BPS",  # balance of payments -> BOP
            "event": "Euro area quarterly balance of payments",
            "source": "European Central Bank",
        },
        {
            "date": "2026-06-11T10:00:00",
            "country": "Euro Area",
            "category": "BSI",  # already a dataflow -> unchanged
            "event": "Monetary developments",
            "source": "European Central Bank",
        },
    ]
    out = Fetcher.transform_data(Fetcher.transform_query({}), rows)
    assert {r.category for r in out} == {"BOP", "BSI"}
