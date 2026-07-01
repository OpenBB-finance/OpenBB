"""Tests for the Cleveland Fed publication helpers and index model."""

from datetime import date
from unittest.mock import MagicMock

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.cleveland_publications import (
    FederalReserveClevelandPublicationsData,
    FederalReserveClevelandPublicationsFetcher,
)
from openbb_federal_reserve.utils import cleveland_publications as cp


def _media(slug: str) -> str:
    """Build a fake Cleveland Fed media PDF URL for a slug."""
    return f"{cp.BASE_URL}/-/media/publications/{slug}.pdf"


def _result(slug: str, title: str, release: str, *, pdf: bool, authors=None) -> dict:
    """Build one site-search result record."""
    links = [_media(slug)] if pdf else ["https://x/y/notes.html"]
    return {
        "title": title,
        "releaseDate": release,
        "mediaLinks": links,
        "authors": [{"label": name} for name in (authors or [])],
    }


def _response(results: list[dict], total: int | None) -> MagicMock:
    """Build a JSON site-search response with the given results and total."""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json = MagicMock(
        return_value={"results": results, "pagingInfo": {"total": total}}
    )
    return response


class TestPdfLinkAndAuthors:
    """Tests for the ``_pdf_link`` and ``_authors`` record helpers."""

    def test_pdf_link_found(self):
        """The first ``.pdf`` media link is returned."""
        record = {"mediaLinks": ["https://x/a.docx", _media("b")]}
        assert cp._pdf_link(record) == _media("b")

    def test_pdf_link_missing(self):
        """A record with no PDF media link returns ``None``."""
        assert cp._pdf_link({"mediaLinks": ["https://x/a.docx"]}) is None
        assert cp._pdf_link({}) is None

    def test_authors_joined(self):
        """Author labels join into a comma-separated string."""
        record = {"authors": [{"label": "A. One "}, {"label": "B. Two"}, {}]}
        assert cp._authors(record) == "A. One, B. Two"

    def test_authors_none(self):
        """A record with no authors returns ``None``."""
        assert cp._authors({"authors": []}) is None
        assert cp._authors({}) is None


class TestIndexSeries:
    """Tests for the per-series site-search indexer."""

    def test_pages_and_keeps_pdf_records(self, monkeypatch):
        """The indexer pages by offset, drops non-PDF records, stops on total."""

        def _request(url, *args, **kwargs):
            """Serve two pages of regional-policy-report results."""
            if "e=0" in url:
                return _response(
                    [
                        _result("rpr-2026", "Almanac 2026", "2026-01-08", pdf=True),
                        _result("nopdf", "HTML Only", "2025-06-01", pdf=False),
                    ],
                    total=3,
                )
            return _response(
                [
                    _result(
                        "rpr-2023", "Migration", "2023-08-01", pdf=True, authors=["X"]
                    )
                ],
                total=3,
            )

        monkeypatch.setattr("openbb_core.provider.utils.helpers.make_request", _request)
        records = cp._index_series("regional_policy_report")
        assert [r["id"] for r in records] == ["rpr-2026.pdf", "rpr-2023.pdf"]
        assert records[0]["date"] == "2026-01-08"
        assert records[0]["series"] == "regional_policy_report"
        assert records[1]["authors"] == "X"
        assert records[0]["url"].endswith("rpr-2026.pdf")

    def test_empty_page_breaks(self, monkeypatch):
        """An empty results page stops paging without raising."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response([], total=0),
        )
        assert cp._index_series("economic_review") == []

    def test_falls_back_to_sort_date(self, monkeypatch):
        """A record lacking a release date falls back to its sort date."""
        result = {
            "title": "No Release Date",
            "sortDate": "2024-03-15T00:00:00",
            "mediaLinks": [_media("sd")],
            "authors": [],
        }
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response([result], total=1),
        )
        records = cp._index_series("economic_review")
        assert records[0]["date"] == "2024-03-15"

    def test_no_total_stops_at_max_pages(self, monkeypatch):
        """A response without a total keeps paging up to the page cap."""
        calls = {"n": 0}

        def _request(url, *args, **kwargs):
            """Return one full page each call, never reporting a total."""
            calls["n"] += 1
            results = [
                _result(f"p{calls['n']}-{i}", f"T{i}", "2020-01-01", pdf=True)
                for i in range(cp._PAGE_SIZE)
            ]
            return _response(results, total=None)

        monkeypatch.setattr(cp, "_MAX_PAGES", 2)
        monkeypatch.setattr("openbb_core.provider.utils.helpers.make_request", _request)
        records = cp._index_series("economic_review")
        assert calls["n"] == 2
        assert len(records) == 2 * cp._PAGE_SIZE


class TestListPublications:
    """Tests for ``list_publications``."""

    def test_single_series(self, monkeypatch):
        """A single-series request indexes only that series."""
        monkeypatch.setattr(
            cp,
            "_index_series",
            lambda name: [
                {
                    "series": name,
                    "id": "a",
                    "date": "2026-01-01",
                    "title": "A",
                    "url": _media("a"),
                    "authors": None,
                }
            ],
        )
        catalog = cp.list_publications("economic_commentary")
        assert len(catalog) == 1
        assert catalog[0]["series"] == "economic_commentary"

    def test_merged_newest_first(self, monkeypatch):
        """With no series every series merges, sorted newest first."""

        def _index(name):
            """Return one synthetic record per series with a series-derived date."""
            year = 2020 + list(cp._SERIES).index(name)
            return [
                {
                    "series": name,
                    "id": name,
                    "date": f"{year}-01-01",
                    "title": name,
                    "url": _media(name),
                    "authors": None,
                }
            ]

        monkeypatch.setattr(cp, "_index_series", _index)
        catalog = cp.list_publications()
        assert {r["series"] for r in catalog} == set(cp._SERIES)
        assert catalog == sorted(catalog, key=lambda r: r["date"], reverse=True)

    def test_unknown_series_raises(self):
        """An unsupported series raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            cp.list_publications("not_a_series")


class TestPublicationsIndexModel:
    """Tests for the discovery index data model."""

    _CATALOG = [
        {
            "series": "working_paper",
            "id": "wp-2614",
            "date": "2026-06-02",
            "title": "A Working Paper",
            "url": "https://x/wp.pdf",
            "authors": "Jane Doe",
        },
        {
            "series": "economic_commentary",
            "id": "ec-202601",
            "date": "2026-02-02",
            "title": "An Economic Commentary",
            "url": "https://x/ec.pdf",
            "authors": None,
        },
        {
            "series": "annual_report",
            "id": "ar-2024",
            "date": "2025-04-01",
            "title": "Annual Report 2024",
            "url": "https://x/ar.pdf",
            "authors": None,
        },
    ]

    def _patch(self, monkeypatch):
        """Point the index model at a synthetic catalog."""
        monkeypatch.setattr(
            cp, "list_publications", lambda series=None: list(self._CATALOG)
        )

    def test_filters_start_and_end_date(self, monkeypatch):
        """The start_date and end_date filters narrow the catalog."""
        self._patch(monkeypatch)
        query = FederalReserveClevelandPublicationsFetcher.transform_query(
            {"start_date": "2026-01-01", "end_date": "2026-06-15"}
        )
        rows = FederalReserveClevelandPublicationsFetcher.transform_data(
            query,
            FederalReserveClevelandPublicationsFetcher.extract_data(query, None),
        )
        assert all(isinstance(r, FederalReserveClevelandPublicationsData) for r in rows)
        assert [r.title for r in rows] == ["A Working Paper", "An Economic Commentary"]
        assert rows[0].date == date(2026, 6, 2)
        assert rows[0].authors == "Jane Doe"
        assert not hasattr(rows[0], "id")

    def test_no_filter_returns_all(self, monkeypatch):
        """With no filters the full catalog is returned."""
        self._patch(monkeypatch)
        query = FederalReserveClevelandPublicationsFetcher.transform_query({})
        rows = FederalReserveClevelandPublicationsFetcher.transform_data(
            query,
            FederalReserveClevelandPublicationsFetcher.extract_data(query, None),
        )
        assert len(rows) == 3

    def test_empty_raises(self, monkeypatch):
        """An empty catalog raises ``EmptyDataError``."""
        monkeypatch.setattr(cp, "list_publications", lambda series=None: [])
        query = FederalReserveClevelandPublicationsFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveClevelandPublicationsFetcher.extract_data(query, None)


class TestPublicationsChoices:
    """Tests for the shared regional_publications_choices contract."""

    @pytest.mark.asyncio
    async def test_choices_expose_pdf_urls(self, monkeypatch):
        """The choices endpoint surfaces each catalog PDF as a labeled choice."""
        from openbb_federal_reserve.federal_reserve_router import (
            regional_publications_choices,
        )

        monkeypatch.setattr(
            cp,
            "list_publications",
            lambda series=None: [
                {
                    "series": "regional_policy_report",
                    "id": "rpr-2026",
                    "date": "2026-01-08",
                    "title": "Fourth District Almanac 2026",
                    "url": _media("rpr-2026"),
                    "authors": "X",
                }
            ],
        )
        choices = await regional_publications_choices("cleveland")
        assert choices[0]["value"] == _media("rpr-2026")
        assert "Fourth District Almanac 2026" in choices[0]["label"]
        assert "2026-01" in choices[0]["label"]
