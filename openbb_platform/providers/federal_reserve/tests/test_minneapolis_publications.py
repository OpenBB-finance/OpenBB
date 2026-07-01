"""Tests for the Minneapolis Fed publication helpers, index model, and commands."""

import base64
from datetime import date
from unittest.mock import MagicMock

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.minneapolis_publications import (
    FederalReserveMinneapolisPublicationsData,
    FederalReserveMinneapolisPublicationsFetcher,
)
from openbb_federal_reserve.utils import minneapolis_publications as mp

_HUB_HTML = (
    '<a href="/research/working-papers/how-small">x</a>'
    '<a href="/research/institute-working-papers/credit-supply">x</a>'
    '<a href="/research/cicd-working-paper-series/native-homeownership">x</a>'
    '<a href="/research/staff-reports/occupational-licensing">x</a>'
    '<a href="/research/quarterly-review/trade-in-ai">x</a>'
    '<a href="/research/working-papers/no-pdf-here">x</a>'
)

_LANDINGS = {
    "/research/working-papers/how-small": (
        '<meta name="title" content="How Small is Small? | Minneapolis"/>'
        '<meta name="sortDate" content="2026-06-22T05:00:00Z"/>'
        '<a href="/research/wp/wp815.pdf">PDF</a>'
        '<img alt="photo of Javier Bianchi"/><img alt="photo of Javier Bianchi"/>'
    ),
    "/research/institute-working-papers/credit-supply": (
        '<meta name="title" content="Credit Supply &amp; Firms | Minneapolis"/>'
        '<meta name="sortDate" content="2026-05-22T05:00:00Z"/>'
        '<a href="/institute/working-papers-institute/iwp128.pdf">PDF</a>'
    ),
    "/research/cicd-working-paper-series/native-homeownership": (
        '<meta name="title" content="Unequal Costs | Minneapolis"/>'
        '<meta name="sortDate" content="2026-04-29T05:00:00Z"/>'
        '<a href="https://www.minneapolisfed.org/-/media/cicd-wp-2023-04.pdf">PDF</a>'
    ),
    "/research/staff-reports/occupational-licensing": (
        '<meta name="title" content="Occupational Licensing | Minneapolis"/>'
        '<meta name="sortDate" content="2026-06-12T05:00:00Z"/>'
        '<a href="/research/sr/sr667.pdf">PDF</a>'
    ),
    "/research/quarterly-review/trade-in-ai": (
        '<meta name="title" content="Trade in AI-Related Products | Minneapolis"/>'
        '<meta name="sortDate" content="2026-06-01T05:00:00Z"/>'
        '<a content="/research/qr/qr4612.pdf">PDF</a>'
    ),
    "/research/working-papers/no-pdf-here": (
        '<meta name="title" content="No PDF | Minneapolis"/>'
        '<meta name="sortDate" content="2026-03-01T05:00:00Z"/>'
        "<p>landing page without a PDF link</p>"
    ),
}


def _html_response(text: str) -> MagicMock:
    """Build a text/PDF response with the given body."""
    response = MagicMock()
    response.headers = {"Content-Type": "text/html"}
    response.text = text
    response.content = b"%PDF-1.7 fake minneapolis pdf"
    response.raise_for_status = MagicMock()
    return response


def _make_request(url, *args, **kwargs):
    """Path-aware fake covering the research hub, landing pages, and PDFs."""
    if url.endswith("/research"):
        return _html_response(_HUB_HTML)
    for path, body in _LANDINGS.items():
        if url.endswith(path):
            return _html_response(body)
    return _html_response("")


@pytest.fixture(autouse=True)
def _patch_make_request(monkeypatch):
    """Route every helper request through the path-aware fake."""
    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.make_request", _make_request
    )


class TestIndexResearchHub:
    """Tests for the research-hub landing-link indexer."""

    def test_lists_landing_paths(self):
        """The hub indexer returns the deduplicated landing paths."""
        paths = mp._index_research_hub()
        assert "/research/working-papers/how-small" in paths
        assert "/research/quarterly-review/trade-in-ai" in paths
        assert len(paths) == 6


class TestResolveLanding:
    """Tests for the per-landing-page PDF resolver."""

    def test_resolves_pdf_date_title_authors(self):
        """A landing page resolves its PDF, date, title, and author block."""
        record = mp._resolve_landing("/research/working-papers/how-small")
        assert record["series"] == "working_paper"
        assert record["id"] == "how-small"
        assert record["date"] == "2026-06-22"
        assert record["title"] == "How Small is Small?"
        assert record["url"].endswith("/research/wp/wp815.pdf")
        assert record["authors"] == "Javier Bianchi"

    def test_absolute_pdf_and_unescaped_title(self):
        """An absolute PDF URL is preserved and HTML entities are unescaped."""
        record = mp._resolve_landing("/research/institute-working-papers/credit-supply")
        assert record["series"] == "institute_working_paper"
        assert record["title"] == "Credit Supply & Firms"
        assert record["url"].endswith("/institute/working-papers-institute/iwp128.pdf")
        assert record["authors"] is None

    def test_already_absolute_pdf_url(self):
        """A landing page that links an already-absolute PDF keeps that URL."""
        record = mp._resolve_landing(
            "/research/cicd-working-paper-series/native-homeownership"
        )
        assert record["series"] == "cicd_working_paper"
        assert record["url"] == (
            "https://www.minneapolisfed.org/-/media/cicd-wp-2023-04.pdf"
        )

    def test_content_attribute_pdf(self):
        """A PDF referenced via a content attribute is still resolved."""
        record = mp._resolve_landing("/research/quarterly-review/trade-in-ai")
        assert record["series"] == "quarterly_review"
        assert record["url"].endswith("/research/qr/qr4612.pdf")

    def test_landing_without_pdf_returns_none(self):
        """A landing page without a PDF link resolves to ``None``."""
        assert mp._resolve_landing("/research/working-papers/no-pdf-here") is None

    def test_title_falls_back_to_slug(self, monkeypatch):
        """A landing page lacking a title meta tag titles from the slug."""

        def _request(url, *args, **kwargs):
            """Serve a landing page with a PDF but no title meta tag."""
            if url.endswith("/research/working-papers/how-small"):
                return _html_response(
                    '<meta name="sortDate" content="2026-06-22T05:00:00Z"/>'
                    '<a href="/research/wp/wp815.pdf">PDF</a>'
                )
            return _make_request(url, *args, **kwargs)

        monkeypatch.setattr("openbb_core.provider.utils.helpers.make_request", _request)
        record = mp._resolve_landing("/research/working-papers/how-small")
        assert record["title"] == "How Small"
        assert record["date"] == "2026-06-22"

    def test_missing_date_is_empty(self, monkeypatch):
        """A landing page lacking a date meta tag resolves to an empty date."""

        def _request(url, *args, **kwargs):
            """Serve a landing page with a PDF but no date meta tag."""
            if url.endswith("/research/working-papers/how-small"):
                return _html_response(
                    '<meta name="title" content="How Small | Minneapolis"/>'
                    '<a href="/research/wp/wp815.pdf">PDF</a>'
                )
            return _make_request(url, *args, **kwargs)

        monkeypatch.setattr("openbb_core.provider.utils.helpers.make_request", _request)
        record = mp._resolve_landing("/research/working-papers/how-small")
        assert record["date"] == ""


class TestListPublications:
    """Tests for the merged catalog."""

    def test_all_series_merged_newest_first(self):
        """With no series filter every series merges, newest first, skipping no-PDF."""
        catalog = mp.list_publications()
        assert len(catalog) == 5
        series = {r["series"] for r in catalog}
        assert series == {
            "working_paper",
            "institute_working_paper",
            "cicd_working_paper",
            "staff_report",
            "quarterly_review",
        }
        assert catalog == sorted(catalog, key=lambda r: r["date"], reverse=True)

    def test_series_filter(self):
        """A series filter narrows the catalog to that series."""
        catalog = mp.list_publications("quarterly_review")
        assert [r["series"] for r in catalog] == ["quarterly_review"]
        assert catalog[0]["url"].endswith("qr4612.pdf")


class TestFetchPublicationPdf:
    """Tests for ``fetch_publication_pdf``."""

    def test_downloads_and_encodes(self):
        """A direct URL downloads and base64-encodes the PDF."""
        out = mp.fetch_publication_pdf("https://x/research/wp/wp815.pdf")
        assert out["data_format"]["filename"] == "wp815.pdf"
        assert out["data_format"]["data_type"] == "pdf"
        assert base64.b64decode(out["content"]).startswith(b"%PDF")


class TestPublicationsIndexModel:
    """Tests for the discovery index data model."""

    _CATALOG = [
        {
            "series": "working_paper",
            "id": "how-small",
            "date": "2026-06-22",
            "title": "How Small",
            "url": "https://x/wp815.pdf",
            "authors": "Javier Bianchi",
        },
        {
            "series": "staff_report",
            "id": "occupational-licensing",
            "date": "2026-06-12",
            "title": "Occupational Licensing",
            "url": "https://x/sr667.pdf",
            "authors": None,
        },
        {
            "series": "quarterly_review",
            "id": "trade-in-ai",
            "date": "2025-01-01",
            "title": "Trade in AI",
            "url": "https://x/qr4612.pdf",
            "authors": None,
        },
    ]

    def _patch(self, monkeypatch):
        """Point the index model at a synthetic catalog."""
        monkeypatch.setattr(
            mp, "list_publications", lambda series=None: list(self._CATALOG)
        )

    def test_filters_start_and_end_date(self, monkeypatch):
        """The start_date and end_date filters narrow the catalog."""
        self._patch(monkeypatch)
        query = FederalReserveMinneapolisPublicationsFetcher.transform_query(
            {"start_date": "2026-01-01", "end_date": "2026-06-15"}
        )
        rows = FederalReserveMinneapolisPublicationsFetcher.transform_data(
            query,
            FederalReserveMinneapolisPublicationsFetcher.extract_data(query, None),
        )
        assert all(
            isinstance(r, FederalReserveMinneapolisPublicationsData) for r in rows
        )
        assert [r.title for r in rows] == ["Occupational Licensing"]
        assert rows[0].date == date(2026, 6, 12)
        assert not hasattr(rows[0], "id")

    def test_no_filter_returns_all(self, monkeypatch):
        """With no filters the full catalog is returned."""
        self._patch(monkeypatch)
        query = FederalReserveMinneapolisPublicationsFetcher.transform_query({})
        rows = FederalReserveMinneapolisPublicationsFetcher.transform_data(
            query,
            FederalReserveMinneapolisPublicationsFetcher.extract_data(query, None),
        )
        assert len(rows) == 3

    def test_empty_raises(self, monkeypatch):
        """An empty catalog raises ``EmptyDataError``."""
        monkeypatch.setattr(mp, "list_publications", lambda series=None: [])
        query = FederalReserveMinneapolisPublicationsFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveMinneapolisPublicationsFetcher.extract_data(query, None)


class TestPublicationsChoices:
    """Tests for the shared regional_publications_choices contract."""

    @pytest.mark.asyncio
    async def test_choices_carry_urls(self):
        """The choices endpoint surfaces each publication with its PDF url."""
        from openbb_federal_reserve.federal_reserve_router import (
            regional_publications_choices,
        )

        choices = await regional_publications_choices("minneapolis")
        assert len(choices) == 5
        assert all(choice["value"].endswith(".pdf") for choice in choices)
        assert all("(" in choice["label"] for choice in choices)
