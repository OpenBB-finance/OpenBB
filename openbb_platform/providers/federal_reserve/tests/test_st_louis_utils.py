"""Tests for the St. Louis Fed data client and Fed in Print search helpers."""

from unittest.mock import MagicMock

import pytest

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


class TestSeriesSlugs:
    """Tests for the curated series slugs and their display labels."""

    def test_slugs_exclude_web_only_series(self):
        """Web-only blog series are absent from the selectable document series."""
        assert "on_the_economy" not in st_louis.SERIES_SLUGS
        assert "open_vault" not in st_louis.SERIES_SLUGS
        assert "working_papers" in st_louis.SERIES_SLUGS
        assert "economic_synopses" in st_louis.SERIES_SLUGS

    def test_choices_map_labels_to_slugs(self):
        """Each choice pairs a display label with its slug and maps to a facet."""
        choices = st_louis.series_choices()
        assert {"label": "Working Papers", "value": "working_papers"} in choices
        assert [choice["value"] for choice in choices] == list(st_louis.SERIES_SLUGS)
        for slug in st_louis.SERIES_SLUGS:
            assert slug in st_louis._FACET_BY_SLUG


class TestSearchPublications:
    """Tests for the St. Louis wrapper over the shared Fed in Print search."""

    def test_maps_slug_to_facet_and_forwards(self, monkeypatch):
        """The wrapper maps a slug to its facet and forwards paging to the util."""
        from openbb_federal_reserve.utils import fedinprint

        captured = {}

        def _search(provider, fetch, series_facet=None, min_year="", start=0, limit=20):
            captured.update(
                provider=provider,
                facet=series_facet,
                min_year=min_year,
                start=start,
                limit=limit,
            )
            return [{"series": "Working Papers", "date": "", "title": "T", "url": "u"}]

        monkeypatch.setattr(fedinprint, "search", _search)
        out = st_louis.search_publications("working_papers", "2024", start=10, limit=5)
        assert captured["provider"] == st_louis.FEDINPRINT_PROVIDER
        assert captured["facet"] == "Working Papers"
        assert (captured["min_year"], captured["start"], captured["limit"]) == (
            "2024",
            10,
            5,
        )
        assert out[0]["title"] == "T"

    def test_unknown_or_absent_slug_has_no_facet(self, monkeypatch):
        """An unknown or absent slug queries the provider with no series facet."""
        from openbb_federal_reserve.utils import fedinprint

        captured = {}

        def _search(provider, fetch, series_facet=None, **_):
            captured["facet"] = series_facet
            return []

        monkeypatch.setattr(fedinprint, "search", _search)
        st_louis.search_publications("bogus")
        assert captured["facet"] is None
        st_louis.search_publications(None)
        assert captured["facet"] is None


class TestListPublications:
    """Tests for the cached, paginated catalog entry point."""

    def test_delegates_with_validated_slug(self, monkeypatch):
        """A valid slug, derived year, and paging are forwarded to the search."""
        from datetime import date

        captured = {}

        def _search(series=None, min_year="", start=0, limit=20):
            captured.update(series=series, min_year=min_year, start=start, limit=limit)
            return [
                {"series": "Review", "date": "2024-05-01", "title": "T", "url": "u"}
            ]

        monkeypatch.setattr(st_louis, "search_publications", _search)
        out = st_louis.list_publications(
            series="working_papers", start_date=date(2024, 5, 1), start=20, limit=5
        )
        assert captured == {
            "series": "working_papers",
            "min_year": "2024",
            "start": 20,
            "limit": 5,
        }
        assert out[0]["title"] == "T"

    def test_unknown_slug_and_no_start_date(self, monkeypatch):
        """An unknown slug and absent start date pass None and an empty year."""
        captured = {}

        def _search(series=None, min_year="", start=0, limit=20):
            captured.update(series=series, min_year=min_year)
            return []

        monkeypatch.setattr(st_louis, "search_publications", _search)
        st_louis.list_publications(series="bogus")
        assert captured["series"] is None
        assert captured["min_year"] == ""


class TestListSeries:
    """Tests for the supported-series directory."""

    def test_merges_supported_series_with_counts(self, monkeypatch):
        """Every supported series is returned with its live count, defaulting to 0."""
        from openbb_federal_reserve.utils import fedinprint

        monkeypatch.setattr(
            fedinprint,
            "series_counts",
            lambda provider, fetch: {"Working Papers": 1850},
        )
        series = st_louis.list_series()
        assert len(series) == len(st_louis.SERIES_SLUGS)
        assert {
            "series": "working_papers",
            "name": "Working Papers",
            "count": 1850,
        } in series
        review = next(record for record in series if record["series"] == "review")
        assert review["count"] == 0
