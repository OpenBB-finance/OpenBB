"""Tests for the NY Fed Survey of Market Expectations helpers and commands."""

import base64
from datetime import date
from unittest.mock import MagicMock

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_federal_reserve.utils import ny_surveys

_SME_HTML = (
    '<a href="/medialibrary/media/markets/survey/2026/apr-2026-sme-results.pdf">x</a>'
    '<a href="/medialibrary/media/markets/survey/2026/apr-survey-sme.pdf">x</a>'
    '<a href="/medialibrary/media/markets/survey/2024/sep-survey-pd.pdf">x</a>'
    '<a href="/medialibrary/media/markets/survey/2024/sep-survey-mp.pdf">x</a>'
    '<a href="/medialibrary/media/markets/survey/2013/sept_survey.pdf">x</a>'
    '<a href="/medialibrary/media/markets/survey/2012/April.pdf">x</a>'
    '<a href="/medialibrary/media/markets/survey/2020/overview.pdf">x</a>'
)


def _make_request(url, *args, **kwargs):
    """Path-aware fake: landing HTML for the survey page, PDF bytes otherwise."""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    if url.endswith("survey-of-market-expectations"):
        response.text = _SME_HTML
    else:
        response.content = b"%PDF-1.7 fake survey"
    return response


class TestClassify:
    """Tests for the filename classifier."""

    def test_full_month_results(self):
        """A full month name with no kind token classifies as combined results."""
        record = ny_surveys._classify("2012", "April")
        assert record == {
            "date": "2012-04-01",
            "kind": "results",
            "subtype": "combined",
            "title": "April 2012 Results (Combined)",
        }

    def test_abbreviated_sept_questionnaire(self):
        """The four-letter 'sept' abbreviation resolves to September."""
        record = ny_surveys._classify("2013", "sept_survey")
        assert record["date"] == "2013-09-01"
        assert record["kind"] == "questionnaire"

    def test_primary_dealer_and_market_participant_subtypes(self):
        """The pd and mp tokens classify the respondent panel."""
        assert ny_surveys._classify("2024", "sep-survey-pd")["subtype"] == (
            "primary_dealers"
        )
        assert ny_surveys._classify("2024", "sep-survey-mp")["subtype"] == (
            "market_participants"
        )

    def test_no_month_returns_none(self):
        """A filename without a month is not classifiable."""
        assert ny_surveys._classify("2020", "overview") is None


class TestListMarketExpectations:
    """Tests for ``list_market_expectations``."""

    def test_classifies_dedups_and_sorts(self, monkeypatch):
        """The catalog classifies every link, skips unparseable, newest first."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        catalog = ny_surveys.list_market_expectations()
        keys = {(r["date"], r["kind"], r["subtype"]) for r in catalog}
        assert ("2026-04-01", "results", "combined") in keys
        assert ("2026-04-01", "questionnaire", "combined") in keys
        assert ("2024-09-01", "questionnaire", "primary_dealers") in keys
        assert ("2024-09-01", "questionnaire", "market_participants") in keys
        assert ("2013-09-01", "questionnaire", "combined") in keys
        assert ("2012-04-01", "results", "combined") in keys
        assert not any(r["date"] == "2020-01-01" for r in catalog)
        assert catalog == sorted(catalog, key=lambda r: r["date"], reverse=True)
        assert catalog[0]["url"].startswith("https://www.newyorkfed.org/medialibrary")


class TestFetchMarketExpectationsPdf:
    """Tests for ``fetch_market_expectations_pdf``."""

    def test_latest_results(self, monkeypatch):
        """The latest results report downloads as a base64 PDF payload."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        out = ny_surveys.fetch_market_expectations_pdf(kind="results")
        assert out["data_format"]["filename"] == "NY_SME_2026-04-01_results.pdf"
        assert base64.b64decode(out["content"]).startswith(b"%PDF")

    def test_specific_date_questionnaire(self, monkeypatch):
        """A requested month and kind select that report."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        out = ny_surveys.fetch_market_expectations_pdf(
            date="2024-09", kind="questionnaire"
        )
        assert out["data_format"]["filename"] == ("NY_SME_2024-09-01_questionnaire.pdf")

    def test_unknown_date_raises(self, monkeypatch):
        """A missing month raises ``OpenBBError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        with pytest.raises(OpenBBError):
            ny_surveys.fetch_market_expectations_pdf(date="1999-01", kind="results")

    def test_no_catalog_raises(self, monkeypatch):
        """An empty catalog raises ``OpenBBError``."""
        monkeypatch.setattr(ny_surveys, "list_market_expectations", list)
        with pytest.raises(OpenBBError):
            ny_surveys.fetch_market_expectations_pdf(kind="results")


class TestMarketExpectationsIndex:
    """Tests for the discovery index data model."""

    _CATALOG = [
        {
            "date": "2026-04-01",
            "kind": "results",
            "subtype": "combined",
            "title": "April 2026 Results (Combined)",
            "url": "https://x/apr-results.pdf",
        },
        {
            "date": "2026-04-01",
            "kind": "questionnaire",
            "subtype": "combined",
            "title": "April 2026 Questionnaire (Combined)",
            "url": "https://x/apr-survey.pdf",
        },
        {
            "date": "2026-01-01",
            "kind": "results",
            "subtype": "combined",
            "title": "January 2026 Results (Combined)",
            "url": "https://x/jan-results.pdf",
        },
    ]

    def _patch(self, monkeypatch):
        """Point the index model at a synthetic catalog."""
        monkeypatch.setattr(
            ny_surveys, "list_market_expectations", lambda: list(self._CATALOG)
        )

    def test_filters_kind_and_start_date(self, monkeypatch):
        """The kind and start_date filters narrow the catalog."""
        from openbb_federal_reserve.models.regional.new_york_market_expectations import (
            FederalReserveNewYorkMarketExpectationsData as DataModel,
            FederalReserveNewYorkMarketExpectationsFetcher as Fetcher,
        )

        self._patch(monkeypatch)
        query = Fetcher.transform_query({"kind": "results", "start_date": "2026-02-01"})
        rows = Fetcher.transform_data(query, Fetcher.extract_data(query, None))
        assert all(isinstance(r, DataModel) for r in rows)
        assert [r.date for r in rows] == [date(2026, 4, 1)]
        assert rows[0].url.endswith("apr-results.pdf")

    def test_filters_end_date(self, monkeypatch):
        """The end_date filter narrows the catalog."""
        from openbb_federal_reserve.models.regional.new_york_market_expectations import (
            FederalReserveNewYorkMarketExpectationsFetcher as Fetcher,
        )

        self._patch(monkeypatch)
        query = Fetcher.transform_query({"end_date": "2026-01-31"})
        rows = Fetcher.transform_data(query, Fetcher.extract_data(query, None))
        assert [r.date for r in rows] == [date(2026, 1, 1)]

    def test_no_filter_returns_all(self, monkeypatch):
        """With no filters the full catalog is returned."""
        from openbb_federal_reserve.models.regional.new_york_market_expectations import (
            FederalReserveNewYorkMarketExpectationsFetcher as Fetcher,
        )

        self._patch(monkeypatch)
        query = Fetcher.transform_query({})
        rows = Fetcher.transform_data(query, Fetcher.extract_data(query, None))
        assert len(rows) == 3

    def test_empty_raises(self, monkeypatch):
        """An empty catalog raises ``EmptyDataError``."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_federal_reserve.models.regional.new_york_market_expectations import (
            FederalReserveNewYorkMarketExpectationsFetcher as Fetcher,
        )

        monkeypatch.setattr(ny_surveys, "list_market_expectations", list)
        query = Fetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            Fetcher.extract_data(query, None)
