"""Unit tests for the ECB releases & documents model (Newsfeed)."""

import asyncio
from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_ecb.models.ecb_releases import ECBReleasesFetcher as Fetcher
from openbb_ecb.utils import non_sdmx

_SUMMARY = (
    "This is the article summary paragraph, and it is comfortably long enough"
    " to serve as the newsfeed excerpt."
)


def _patch(monkeypatch):
    async def _rss(feed):
        return [
            {
                "date": "2026-06-24T12:00:00",
                "title": "T1",
                "url": "http://a",
                "category": feed,
            },
            {
                "date": "2026-06-20T12:00:00",
                "title": "T2",
                "url": "http://b",
                "category": feed,
            },
            # null date AND no url -> exercises the missing-url / empty-body paths
            {"date": None, "title": "ND", "url": None, "category": feed},
        ]

    async def _body(url):
        # No url -> no body (the article can't be fetched).
        return f"* NAV\n# Title\n{_SUMMARY}" if url else ""

    monkeypatch.setattr(non_sdmx, "fetch_rss_items", _rss)
    monkeypatch.setattr(non_sdmx, "fetch_release_body", _body)


def test_single_feed_fetches_bodies(monkeypatch):
    """Bodies are fetched per item; null dates dropped; excerpt + author set."""
    _patch(monkeypatch)
    query = Fetcher.transform_query({"category": "press_releases"})
    raw = asyncio.run(Fetcher.aextract_data(query, None))
    assert len(raw) == 3 and all("body" in item for item in raw)

    out = Fetcher.transform_data(query, raw)
    assert [r.title for r in out] == ["T1", "T2"]  # newest first, null date dropped
    assert out[0].author == "European Central Bank"
    assert out[0].excerpt.startswith("This is the article summary")
    assert _SUMMARY in (out[0].body or "")


def test_all_feeds_limit_before_body(monkeypatch):
    """category='all' fetches every feed; the limit caps before body fetch."""
    _patch(monkeypatch)
    query = Fetcher.transform_query({"category": "all", "limit": 1})
    raw = asyncio.run(Fetcher.aextract_data(query, None))
    assert len(raw) == 1  # limit applied in aextract (before fetching bodies)
    assert len(Fetcher.transform_data(query, raw)) == 1


def test_transform_empty_raises(monkeypatch):
    """An empty filtered set raises."""
    _patch(monkeypatch)
    raw = asyncio.run(
        Fetcher.aextract_data(Fetcher.transform_query({"category": "blog"}), None)
    )
    query = Fetcher.transform_query({"start_date": date(2030, 1, 1)})
    with pytest.raises(EmptyDataError):
        Fetcher.transform_data(query, raw)
