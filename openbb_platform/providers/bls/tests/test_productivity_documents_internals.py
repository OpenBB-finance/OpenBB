"""Internal-branch tests for ``openbb_bls.models.productivity_documents``."""

from __future__ import annotations

from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_bls.models.productivity_documents as pd_mod

_CATALOG = [
    {
        "code": "prod2",
        "category": "labor_productivity",
        "title": "Productivity and Costs",
        "pdf_url": "https://www.bls.gov/news.release/pdf/prod2.pdf",
        "news_release_url": "https://x/prod2.nr0.htm",
        "toc_url": None,
        "supplemental_toc_url": None,
    },
    {
        "code": "prod3",
        "category": "total_factor_productivity",
        "title": "Total Factor Productivity",
        "pdf_url": "https://www.bls.gov/news.release/pdf/prod3.pdf",
        "news_release_url": "https://x/prod3.nr0.htm",
        "toc_url": None,
        "supplemental_toc_url": None,
    },
]


def _patch(monkeypatch, *, catalog=None, archive_fn=None):
    """Patch model-side catalog + archive lookups."""
    monkeypatch.setattr(pd_mod, "scrape_release_catalog", lambda: catalog or _CATALOG)
    monkeypatch.setattr(
        pd_mod,
        "scrape_archive",
        archive_fn if archive_fn is not None else (lambda _c: ()),
    )


def test_extract_skips_archive_rows_with_none_date(monkeypatch):
    """``latest_dates`` ignores archive rows whose ``date`` is None."""

    def _archive(code):
        return (
            {
                "date": None,
                "title": None,
                "pdf_url": None,
                "html_url": None,
            },
            {
                "date": date(2026, 1, 1),
                "title": "Jan 2026",
                "pdf_url": "https://x/a.pdf",
                "html_url": None,
            },
        )

    _patch(monkeypatch, archive_fn=_archive)
    query = pd_mod.BlsProductivityDocumentsQueryParams(category="all")
    rows = pd_mod.BlsProductivityDocumentsFetcher.extract_data(query, None)
    titles = [r["name"] for r in rows]
    assert "Productivity and Costs" in titles


def test_extract_filters_current_releases_by_category(monkeypatch):
    """``category='labor_productivity'`` excludes prod3."""
    _patch(monkeypatch)
    query = pd_mod.BlsProductivityDocumentsQueryParams(category="labor_productivity")
    rows = pd_mod.BlsProductivityDocumentsFetcher.extract_data(query, None)
    assert {r["release_code"] for r in rows} == {"prod2"}


def test_extract_filters_current_releases_by_release_code(monkeypatch):
    """``release_code`` narrows down the current set."""
    _patch(monkeypatch)
    query = pd_mod.BlsProductivityDocumentsQueryParams(
        category="all", release_code="prod3"
    )
    rows = pd_mod.BlsProductivityDocumentsFetcher.extract_data(query, None)
    assert all(r["release_code"] == "prod3" for r in rows)


def test_extract_filters_archived_by_date_range_and_skips_blank_urls(monkeypatch):
    """``start_date`` / ``end_date`` clip rows and rows lacking any URL are dropped."""

    def _archive(code):
        return (
            {
                "date": date(2024, 1, 1),
                "title": "Old",
                "pdf_url": "https://x/old.pdf",
                "html_url": None,
            },
            {
                "date": date(2026, 1, 1),
                "title": "Mid",
                "pdf_url": "https://x/mid.pdf",
                "html_url": None,
            },
            {
                "date": date(2028, 1, 1),
                "title": "New",
                "pdf_url": "https://x/new.pdf",
                "html_url": None,
            },
            {
                "date": date(2026, 6, 1),
                "title": "Blank",
                "pdf_url": None,
                "html_url": None,
            },
        )

    _patch(monkeypatch, archive_fn=_archive)
    query = pd_mod.BlsProductivityDocumentsQueryParams(
        category="archived",
        start_date=date(2025, 1, 1),
        end_date=date(2027, 1, 1),
    )
    rows = pd_mod.BlsProductivityDocumentsFetcher.extract_data(query, None)
    assert {r["name"] for r in rows} == {"Mid"}


def test_extract_uses_html_url_when_pdf_missing(monkeypatch):
    """When ``pdf_url`` is None and ``html_url`` is set, the latter is used."""

    def _archive(code):
        return (
            {
                "date": date(2026, 4, 1),
                "title": None,
                "pdf_url": None,
                "html_url": "https://x/p.htm",
            },
        )

    _patch(monkeypatch, catalog=[_CATALOG[0]], archive_fn=_archive)
    query = pd_mod.BlsProductivityDocumentsQueryParams(category="archived")
    rows = pd_mod.BlsProductivityDocumentsFetcher.extract_data(query, None)
    assert rows
    htm = [r for r in rows if r["format"] == "htm"]
    assert htm and htm[0]["url"] == "https://x/p.htm"
    assert htm[0]["name"].endswith("2026-04-01")


def test_transform_data_raises_when_empty():
    """``transform_data`` raises ``EmptyDataError`` for no documents."""
    query = pd_mod.BlsProductivityDocumentsQueryParams(category="all")
    with pytest.raises(EmptyDataError):
        pd_mod.BlsProductivityDocumentsFetcher.transform_data(query, [])
