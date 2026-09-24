"""Tests for the SEC Full-Text Search model."""

import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_sec.models.full_text_search import (
    SecFullTextSearchFetcher,
    SecFullTextSearchQueryParams,
)

_AMAKE = "openbb_core.provider.utils.helpers.amake_request"


def _hit(doc_id, ciks, adsh, display_names):
    """Build a single EFTS hit."""
    return {
        "_id": doc_id,
        "_source": {
            "file_date": "2024-01-15",
            "form": "8-K",
            "file_description": "desc",
            "ciks": ciks,
            "adsh": adsh,
            "display_names": display_names,
        },
    }


def test_transform_query():
    """transform_query returns the query params model."""
    query = SecFullTextSearchFetcher.transform_query({"query": "climate"})
    assert isinstance(query, SecFullTextSearchQueryParams)
    assert query.query == "climate"


def test_aextract_requires_a_criterion():
    """An empty query raises EmptyDataError before any request."""
    query = SecFullTextSearchFetcher.transform_query({})
    with pytest.raises(EmptyDataError):
        asyncio.run(SecFullTextSearchFetcher.aextract_data(query, None))


def test_aextract_paginates_to_total(monkeypatch):
    """aextract_data follows pagination and builds the full query string."""
    pages = [
        {
            "hits": {
                "hits": [_hit("a:1.htm", ["1"], "0-1", ["A (CIK 1)"])],
                "total": {"value": 2},
            }
        },
        {
            "hits": {
                "hits": [_hit("b:2.htm", ["2"], "0-2", ["B (CIK 2)"])],
                "total": {"value": 2},
            }
        },
    ]
    calls: list = []

    async def fake(url, **kwargs):
        calls.append(url)
        return pages[len(calls) - 1]

    monkeypatch.setattr(_AMAKE, fake, raising=False)
    query = SecFullTextSearchFetcher.transform_query(
        {
            "query": "climate",
            "entity": "AAPL",
            "category": "form-type",
            "form_type": "8-K",
            "location": "NY",
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 3, 1),
            "limit": 500,
        }
    )
    data = asyncio.run(SecFullTextSearchFetcher.aextract_data(query, None))
    assert len(data) == 2
    assert len(calls) == 2
    assert "dateRange=custom" in calls[0]
    assert "locationCodes=NY" in calls[0]


def test_aextract_stops_on_non_dict(monkeypatch):
    """A non-dict response stops pagination and yields nothing."""

    async def fake(url, **kwargs):
        return "throttled"

    monkeypatch.setattr(_AMAKE, fake, raising=False)
    query = SecFullTextSearchFetcher.transform_query({"query": "x"})
    assert asyncio.run(SecFullTextSearchFetcher.aextract_data(query, None)) == []


def test_aextract_stops_on_empty_hits(monkeypatch):
    """An empty hits page stops pagination."""

    async def fake(url, **kwargs):
        return {"hits": {"hits": [], "total": {"value": 0}}}

    monkeypatch.setattr(_AMAKE, fake, raising=False)
    query = SecFullTextSearchFetcher.transform_query({"entity": "AAPL"})
    assert asyncio.run(SecFullTextSearchFetcher.aextract_data(query, None)) == []


def test_aextract_request_error(monkeypatch):
    """A transport error is surfaced as an OpenBBError."""

    async def fake(url, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(_AMAKE, fake, raising=False)
    query = SecFullTextSearchFetcher.transform_query({"query": "x"})
    with pytest.raises(OpenBBError):
        asyncio.run(SecFullTextSearchFetcher.aextract_data(query, None))


def test_transform_data_parses_and_dedupes():
    """transform_data parses names/tickers, skips invalid hits, and dedupes."""
    query = SecFullTextSearchFetcher.transform_query({"query": "x"})
    data = [
        _hit(
            "0001-24:doc.htm",
            ["320193"],
            "0001-24",
            ["Apple Inc (AAPL) (CIK 0000320193)"],
        ),
        _hit(
            "0001-24:doc.htm",
            ["320193"],
            "0001-24",
            ["Apple Inc (AAPL) (CIK 0000320193)"],
        ),
        _hit("no-colon", ["320193"], "0001-24", ["X"]),
        {"_id": "0001-24:y.htm", "_source": {"ciks": [], "display_names": []}},
    ]
    results = SecFullTextSearchFetcher.transform_data(query, data)
    assert len(results) == 1
    row = results[0]
    assert row.symbol == "AAPL"
    assert row.name == "Apple Inc"
    assert "320193" in row.cik
    assert row.url.endswith("/000124/doc.htm")


def test_transform_data_empty():
    """No data raises EmptyDataError."""
    query = SecFullTextSearchFetcher.transform_query({"query": "x"})
    with pytest.raises(EmptyDataError):
        SecFullTextSearchFetcher.transform_data(query, [])


def test_form_type_json_array_string_is_joined():
    """A JSON-array string from the Workspace multi-select is comma-joined."""
    query = SecFullTextSearchFetcher.transform_query(
        {"query": "x", "form_type": '["S-1", "8-K"]'}
    )
    assert query.form_type == "S-1,8-K"


def test_form_type_invalid_json_array_returns_stripped():
    """A bracketed but non-JSON value falls back to its stripped self."""
    query = SecFullTextSearchFetcher.transform_query(
        {"query": "x", "form_type": "[S-1, 8-K]"}
    )
    assert query.form_type == "[S-1, 8-K]"


def test_form_type_list_is_joined():
    """A real list/tuple is comma-joined, dropping blank entries."""
    query = SecFullTextSearchFetcher.transform_query(
        {"query": "x", "form_type": ["S-1", " ", "8-K"]}
    )
    assert query.form_type == "S-1,8-K"
