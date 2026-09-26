"""Internal-branch tests for ``openbb_bls.models.jolts_documents``."""

from __future__ import annotations

from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_bls.models.jolts_documents as jd_mod

_CATALOG = [
    {
        "code": "jolts",
        "category": "national",
        "title": "JOLTS National",
        "pdf_url": "https://www.bls.gov/news.release/pdf/jolts.pdf",
    },
    {
        "code": "jltst",
        "category": "state",
        "title": "JOLTS State",
        "pdf_url": "https://www.bls.gov/news.release/pdf/jltst.pdf",
    },
]


def _archive_with_none_date(code):
    """Return one archive row whose date is None plus one with a real date."""
    return (
        {"date": None, "title": None, "pdf_url": None},
        {
            "date": date(2026, 1, 1),
            "title": "January 2026",
            "pdf_url": f"https://www.bls.gov/news.release/archives/{code}_01012026.pdf",
        },
    )


def _patch(monkeypatch, *, catalog=None, archive_fn=None):
    """Patch the model-side bindings for catalog + archive lookups."""
    monkeypatch.setattr(jd_mod, "list_releases", lambda: catalog or _CATALOG)
    monkeypatch.setattr(
        jd_mod,
        "scrape_archive",
        archive_fn if archive_fn is not None else _archive_with_none_date,
    )


def test_extract_skips_archived_rows_with_none_date(monkeypatch):
    """A ``date is None`` archive row is excluded from ``latest_dates``."""
    _patch(monkeypatch)
    query = jd_mod.BlsJoltsDocumentsQueryParams(category="all")
    rows = jd_mod.BlsJoltsDocumentsFetcher.extract_data(query, None)
    titles = [r["name"] for r in rows]
    assert "JOLTS National" in titles
    assert "JOLTS State" in titles


def test_extract_filters_current_releases_by_category(monkeypatch):
    """``category='national'`` drops the state release from the current set."""
    _patch(monkeypatch)
    query = jd_mod.BlsJoltsDocumentsQueryParams(category="national")
    rows = jd_mod.BlsJoltsDocumentsFetcher.extract_data(query, None)
    assert all(r["release_code"] == "jolts" for r in rows)


def test_extract_filters_archived_by_date_range(monkeypatch):
    """``start_date`` and ``end_date`` clip the archived rows."""

    def _archive(code):
        return (
            {"date": date(2024, 1, 1), "title": "Old", "pdf_url": "https://x/a.pdf"},
            {"date": date(2026, 1, 1), "title": "Mid", "pdf_url": "https://x/b.pdf"},
            {"date": date(2028, 1, 1), "title": "New", "pdf_url": "https://x/c.pdf"},
        )

    _patch(monkeypatch, archive_fn=_archive)
    query = jd_mod.BlsJoltsDocumentsQueryParams(
        category="archived",
        start_date=date(2025, 1, 1),
        end_date=date(2027, 1, 1),
    )
    rows = jd_mod.BlsJoltsDocumentsFetcher.extract_data(query, None)
    assert {r["name"] for r in rows} == {"Mid"}


def test_extract_skips_archived_rows_without_pdf_url(monkeypatch):
    """Archive entries whose ``pdf_url`` is ``None`` are dropped."""

    def _archive(code):
        return (
            {"date": date(2026, 1, 1), "title": None, "pdf_url": None},
            {
                "date": date(2026, 2, 1),
                "title": "Has PDF",
                "pdf_url": "https://x/p.pdf",
            },
        )

    _patch(monkeypatch, archive_fn=_archive)
    query = jd_mod.BlsJoltsDocumentsQueryParams(category="archived")
    rows = jd_mod.BlsJoltsDocumentsFetcher.extract_data(query, None)
    assert all(r["url"] == "https://x/p.pdf" for r in rows)


def test_extract_falls_back_to_synthetic_title(monkeypatch):
    """A None ``title`` falls back to ``f'{code} — {date}'``."""

    def _archive(code):
        return (
            {"date": date(2026, 3, 1), "title": None, "pdf_url": "https://x/p.pdf"},
        )

    _patch(monkeypatch, catalog=[_CATALOG[0]], archive_fn=_archive)
    query = jd_mod.BlsJoltsDocumentsQueryParams(category="archived")
    rows = jd_mod.BlsJoltsDocumentsFetcher.extract_data(query, None)
    assert any("jolts — 2026-03-01" in r["name"] for r in rows)


def test_transform_data_raises_when_empty():
    """``transform_data`` raises ``EmptyDataError`` for no documents."""
    query = jd_mod.BlsJoltsDocumentsQueryParams(category="all")
    with pytest.raises(EmptyDataError):
        jd_mod.BlsJoltsDocumentsFetcher.transform_data(query, [])
