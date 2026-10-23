"""Unit tests for ``openbb_bls.utils.productivity_catalog``."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

import openbb_bls.utils.productivity_catalog as catalog

_FIXTURES = Path(__file__).parent / "fixtures"


class _FakeResponse:
    """Minimal ``requests.Response`` stand-in for HTML pages."""

    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self) -> None:
        """No-op."""


def _read_fixture(name: str) -> bytes:
    """Return raw bytes of a bundled HTML fixture."""
    return (_FIXTURES / name).read_bytes()


def _make_router(routes: dict[str, bytes], default_status: int = 404):
    """Build a fake ``requests.get`` that dispatches by URL substring."""

    def _get(url: str, *args, **kwargs) -> _FakeResponse:
        for needle, payload in routes.items():
            if needle in url:
                return _FakeResponse(payload)
        return _FakeResponse(b"", status_code=default_status)

    return _get


@pytest.fixture(autouse=True)
def _clear_catalog_caches():
    """Reset every lru_cache in the catalog module between tests."""
    catalog.scrape_release_catalog.cache_clear()
    catalog.scrape_supplemental_files.cache_clear()
    catalog._scrape_archive_page.cache_clear()
    catalog.scrape_archive.cache_clear()
    yield
    catalog.scrape_release_catalog.cache_clear()
    catalog.scrape_supplemental_files.cache_clear()
    catalog._scrape_archive_page.cache_clear()
    catalog.scrape_archive.cache_clear()


def test_decode_html_utf8():
    """UTF-8 bytes round-trip cleanly through ``_decode_html``."""
    assert catalog._decode_html(b"hello") == "hello"


def test_decode_html_latin1_fallback():
    """Bytes that fail UTF-8 decode fall back to latin-1."""
    raw = "café".encode("latin-1")
    out = catalog._decode_html(raw)
    assert "caf" in out


def test_abs_with_absolute_url_passes_through():
    """``_abs`` returns http(s) URLs unchanged."""
    assert catalog._abs("https://example.com/x") == "https://example.com/x"


def test_abs_with_leading_slash_adds_host():
    """``_abs`` adds the BLS host to root-relative paths."""
    assert catalog._abs("/news.release/foo.htm") == (
        "https://www.bls.gov/news.release/foo.htm"
    )


def test_abs_with_bare_path_adds_host_and_slash():
    """``_abs`` adds host and slash to bare relative paths."""
    assert catalog._abs("foo.htm") == "https://www.bls.gov/foo.htm"


def test_resolve_relative_absolute_url_passthrough():
    """``_resolve_relative`` returns http(s) URLs unchanged."""
    assert (
        catalog._resolve_relative("https://www.bls.gov/web", "https://other/foo")
        == "https://other/foo"
    )


def test_resolve_relative_with_leading_slash():
    """``_resolve_relative`` rewrites root-relative paths to the BLS host."""
    assert (
        catalog._resolve_relative("https://www.bls.gov/web", "/x/y.xlsx")
        == "https://www.bls.gov/x/y.xlsx"
    )


def test_resolve_relative_dot_dot_and_dot_segments():
    """``_resolve_relative`` honours ``..`` and ``.`` path segments."""
    out = catalog._resolve_relative(
        "https://www.bls.gov/web", "../news.release/./archives/foo.pdf"
    )
    assert out == "https://www.bls.gov/news.release/archives/foo.pdf"


def test_resolve_relative_dot_dot_past_root_is_safe():
    """``..`` past an empty parts list is silently absorbed."""
    out = catalog._resolve_relative("", "../../foo")
    assert out == "foo"


def test_scrape_release_catalog_happy_path(monkeypatch):
    """``scrape_release_catalog`` extracts LP + TFP entries and tags prod2."""
    import requests

    monkeypatch.setattr(
        requests,
        "get",
        _make_router({"news-releases.htm": _read_fixture("prod_news_releases.html")}),
    )
    rows = catalog.scrape_release_catalog()
    by_code = {r["code"]: r for r in rows}

    assert "prod2" in by_code
    assert "prin" in by_code
    assert "prod3" in by_code
    assert "prod9" not in by_code

    prod2 = by_code["prod2"]
    assert prod2["category"] == "labor_productivity"
    assert prod2["title"] == "Productivity and Costs"
    assert prod2["news_release_url"] == "https://www.bls.gov/news.release/prod2.nr0.htm"
    assert prod2["pdf_url"] == "https://www.bls.gov/news.release/pdf/prod2.pdf"
    assert prod2["toc_url"] == "https://www.bls.gov/news.release/prod2.toc.htm"
    assert prod2["supplemental_toc_url"] == (
        "https://www.bls.gov/web/prod2.supp.toc.htm"
    )

    prin = by_code["prin"]
    assert prin["category"] == "labor_productivity"
    assert prin["pdf_url"] == "https://www.bls.gov/news.release/pdf/prin.pdf"
    assert prin["supplemental_toc_url"] is None

    prod3 = by_code["prod3"]
    assert prod3["category"] == "total_factor_productivity"
    assert prod3["pdf_url"] == "https://www.bls.gov/news.release/pdf/prod3.pdf"


def test_scrape_release_catalog_http_error(monkeypatch):
    """Non-200 responses are surfaced as ``OpenBBError``."""
    import requests
    from openbb_core.app.model.abstract.error import OpenBBError

    monkeypatch.setattr(
        requests,
        "get",
        lambda *a, **k: _FakeResponse(b"", status_code=503),
    )
    with pytest.raises(OpenBBError, match="HTTP 503"):
        catalog.scrape_release_catalog()


def test_scrape_release_catalog_missing_anchors(monkeypatch):
    """A page missing LP/TFP/SCH anchors raises ``OpenBBError``."""
    import requests
    from openbb_core.app.model.abstract.error import OpenBBError

    html = b"<html><body><p>nothing useful here</p></body></html>"
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(html))
    with pytest.raises(OpenBBError, match="layout changed"):
        catalog.scrape_release_catalog()


def test_scrape_supplemental_files_happy_path(monkeypatch):
    """``scrape_supplemental_files`` deduplicates and resolves relative hrefs."""
    import requests

    monkeypatch.setattr(
        requests,
        "get",
        _make_router({"prod2.supp.toc.htm": _read_fixture("prod2_supp_toc.html")}),
    )
    rows = catalog.scrape_supplemental_files(
        "https://www.bls.gov/web/prod2.supp.toc.htm"
    )
    urls = [r["url"] for r in rows]

    assert "https://www.bls.gov/web/prod2_supp_table-a.xlsx" in urls
    assert "https://www.bls.gov/web/prod2_supp_table-b.pdf" in urls
    assert "https://www.bls.gov/web/prod2_absolute.xlsx" in urls
    assert "https://example.com/external.pdf" in urls
    assert "https://www.bls.gov/web/data.csv" in urls
    assert "https://www.bls.gov/web/readme.txt" in urls
    assert urls.count("https://www.bls.gov/web/prod2_supp_table-a.xlsx") == 1
    assert not any(u.endswith("notes.html") for u in urls)

    table_a = next(r for r in rows if r["url"].endswith("prod2_supp_table-a.xlsx"))
    assert table_a["format"] == "xlsx"
    assert table_a["name"] == "Prod2 Supp Table A"
    assert table_a["label_from_page"] == "Supplemental Table A"


def test_scrape_supplemental_files_non_200_returns_empty(monkeypatch):
    """``scrape_supplemental_files`` returns ``()`` on HTTP failure."""
    import requests

    monkeypatch.setattr(
        requests,
        "get",
        lambda *a, **k: _FakeResponse(b"", status_code=500),
    )
    assert catalog.scrape_supplemental_files("https://x/y.htm") == ()


def test_scrape_archive_simple_page(monkeypatch):
    """Single-code archive pages return deduped, newest-first rows."""
    import requests

    monkeypatch.setattr(
        requests,
        "get",
        _make_router({"prod.htm": _read_fixture("prod_archive_simple.html")}),
    )

    rows = catalog.scrape_archive("prod2")
    assert len(rows) == 2
    dates = [r["date"] for r in rows]
    assert dates == sorted(dates, reverse=True)
    assert dates[0] == date(2026, 5, 7)
    assert dates[1] == date(2025, 2, 7)

    top = rows[0]
    assert top["code"] == "prod2"
    assert top["pdf_url"] == (
        "https://www.bls.gov/news.release/archives/prod2_05072026.pdf"
    )
    assert top["html_url"] == (
        "https://www.bls.gov/news.release/archives/prod2_05072026.htm"
    )
    assert top["title"] == "duplicate-by-date entry"


def test_scrape_archive_shared_page_prin(monkeypatch):
    """Codes prin/prin1/prin2 share a single page and filter by code only."""
    import requests

    monkeypatch.setattr(
        requests,
        "get",
        _make_router({"prin.htm": _read_fixture("prod_archive_simple.html")}),
    )
    prin_rows = catalog.scrape_archive("prin")
    prin1_rows = catalog.scrape_archive("prin1")
    prin2_rows = catalog.scrape_archive("prin2")

    assert len(prin_rows) == 1
    assert prin_rows[0]["code"] == "prin"
    assert prin_rows[0]["pdf_url"] == (
        "https://www.bls.gov/news.release/archives/prin_03132026.pdf"
    )
    assert prin_rows[0]["html_url"] == (
        "https://www.bls.gov/news.release/archives/prin_03132026.htm"
    )

    assert len(prin1_rows) == 1
    assert prin1_rows[0]["code"] == "prin1"
    assert prin1_rows[0]["pdf_url"] == (
        "https://www.bls.gov/news.release/archives/prin1_02152026.pdf"
    )
    assert prin1_rows[0]["html_url"] is None

    assert len(prin2_rows) == 1
    assert prin2_rows[0]["code"] == "prin2"


def test_scrape_archive_home_page_section_filtering(monkeypatch):
    """Home-page archives are filtered by both code AND section anchor."""
    import requests

    monkeypatch.setattr(
        requests,
        "get",
        _make_router({"home.htm": _read_fixture("prod_archive_home.html")}),
    )

    prod3 = catalog.scrape_archive("prod3")
    prod3_dates = sorted([r["date"] for r in prod3], reverse=True)
    assert prod3_dates == [date(2026, 3, 19), date(2025, 3, 20)]
    assert all(r["code"] == "prod3" for r in prod3)
    assert not any(d == date(2020, 1, 1) for d in prod3_dates)

    prod5 = catalog.scrape_archive("prod5")
    assert len(prod5) == 1
    assert prod5[0]["date"] == date(2025, 11, 14)
    assert prod5[0]["code"] == "prod5"

    prin3 = catalog.scrape_archive("prin3")
    assert len(prin3) == 1
    assert prin3[0]["date"] == date(2025, 9, 30)
    assert prin3[0]["code"] == "prin3"

    prin4 = catalog.scrape_archive("prin4")
    assert len(prin4) == 1
    assert prin4[0]["date"] == date(2025, 6, 18)
    assert prin4[0]["code"] == "prin4"


def test_scrape_archive_unknown_code_returns_empty():
    """Codes outside ``_ARCHIVE_PAGE`` return an empty tuple without HTTP."""
    assert catalog.scrape_archive("does-not-exist") == ()


def test_scrape_archive_page_http_error_returns_empty(monkeypatch):
    """``_scrape_archive_page`` returns ``()`` on HTTP failure."""
    import requests

    monkeypatch.setattr(
        requests,
        "get",
        lambda *a, **k: _FakeResponse(b"", status_code=404),
    )
    assert catalog._scrape_archive_page("https://www.bls.gov/whatever") == ()


def test_scrape_archive_title_backfill_across_entries(monkeypatch):
    """A later titled entry fills in an earlier untitled slot for the same date."""
    import requests

    html = (
        b"<html><body>"
        b"<h4>2026 Releases</h4><ul>"
        b'<li><a href="/news.release/archives/prod2_05072026.pdf">x</a></li>'
        b'<li><a href="/news.release/archives/prod2_05072026.htm">'
        b"2026 First Quarter Productivity and Costs"
        b"</a></li>"
        b"</ul></body></html>"
    )
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(html))
    rows = catalog.scrape_archive("prod2")

    assert len(rows) == 1
    assert rows[0]["date"] == date(2026, 5, 7)
    assert rows[0]["title"] == "2026 First Quarter Productivity and Costs"
    assert rows[0]["pdf_url"] == (
        "https://www.bls.gov/news.release/archives/prod2_05072026.pdf"
    )
    assert rows[0]["html_url"] == (
        "https://www.bls.gov/news.release/archives/prod2_05072026.htm"
    )


def test_scrape_archive_page_anchor_without_href_no_id_is_skipped(monkeypatch):
    """An anchor with neither ``href`` nor ``id`` does not crash and yields nothing."""
    import requests

    html = (
        b"<html><body>"
        b"<a></a>"
        b'<a href="/news.release/archives/prod2_05072026.pdf">'
        b"2026 Q1 Productivity</a>"
        b"</body></html>"
    )
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(html))
    rows = catalog._scrape_archive_page("https://www.bls.gov/bls/news-release/prod.htm")
    assert len(rows) == 1
    assert rows[0]["code"] == "prod2"


def test_scrape_archive_page_div_id_sets_current_section(monkeypatch):
    """A non-anchor element with an ``id`` updates ``current_section``."""
    import requests

    html = (
        b"<html><body>"
        b'<div id="tfp"></div>'
        b'<a href="/news.release/archives/prod3_03192026.pdf">2025 TFP</a>'
        b"</body></html>"
    )
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(html))
    rows = catalog._scrape_archive_page("https://www.bls.gov/bls/news-release/home.htm")
    assert len(rows) == 1
    assert rows[0]["section"] == "tfp"


def test_scrape_archive_page_label_only_anchors_are_skipped(monkeypatch):
    """``HTML``/``PDF``/``XLSX``/``TXT`` label anchors do not populate titles."""
    import requests

    html = (
        b"<html><body><ul>"
        b'<li><a href="/news.release/archives/prod2_05072026.pdf">PDF</a></li>'
        b'<li><a href="/news.release/archives/prod2_05072026.htm">HTML</a></li>'
        b'<li><a href="/news.release/archives/prod2_05072026.xlsx">XLSX</a></li>'
        b'<li><a href="/news.release/archives/prod2_05072026.txt">TXT</a></li>'
        b"</ul></body></html>"
    )
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(html))
    rows = catalog.scrape_archive("prod2")
    assert len(rows) == 1
    assert rows[0]["title"] is None
    assert rows[0]["pdf_url"] == (
        "https://www.bls.gov/news.release/archives/prod2_05072026.pdf"
    )
    assert rows[0]["html_url"] == (
        "https://www.bls.gov/news.release/archives/prod2_05072026.txt"
    )
