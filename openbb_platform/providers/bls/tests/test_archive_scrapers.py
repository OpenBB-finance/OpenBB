"""Tests for the single-program BLS archive scrapers.

Each scraper (``cpi_archive``, ``empsit_archive``, ``realer_archive``,
``ximpim_archive``) shares the same shape:

* ``scrape_archive() -> tuple[dict, ...]`` — hits the BLS HTML index page
  and returns one record per archived PDF (newest-first), de-duplicated by
  href and tolerant of (a) entries with an explicit ``aria-label``, (b)
  older entries where the title is bare text inside ``<li>``, and (c)
  malformed date tokens that must be silently skipped.
* ``current_release() -> dict`` — returns a static record pointing at the
  always-current PDF / HTML URLs.

Each module's HTTP fetch is replaced with a canned ``requests.get`` that
serves bundled HTML fixtures under ``tests/fixtures/*_archive.html``. The
fixtures are tiny (a few hundred bytes) and exercise every branch of the
scraper.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

import openbb_bls.utils.cpi_archive as cpi_arch
import openbb_bls.utils.empsit_archive as empsit_arch
import openbb_bls.utils.realer_archive as realer_arch
import openbb_bls.utils.ximpim_archive as ximpim_arch

_FIXTURES = Path(__file__).parent / "fixtures"


class _FakeResponse:
    """Minimal ``requests.Response`` stand-in for HTML pages."""

    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self) -> None:
        """No-op — fixture responses are always 200."""


def _make_get(fixture_name: str):
    """Build a fake ``requests.get`` that returns one bundled fixture."""

    def _get(url: str, *args, **kwargs) -> _FakeResponse:
        return _FakeResponse((_FIXTURES / fixture_name).read_bytes())

    return _get


def _make_404_get():
    """Build a fake ``requests.get`` that returns HTTP 404 for every URL."""

    def _get(url: str, *args, **kwargs) -> _FakeResponse:
        return _FakeResponse(b"", status_code=404)

    return _get


_ARCHIVES = [
    (
        "cpi",
        cpi_arch,
        "cpi_archive.html",
        date(2026, 5, 12),
        "April 2026 Consumer Price Index",
        "https://www.bls.gov/news.release/archives/cpi_05122026.pdf",
        "https://www.bls.gov/news.release/pdf/cpi.pdf",
        "Consumer Price Index — current release",
        # Oldest entry uses the fallback (no aria-label):
        "July 2002 Consumer Price Index",
        date(2002, 8, 16),
    ),
    (
        "empsit",
        empsit_arch,
        "empsit_archive.html",
        date(2026, 5, 8),
        "April 2026 Employment Situation",
        "https://www.bls.gov/news.release/archives/empsit_05082026.pdf",
        "https://www.bls.gov/news.release/pdf/empsit.pdf",
        "Employment Situation — current release",
        "January 1995 Employment Situation",
        date(1995, 2, 3),
    ),
    (
        "realer",
        realer_arch,
        "realer_archive.html",
        date(2026, 5, 12),
        "April 2026 Real Earnings",
        "https://www.bls.gov/news.release/archives/realer_05122026.pdf",
        "https://www.bls.gov/news.release/pdf/realer.pdf",
        "Real Earnings — current release",
        None,
        None,
    ),
    (
        "ximpim",
        ximpim_arch,
        "ximpim_archive.html",
        date(2026, 5, 14),
        "April 2026 U.S. Import and Export Price Indexes",
        "https://www.bls.gov/news.release/archives/ximpim_05142026.pdf",
        "https://www.bls.gov/news.release/pdf/ximpim.pdf",
        "U.S. Import and Export Price Indexes — current release",
        None,
        None,
    ),
]


@pytest.fixture(autouse=True)
def _clear_archive_caches():
    """Drop ``scrape_archive`` lru_cache state between tests so each test starts fresh."""
    for _, module, *_rest in _ARCHIVES:
        module.scrape_archive.cache_clear()
    yield
    for _, module, *_rest in _ARCHIVES:
        module.scrape_archive.cache_clear()


@pytest.mark.parametrize(
    "label,module,fixture,latest_date,latest_title,latest_url,"
    "current_url,current_title,fallback_title,fallback_date",
    _ARCHIVES,
    ids=[t[0] for t in _ARCHIVES],
)
def test_archive_scraper_full_pass(
    monkeypatch,
    label,
    module,
    fixture,
    latest_date,
    latest_title,
    latest_url,
    current_url,
    current_title,
    fallback_title,
    fallback_date,
):
    """Each scraper extracts the newest PDF + uses the aria-label / li fallback."""
    import requests

    monkeypatch.setattr(requests, "get", _make_get(fixture))
    rows = module.scrape_archive()
    assert len(rows) >= 1

    top = rows[0]
    assert top["date"] == latest_date
    assert top["title"] == latest_title
    assert top["url"] == latest_url

    # Newest-first ordering
    dates = [r["date"] for r in rows]
    assert dates == sorted(dates, reverse=True)

    if fallback_title is not None:
        # The old-style entry (no aria-label) should be picked up via the
        # parent-<li> text fallback with (TXT)/(PDF) markers stripped.
        last = rows[-1]
        assert last["date"] == fallback_date
        assert last["title"] == fallback_title

    # current_release() is a static dict
    cur = module.current_release()
    assert cur["url"] == current_url
    assert cur["title"] == current_title


@pytest.mark.parametrize(
    "label,module,fixture",
    [(t[0], t[1], t[2]) for t in _ARCHIVES],
    ids=[t[0] for t in _ARCHIVES],
)
def test_archive_scraper_404_raises(monkeypatch, label, module, fixture):
    """Non-200 responses surface as OpenBBError so callers see the failure."""
    import requests
    from openbb_core.app.model.abstract.error import OpenBBError

    monkeypatch.setattr(requests, "get", _make_404_get())
    with pytest.raises(OpenBBError, match="HTTP 404"):
        module.scrape_archive()


def test_empsit_prefers_li_text_over_stale_aria(monkeypatch):
    """BLS ships stale aria-labels on recent Employment Situation entries.

    The three most recent releases share one outdated ``aria-label``
    ("February 2026"), while the visible ``<li>`` text holds the correct
    reference month. The scraper must trust the list text so each month is
    distinct and correct rather than collapsing into duplicate names.
    """
    import requests

    monkeypatch.setattr(requests, "get", _make_get("empsit_archive.html"))
    rows = empsit_arch.scrape_archive()
    titles = {r["url"].rsplit("/", 1)[1]: r["title"] for r in rows}
    assert titles["empsit_05082026.pdf"] == "April 2026 Employment Situation"
    assert titles["empsit_04032026.pdf"] == "March 2026 Employment Situation"
    assert titles["empsit_03062026.pdf"] == "February 2026 Employment Situation"
    recent = [
        titles["empsit_05082026.pdf"],
        titles["empsit_04032026.pdf"],
        titles["empsit_03062026.pdf"],
    ]
    assert len(set(recent)) == 3


@pytest.mark.parametrize(
    "label,module",
    [(t[0], t[1]) for t in _ARCHIVES],
    ids=[t[0] for t in _ARCHIVES],
)
def test_archive_scraper_decode_fallback(monkeypatch, label, module):
    """Latin-1 bytes that fail UTF-8 decode still parse via the fallback decoder."""
    import requests

    latin1_html = "<html><body><h4 id='2024'>café 2024</h4></body></html>".encode(
        "latin-1"
    )
    monkeypatch.setattr(
        requests,
        "get",
        lambda *a, **k: _FakeResponse(latin1_html),
    )
    rows = module.scrape_archive()
    assert rows == ()
