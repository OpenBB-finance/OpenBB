"""Unit tests for the FOMC document utility helpers."""

# ruff: noqa: I001

import pytest

import openbb_federal_reserve.utils.fomc_documents as mod
from openbb_federal_reserve.utils.fomc_documents import (
    FomcDocumentType,
    get_fomc_documents_by_year,
    load_historical_fomc_documents,
)

FAKE_CURRENT = [
    {"date": "2025-02-01", "doc_type": "beige_book", "doc_format": "htm", "url": "u2"},
    {"date": "2025-01-29", "doc_type": "minutes", "doc_format": "pdf", "url": "u1"},
]
FAKE_HISTORICAL = [
    {"date": "2024-12-18", "doc_type": "projections", "doc_format": "htm", "url": "h1"},
    {"date": "2024-06-14", "doc_type": "minutes", "doc_format": "pdf", "url": "h2"},
    {"date": "2023-06-14", "doc_type": "minutes", "doc_format": "pdf", "url": "h3"},
]


def _by_year(monkeypatch):
    """Patch the cached dependencies and return the un-cached helper."""
    monkeypatch.setattr(mod, "get_current_fomc_documents", lambda *a, **k: FAKE_CURRENT)
    monkeypatch.setattr(
        mod, "load_historical_fomc_documents", lambda *a, **k: FAKE_HISTORICAL
    )
    return get_fomc_documents_by_year.__wrapped__


class TestLoadHistoricalFomcDocuments:
    """Tests for ``load_historical_fomc_documents``."""

    def test_reads_local_assets(self):
        """The loader reads the on-disk ``historical_releases.json`` asset."""
        docs = load_historical_fomc_documents()
        assert isinstance(docs, list)
        assert docs
        assert set(docs[0]) == {"date", "doc_type", "doc_format", "url"}


class TestGetFomcDocumentsByYearValidation:
    """Tests for the validation branches of ``get_fomc_documents_by_year``."""

    def test_year_before_1959_raises(self, monkeypatch):
        """A year earlier than 1959 raises ``ValueError``."""
        by_year = _by_year(monkeypatch)
        with pytest.raises(ValueError, match="Year must be from 1959."):
            by_year(1900)

    def test_invalid_document_type_raises(self, monkeypatch):
        """An unknown ``document_type`` raises ``ValueError``."""
        by_year = _by_year(monkeypatch)
        with pytest.raises(ValueError, match="Invalid document type"):
            by_year(2024, "not_a_type")

    def test_document_type_must_be_known_literal(self, monkeypatch):
        """The error message lists the valid document-type choices."""
        by_year = _by_year(monkeypatch)
        with pytest.raises(ValueError, match="monetary_policy"):
            by_year(None, "bogus")

    def test_digit_string_year_is_coerced(self, monkeypatch):
        """A numeric string year is coerced to an int and filtered normally."""
        by_year = _by_year(monkeypatch)
        result = by_year("2024")
        assert result
        assert all(doc["date"].startswith("2024") for doc in result)

    def test_non_digit_string_year_raises(self, monkeypatch):
        """A non-numeric string year raises ``ValueError``."""
        by_year = _by_year(monkeypatch)
        with pytest.raises(ValueError, match="Year must be an integer."):
            by_year("abc")


class TestGetFomcDocumentsByYearSelection:
    """Tests for the source-selection and filtering branches."""

    def test_future_year_uses_current_source(self, monkeypatch):
        """A year past 2024 reads from the live (current) source."""
        by_year = _by_year(monkeypatch)
        out = by_year(2025)
        assert {d["url"] for d in out} == {"u1", "u2"}

    def test_past_year_uses_historical_source(self, monkeypatch):
        """A year up to 2024 reads from the historical source."""
        by_year = _by_year(monkeypatch)
        out = by_year(2024)
        assert {d["url"] for d in out} == {"h1", "h2"}

    def test_year_filter_drops_other_years(self, monkeypatch):
        """Documents whose year differs from the requested year are dropped."""
        by_year = _by_year(monkeypatch)
        out = by_year(2024)
        assert all(d["date"].startswith("2024") for d in out)
        assert "h3" not in {d["url"] for d in out}

    def test_no_year_concatenates_current_and_historical(self, monkeypatch):
        """When no year is given, current and historical sources are merged."""
        by_year = _by_year(monkeypatch)
        out = by_year(None)
        assert len(out) == len(FAKE_CURRENT) + len(FAKE_HISTORICAL)

    def test_default_document_type_is_all(self, monkeypatch):
        """A ``None`` document type defaults to returning every type."""
        by_year = _by_year(monkeypatch)
        out = by_year(None, None)
        assert {d["doc_type"] for d in out} == {"beige_book", "minutes", "projections"}

    def test_document_type_filter(self, monkeypatch):
        """A specific document type keeps only matching documents."""
        by_year = _by_year(monkeypatch)
        out = by_year(None, "minutes")
        assert out
        assert all(d["doc_type"] == "minutes" for d in out)

    def test_pdf_only_filter(self, monkeypatch):
        """``pdf_only`` drops non-PDF formats."""
        by_year = _by_year(monkeypatch)
        out = by_year(None, "all", True)
        assert out
        assert all(d["doc_format"] == "pdf" for d in out)

    def test_results_sorted_desc_by_date(self, monkeypatch):
        """Results are returned newest-first."""
        by_year = _by_year(monkeypatch)
        out = by_year(None)
        dates = [d["date"] for d in out]
        assert dates == sorted(dates, reverse=True)


class TestGetCurrentFomcDocuments:
    """Tests for the live HTML-scrape path of ``get_current_fomc_documents``."""

    HTML = (
        b"<html><body>"
        b'<a href="/monetarypolicy/files/monetary20250129a1.pdf">MP</a>'
        b'<a href="/monetarypolicy/fomcprojtabl20250129.htm">Proj</a>'
        b'<a href="/monetarypolicy/fomcminutes20250129.pdf">Min</a>'
        b'<a href="/monetarypolicy/fomcpresconf20250129.pdf">Conf</a>'
        b'<a href="/newsevents/pressreleases/monetary20250129a.htm">skip</a>'
        b'<a href="/monetarypolicy/beigebook20250115.htm">Beige</a>'
        b'<a href="/aboutthefed/structurefederalreserve.htm">NoDate</a>'
        b"</body></html>"
    )

    def _patch_request(self, monkeypatch):
        """Patch ``make_request`` to return the crafted HTML snippet."""
        from openbb_core.provider.utils import helpers

        class _Resp:
            content = self.HTML

        monkeypatch.setattr(helpers, "make_request", lambda *a, **k: _Resp())

    def test_parses_dates_types_and_formats(self, monkeypatch):
        """Anchors are parsed into typed, dated document dictionaries."""
        self._patch_request(monkeypatch)
        out = mod.get_current_fomc_documents.__wrapped__(
            url="https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
        )
        by_url = {d["url"].rsplit("/", 1)[-1]: d for d in out}

        assert by_url["monetary20250129a1.pdf"]["doc_type"] == "monetary_policy"
        assert by_url["monetary20250129a1.pdf"]["date"] == "2025-01-29"
        assert by_url["monetary20250129a1.pdf"]["doc_format"] == "pdf"
        assert by_url["fomcprojtabl20250129.htm"]["doc_type"] == "projections"
        assert by_url["fomcminutes20250129.pdf"]["doc_type"] == "minutes"
        assert by_url["fomcpresconf20250129.pdf"]["doc_type"] == "press_conference"
        assert by_url["beigebook20250115.htm"]["doc_type"] == "beige_book"

    def test_skips_press_release_and_dateless_links(self, monkeypatch):
        """Press-release links and links without a date are skipped."""
        self._patch_request(monkeypatch)
        out = mod.get_current_fomc_documents.__wrapped__(
            url="https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
        )
        urls = {d["url"] for d in out}
        assert not any("pressreleases" in u for u in urls)
        assert not any("structurefederalreserve" in u for u in urls)

    def test_prefixes_relative_urls(self, monkeypatch):
        """Relative hrefs are prefixed with the Federal Reserve domain."""
        self._patch_request(monkeypatch)
        out = mod.get_current_fomc_documents.__wrapped__(
            url="https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
        )
        assert all(d["url"].startswith("https://www.federalreserve.gov") for d in out)

    def test_results_sorted_desc_by_date(self, monkeypatch):
        """The scraped releases are sorted newest-first."""
        self._patch_request(monkeypatch)
        out = mod.get_current_fomc_documents.__wrapped__(
            url="https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
        )
        dates = [d["date"] for d in out]
        assert dates == sorted(dates, reverse=True)

    def test_default_url_prepends_beige_books(self, monkeypatch):
        """With no URL, beige books are fetched and prepended to the calendar scrape."""
        self._patch_request(monkeypatch)
        beige = [
            {
                "date": "2025-03-05",
                "doc_type": "beige_book",
                "doc_format": "pdf",
                "url": "https://www.federalreserve.gov/beige.pdf",
            }
        ]
        monkeypatch.setattr(mod, "get_beige_books", lambda *a, **k: beige)
        out = mod.get_current_fomc_documents.__wrapped__()
        assert "https://www.federalreserve.gov/beige.pdf" in {d["url"] for d in out}

    def test_default_url_handles_no_beige_books(self, monkeypatch):
        """An empty beige-book result is tolerated on the default-URL path."""
        self._patch_request(monkeypatch)
        monkeypatch.setattr(mod, "get_beige_books", lambda *a, **k: [])
        out = mod.get_current_fomc_documents.__wrapped__()
        assert out
        assert all("beige.pdf" not in d["url"] for d in out)


class TestGetBeigeBooks:
    """Tests for ``get_beige_books``."""

    def test_delegates_to_current_with_default_url(self, monkeypatch):
        """With no year, the default beige-book listing URL is requested."""
        seen: dict = {}

        def _fake(url=None):
            seen["url"] = url
            return [{"date": "2025-01-15", "doc_type": "beige_book"}]

        monkeypatch.setattr(mod, "get_current_fomc_documents", _fake)
        out = mod.get_beige_books()
        assert out and out[0]["doc_type"] == "beige_book"
        assert seen["url"].endswith("beige-book-default.htm")

    def test_year_builds_year_specific_url(self, monkeypatch):
        """A given year builds a year-specific beige-book URL."""
        seen: dict = {}

        def _fake(url=None):
            seen["url"] = url
            return []

        monkeypatch.setattr(mod, "get_current_fomc_documents", _fake)
        mod.get_beige_books(2020)
        assert seen["url"].endswith("beigebook2020.htm")


class TestFomcDocumentType:
    """Tests for the ``FomcDocumentType`` literal."""

    def test_includes_expected_members(self):
        """The literal exposes the documented document-type choices."""
        members = set(FomcDocumentType.__args__)
        assert {"all", "monetary_policy", "minutes", "beige_book"} <= members
