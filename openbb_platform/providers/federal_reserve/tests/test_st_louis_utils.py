"""Tests for the St. Louis Fed data client and FRASER enumeration helpers."""

from unittest.mock import MagicMock

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_federal_reserve.utils import st_louis


@pytest.fixture(autouse=True)
def _no_cache(monkeypatch):
    """Bypass the disk cache so producers run directly in tests."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.cache.cached",
        lambda key, ttl, producer: producer(),
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.cache.seconds_until_next_release",
        lambda cadence: 60.0,
    )
    st_louis.reset_session()
    yield
    st_louis.reset_session()


def _response(status=200, *, text="", content=b"") -> MagicMock:
    """Build a fake curl_cffi response."""
    response = MagicMock()
    response.status_code = status
    response.text = text
    response.content = content
    response.raise_for_status = MagicMock()
    return response


class _Session:
    """A scripted curl_cffi session double keyed by URL substrings."""

    def __init__(self, routes, warmups=None):
        self.routes = routes
        self.warmups = warmups if warmups is not None else []
        self.calls: list[str] = []

    def get(self, url, headers=None, timeout=None):
        """Return the first matching scripted response and record the call."""
        self.calls.append(url)
        if url in (
            "https://www.stlouisfed.org/",
            "https://fred.stlouisfed.org/",
            "https://fraser.stlouisfed.org/",
        ):
            self.warmups.append(url)
            return _response(200)
        for needle, response in self.routes:
            if needle in url:
                return response() if isinstance(response, _Producer) else response
        return _response(404)


class _Producer:
    """Wrap a zero-argument callable so the session double calls it lazily."""

    def __init__(self, func):
        self.func = func

    def __call__(self):
        """Return the next scripted response."""
        return self.func()


def _install(monkeypatch, session):
    """Force ``_get_session`` to return the provided session double."""
    monkeypatch.setattr(st_louis, "_get_session", lambda: session)


class TestSession:
    """Tests for the warmed session lifecycle."""

    def test_get_session_warms_all_hosts(self, monkeypatch):
        """The session warms every St. Louis host once and is cached."""
        from curl_cffi import requests as curl_requests

        session = _Session([])
        monkeypatch.setattr(curl_requests, "Session", lambda impersonate: session)
        first = st_louis._get_session()
        second = st_louis._get_session()
        assert first is second
        assert set(first.warmups) == set(st_louis._WARMUP_HOSTS)

    def test_reset_session(self, monkeypatch):
        """Resetting drops the cached session so the next call builds a fresh one."""
        from curl_cffi import requests as curl_requests

        sessions = iter([_Session([]), _Session([])])
        monkeypatch.setattr(
            curl_requests, "Session", lambda impersonate: next(sessions)
        )
        first = st_louis._get_session()
        assert st_louis._get_session() is first
        st_louis.reset_session()
        second = st_louis._get_session()
        assert second is not first
        assert set(second.warmups) == set(st_louis._WARMUP_HOSTS)


class TestFetch:
    """Tests for ``fetch_text`` and ``fetch_bytes``."""

    def test_fetch_text_ok(self, monkeypatch):
        """A 200 returns the body text."""
        session = _Session([("data.csv", _response(200, text="a,b"))])
        _install(monkeypatch, session)
        assert st_louis.fetch_text("https://x/data.csv", referer="https://x/") == "a,b"

    def test_fetch_bytes_ok(self, monkeypatch):
        """A 200 returns the body bytes."""
        session = _Session([("file.pdf", _response(200, content=b"%PDF"))])
        _install(monkeypatch, session)
        assert st_louis.fetch_bytes("https://x/file.pdf") == b"%PDF"

    def test_fetch_text_rewarms_on_403(self, monkeypatch):
        """A 403 drops the session and retries once."""
        first = _response(403)
        second = _response(200, text="ok")
        responses = iter([first, second])
        session = _Session([("data.csv", _Producer(lambda: next(responses)))])
        sessions = iter([session, session])
        monkeypatch.setattr(st_louis, "_get_session", lambda: next(sessions))
        reset_calls = []
        real_reset = st_louis.reset_session
        monkeypatch.setattr(
            st_louis, "reset_session", lambda: reset_calls.append(1) or real_reset()
        )
        assert st_louis.fetch_text("https://x/data.csv") == "ok"
        assert reset_calls == [1]

    def test_fetch_bytes_rewarms_on_403(self, monkeypatch):
        """A 403 on a bytes fetch drops the session and retries once."""
        responses = iter([_response(403), _response(200, content=b"%PDF")])
        session = _Session([("file.pdf", _Producer(lambda: next(responses)))])
        monkeypatch.setattr(st_louis, "_get_session", lambda: session)
        monkeypatch.setattr(st_louis, "reset_session", lambda: None)
        assert st_louis.fetch_bytes("https://x/file.pdf") == b"%PDF"


class TestCachedDownloads:
    """Tests for the cache-wrapped download helpers."""

    def test_fetch_fred_graph_csv(self, monkeypatch):
        """The fredgraph helper formats the URL and returns the text."""
        captured = {}

        def _capture(url, referer=None):
            captured["url"] = url
            return "csv"

        monkeypatch.setattr(st_louis, "fetch_text", _capture)
        assert st_louis.fetch_fred_graph_csv("STLFSI4") == "csv"
        assert "id=STLFSI4" in captured["url"]

    def test_fetch_fred_panel_monthly(self, monkeypatch):
        """The monthly panel uses the FRED-MD URL."""
        captured = {}

        def _capture(url, referer=None):
            captured["url"] = url
            return "panel"

        monkeypatch.setattr(st_louis, "fetch_text", _capture)
        assert st_louis.fetch_fred_panel("monthly") == "panel"
        assert captured["url"] == st_louis.FRED_MD_URL

    def test_fetch_fred_panel_quarterly(self, monkeypatch):
        """The quarterly panel uses the FRED-QD URL."""
        captured = {}

        def _capture(url, referer=None):
            captured["url"] = url
            return "panel"

        monkeypatch.setattr(st_louis, "fetch_text", _capture)
        assert st_louis.fetch_fred_panel("quarterly") == "panel"
        assert captured["url"] == st_louis.FRED_QD_URL

    def test_fetch_fred_panel_invalid(self):
        """An unknown frequency raises ``ValueError``."""
        with pytest.raises(ValueError, match="frequency"):
            st_louis.fetch_fred_panel("daily")


_BROWSE_ITEM = (
    '<a class="list-item" data-id="{item_id}" data-type="item" '
    'href="/title/economic-synopses-6715/{slug}-{item_id}" id="item-{item_id}">'
    '<span class="list-item-title">{title}, {year}, No. {issue}</span></a>'
)


def _browse_html(items):
    """Render a FRASER browse page from item tuples."""
    return "".join(
        _BROWSE_ITEM.format(item_id=i, slug=s, title=t, year=y, issue=n)
        for i, s, t, y, n in items
    )


def _landing_html(stamp: str) -> str:
    """Render a landing page carrying a dated citation PDF URL."""
    return (
        '<meta name="citation_pdf_url" content="https://fraser.stlouisfed.org/files/'
        f'docs/publications/frbsl_econosynops/economicsynopses_stls_{stamp}.pdf" />'
    )


class TestListEconomicSynopses:
    """Tests for the FRASER catalog scraper."""

    def test_parses_dedups_and_sorts(self, monkeypatch):
        """Articles parse, resolve dates, dedupe by id, and sort newest first."""
        pages = {
            "2020s": _browse_html(
                [("624571", "college-wealth", "The College Wealth Divide", 2020, 1)]
            ),
            "2010s": _browse_html(
                [("400001", "evolving-banks", "The Evolving Size of Banks", 2010, 1)]
            ),
            "2000s": _browse_html([]),
        }
        landings = {"624571": "20200409", "400001": "20100115"}

        def _fetch(url, referer=None):
            for decade, html in pages.items():
                if decade in url:
                    return html
            for item_id, stamp in landings.items():
                if item_id in url:
                    return _landing_html(stamp)
            return ""

        monkeypatch.setattr(st_louis, "fetch_text", _fetch)
        catalog = st_louis.list_economic_synopses()
        assert [r["date"] for r in catalog] == ["2020-04-09", "2010-01-15"]
        assert catalog[0]["year"] == 2020
        assert catalog[0]["title"] == "The College Wealth Divide"
        assert catalog[0]["url"].startswith("https://fraser.stlouisfed.org")

    def test_unresolvable_date_is_empty(self, monkeypatch):
        """An article whose landing page has no PDF resolves to an empty date."""
        page = _browse_html(
            [("1", "real", "Getting &quot;Real&quot; About Policy", 2002, 1)]
        )

        def _fetch(url, referer=None):
            if "browse" in url:
                return page if "2000s" in url else _browse_html([])
            return "<html></html>"

        monkeypatch.setattr(st_louis, "fetch_text", _fetch)
        catalog = st_louis.list_economic_synopses()
        assert catalog[0]["title"] == 'Getting "Real" About Policy'
        assert catalog[0]["date"] == ""

    def test_title_without_issue_tail(self, monkeypatch):
        """An entry lacking the ``YYYY, No. NN`` tail keeps a null year/issue."""
        article = (
            '<a class="list-item" data-id="9" data-type="item" '
            'href="/title/economic-synopses-6715/odd-9" id="item-9">'
            '<span class="list-item-title">An Untagged Article</span></a>'
        )

        def _fetch(url, referer=None):
            if "browse" in url:
                return article if "2000s" in url else _browse_html([])
            return _landing_html("20020110")

        monkeypatch.setattr(st_louis, "fetch_text", _fetch)
        catalog = st_louis.list_economic_synopses()
        assert catalog[0]["year"] is None
        assert catalog[0]["issue"] is None
        assert catalog[0]["title"] == "An Untagged Article"
        assert catalog[0]["date"] == "2002-01-10"


_LANDING = (
    '<meta name="citation_pdf_url" content="https://fraser.stlouisfed.org/files/'
    'docs/publications/frbsl_econosynops/economicsynopses_stls_20200409.pdf" />'
)


class TestResolveSynopsisPdfUrl:
    """Tests for the landing-page PDF resolver."""

    def test_resolves_url_and_date(self, monkeypatch):
        """The resolver extracts the PDF URL and its filename date."""
        monkeypatch.setattr(st_louis, "fetch_text", lambda url, referer=None: _LANDING)
        out = st_louis.resolve_synopsis_pdf_url("https://x/landing")
        assert out["url"].endswith("economicsynopses_stls_20200409.pdf")
        assert out["date"] == "2020-04-09"

    def test_resolves_url_without_date(self, monkeypatch):
        """A PDF URL without the dated filename yields an empty date."""
        html = '<meta name="citation_pdf_url" content="https://x/files/other.pdf" />'
        monkeypatch.setattr(st_louis, "fetch_text", lambda url, referer=None: html)
        out = st_louis.resolve_synopsis_pdf_url("https://x/landing")
        assert out["date"] == ""

    def test_missing_pdf_raises(self, monkeypatch):
        """A landing page without a PDF link raises ``OpenBBError``."""
        monkeypatch.setattr(
            st_louis, "fetch_text", lambda url, referer=None: "<html></html>"
        )
        with pytest.raises(OpenBBError):
            st_louis.resolve_synopsis_pdf_url("https://x/landing")


_PUBLICATIONS = [
    {
        "item_id": "672949",
        "title": "Latest",
        "year": 2024,
        "issue": 14,
        "date": "2024-07-01",
        "url": "https://x/latest-672949",
        "pdf_url": "https://x/latest.pdf",
    },
    {
        "item_id": "624571",
        "title": "Older",
        "year": 2020,
        "issue": 1,
        "date": "2020-04-09",
        "url": "https://x/older-624571",
        "pdf_url": "https://x/older.pdf",
    },
    {
        "item_id": "111111",
        "title": "No PDF",
        "year": None,
        "issue": None,
        "date": "",
        "url": "https://x/no-pdf-111111",
        "pdf_url": "",
    },
]


class TestListPublications:
    """Tests for the publications-catalog aggregation helper."""

    def test_folds_pdfs_and_skips_missing(self, monkeypatch):
        """Synopses with a PDF url become records, newest first; PDF-less ones drop."""
        monkeypatch.setattr(st_louis, "list_economic_synopses", lambda: _PUBLICATIONS)
        catalog = st_louis.list_publications()
        assert [record["id"] for record in catalog] == ["672949", "624571"]
        assert catalog[0]["series"] == "economic_synopses"
        assert catalog[0]["url"] == "https://x/latest.pdf"
        assert catalog[0]["date"] == "2024-07-01"
