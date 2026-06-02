"""Tests for ``openbb_bls.utils.jolts_catalog``."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

import openbb_bls.utils.jolts_catalog as jolts_cat

_FIXTURES = Path(__file__).parent / "fixtures"


class _FakeResponse:
    """Minimal ``requests.Response`` stand-in for HTML pages."""

    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self) -> None:
        """No-op for fixture responses."""


def _make_router(url_to_fixture: dict[str, str], status: int = 200):
    """Build a fake ``requests.get`` routing each URL to a fixture file."""

    def _get(url: str, *args, **kwargs) -> _FakeResponse:
        if url not in url_to_fixture:
            raise AssertionError(f"unexpected URL: {url}")
        body = (_FIXTURES / url_to_fixture[url]).read_bytes()
        return _FakeResponse(body, status_code=status)

    return _get


def _make_status_get(status: int):
    """Build a fake ``requests.get`` that always returns a non-200 status."""

    def _get(url: str, *args, **kwargs) -> _FakeResponse:
        return _FakeResponse(b"<html></html>", status_code=status)

    return _get


@pytest.fixture(autouse=True)
def _clear_jolts_caches():
    """Drop every lru_cache in ``jolts_catalog`` between tests."""
    jolts_cat.scrape_supplemental_files.cache_clear()
    jolts_cat._scrape_archive_page.cache_clear()
    jolts_cat.scrape_archived_supplemental_index.cache_clear()
    jolts_cat.scrape_archive.cache_clear()
    yield
    jolts_cat.scrape_supplemental_files.cache_clear()
    jolts_cat._scrape_archive_page.cache_clear()
    jolts_cat.scrape_archived_supplemental_index.cache_clear()
    jolts_cat.scrape_archive.cache_clear()


def test_list_releases_returns_jolts_and_jltst():
    """``list_releases`` exposes the two hardcoded current releases."""
    rows = jolts_cat.list_releases()
    codes = [r["code"] for r in rows]
    assert codes == ["jolts", "jltst"]
    for row in rows:
        assert row["news_release_url"].startswith("https://www.bls.gov/")
        assert row["archive_index_url"].startswith("https://www.bls.gov/")


def test_decode_html_utf8_path():
    """``_decode_html`` returns UTF-8 text when bytes decode cleanly."""
    assert jolts_cat._decode_html(b"plain ascii") == "plain ascii"


def test_decode_html_latin1_fallback():
    """``_decode_html`` falls back to latin-1 on UTF-8 decode errors."""
    payload = "café".encode("latin-1")
    decoded = jolts_cat._decode_html(payload)
    assert "caf" in decoded


@pytest.mark.parametrize(
    "href,expected",
    [
        ("https://example.com/x.htm", "https://example.com/x.htm"),
        ("/news.release/x.htm", "https://www.bls.gov/news.release/x.htm"),
        ("news.release/x.htm", "https://www.bls.gov/news.release/x.htm"),
    ],
)
def test_abs_promotes_relative_hrefs(href, expected):
    """``_abs`` normalises absolute, root-relative and bare-relative hrefs."""
    assert jolts_cat._abs(href) == expected


@pytest.mark.parametrize(
    "base,href,expected",
    [
        (
            "https://www.bls.gov/web",
            "https://other/x.xlsx",
            "https://other/x.xlsx",
        ),
        (
            "https://www.bls.gov/web",
            "/web/jolts/x.xlsx",
            "https://www.bls.gov/web/jolts/x.xlsx",
        ),
        (
            "https://www.bls.gov/web",
            "../web/jolts/x.xlsx",
            "https://www.bls.gov/web/jolts/x.xlsx",
        ),
        (
            "https://www.bls.gov/web",
            "./sub/x.xlsx",
            "https://www.bls.gov/web/sub/x.xlsx",
        ),
        ("", "../x.xlsx", "x.xlsx"),
    ],
)
def test_resolve_relative_variants(base, href, expected):
    """``_resolve_relative`` covers absolute, rooted, ``..``, ``.`` and empty-base cases."""
    assert jolts_cat._resolve_relative(base, href) == expected


def test_scrape_supplemental_files_parses_every_extension(monkeypatch):
    """Supplemental TOC scraping picks up xlsx, pdf, txt, csv with dedup + labels."""
    import requests

    toc_url = "https://www.bls.gov/web/jolts.supp.toc.htm"
    monkeypatch.setattr(
        requests,
        "get",
        _make_router({toc_url: "jolts_supp_toc.html"}),
    )
    rows = jolts_cat.scrape_supplemental_files(toc_url)
    by_url = {r["url"]: r for r in rows}

    openings = by_url["https://www.bls.gov/web/jolts/jt_openings_indu.xlsx"]
    assert openings["format"] == "xlsx"
    assert "Job Openings" in openings["name"]

    openings_pdf = by_url["https://www.bls.gov/web/jolts/jt_openings_indu.pdf"]
    assert openings_pdf["format"] == "pdf"

    hires = by_url["https://www.bls.gov/web/jolts/jt_hires_region.xlsx"]
    assert hires["name"] == "Hires by Region"

    separations = by_url["https://www.bls.gov/web/jolts/jt_separations.txt"]
    assert separations["format"] == "txt"
    assert separations["name"] == "Separations data file"

    quits = by_url["https://www.bls.gov/web/jolts/jt_quits_extra.csv"]
    assert quits["format"] == "csv"
    assert quits["name"] == "Quits Extra"

    layoffs = by_url["https://www.bls.gov/web/jolts/jt_layoffs.xlsx"]
    assert layoffs["name"] == "Standalone paragraph link"

    label_only = by_url["https://www.bls.gov/web/jolts/jt_only_label.pdf"]
    assert label_only["name"] == "Jt Only Label"

    urls = [r["url"] for r in rows]
    assert len(urls) == len(set(urls))


def test_scrape_supplemental_files_non_200_returns_empty(monkeypatch):
    """Non-200 responses short-circuit to an empty tuple."""
    import requests

    monkeypatch.setattr(requests, "get", _make_status_get(404))
    assert jolts_cat.scrape_supplemental_files("https://x") == ()


def test_scrape_archive_jolts_dedupes_by_date(monkeypatch):
    """Per-code dedup-by-date merges htm + pdf releases and drops malformed dates."""
    import requests

    archive_url = "https://www.bls.gov/bls/news-release/jolts.htm"
    monkeypatch.setattr(
        requests,
        "get",
        _make_router({archive_url: "jolts_archive_jolts.html"}),
    )

    rows = jolts_cat.scrape_archive("JOLTS")

    dates = [r["date"] for r in rows]
    assert dates == sorted(dates, reverse=True)
    assert date(2026, 5, 5) in dates
    assert date(2026, 4, 2) in dates
    assert date(2024, 3, 13) in dates
    assert date(2026, 2, 13) in dates

    by_date = {r["date"]: r for r in rows}
    top = by_date[date(2026, 5, 5)]
    assert top["title"] == "March 2026 Job Openings and Labor Turnover"
    assert top["html_url"] == (
        "https://www.bls.gov/news.release/archives/jolts_05052026.htm"
    )
    assert top["pdf_url"] == (
        "https://www.bls.gov/news.release/archives/jolts_05052026.pdf"
    )

    legacy = by_date[date(2024, 3, 13)]
    assert legacy["html_url"].endswith("jolts_03132024.htm")
    assert legacy["pdf_url"].endswith("jolts_03132024.pdf")
    assert legacy["title"] == "January 2024 Job Openings and Labor Turnover"

    bare = by_date[date(2026, 2, 13)]
    assert bare["pdf_url"].endswith("jolts_02132026.pdf")
    assert bare["html_url"] is None

    for row in rows:
        assert row["code"] == "jolts"


def test_scrape_archive_unknown_code_returns_empty():
    """Unknown release codes yield an empty tuple without HTTP."""
    assert jolts_cat.scrape_archive("not-a-code") == ()


def test_scrape_archive_page_non_200(monkeypatch):
    """Non-200 responses on the archive page produce an empty tuple."""
    import requests

    monkeypatch.setattr(requests, "get", _make_status_get(500))
    assert jolts_cat.scrape_archive("jolts") == ()


def test_scrape_archived_supplemental_index_jolts(monkeypatch):
    """Archived supp-index scraper dedupes, drops bogus months and falls back on labels."""
    import requests

    index_url = "https://www.bls.gov/jlt/jolts-archived-supplemental.htm"
    monkeypatch.setattr(
        requests,
        "get",
        _make_router({index_url: "jolts_archived_supp_index.html"}),
    )
    rows = jolts_cat.scrape_archived_supplemental_index("JOLTS")

    dates = [r["date"] for r in rows]
    assert dates == sorted(dates, reverse=True)

    by_date = {r["date"]: r for r in rows}
    assert date(2026, 3, 1) in by_date
    assert date(2026, 2, 1) in by_date
    assert date(2026, 1, 1) in by_date
    assert date(2025, 9, 1) in by_date

    fallback = by_date[date(2025, 9, 1)]
    assert fallback["month_label"] == "Sept 2025"

    march = by_date[date(2026, 3, 1)]
    assert march["month_label"] == "March 2026 supplemental files"
    assert march["toc_url"] == ("https://www.bls.gov/jlt/jolts-mar2026-supp-toc.htm")

    for row in rows:
        assert row["code"] == "jolts"

    toc_urls = [r["toc_url"] for r in rows]
    assert len(toc_urls) == len(set(toc_urls))


def test_scrape_archived_supplemental_index_unknown_code():
    """Unknown codes bypass HTTP and return an empty tuple."""
    assert jolts_cat.scrape_archived_supplemental_index("other") == ()


def test_scrape_archived_supplemental_index_non_200(monkeypatch):
    """Non-200 responses on the archived supp-index page yield an empty tuple."""
    import requests

    monkeypatch.setattr(requests, "get", _make_status_get(503))
    assert jolts_cat.scrape_archived_supplemental_index("jltst") == ()
