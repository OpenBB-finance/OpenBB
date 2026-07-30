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


class TestMarketExpectationsReports:
    """Tests for the Survey of Market Expectations PDF-catalog model."""

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
        """Point the catalog model at a synthetic PDF index."""
        monkeypatch.setattr(
            ny_surveys, "list_market_expectations", lambda: list(self._CATALOG)
        )

    def test_filters_kind_and_start_date(self, monkeypatch):
        """The kind and start_date filters narrow the catalog."""
        from openbb_federal_reserve.models.regional.new_york_market_expectations_reports import (  # noqa: E501
            FederalReserveNewYorkMarketExpectationsReportsData as DataModel,
            FederalReserveNewYorkMarketExpectationsReportsFetcher as Fetcher,
        )

        self._patch(monkeypatch)
        query = Fetcher.transform_query({"kind": "results", "start_date": "2026-02-01"})
        rows = Fetcher.transform_data(query, Fetcher.extract_data(query, None))
        assert all(isinstance(r, DataModel) for r in rows)
        assert [r.date for r in rows] == [date(2026, 4, 1)]
        assert rows[0].url.endswith("apr-results.pdf")

    def test_filters_end_date(self, monkeypatch):
        """The end_date filter narrows the catalog."""
        from openbb_federal_reserve.models.regional.new_york_market_expectations_reports import (  # noqa: E501
            FederalReserveNewYorkMarketExpectationsReportsFetcher as Fetcher,
        )

        self._patch(monkeypatch)
        query = Fetcher.transform_query({"end_date": "2026-01-31"})
        rows = Fetcher.transform_data(query, Fetcher.extract_data(query, None))
        assert [r.date for r in rows] == [date(2026, 1, 1)]

    def test_no_filter_returns_all(self, monkeypatch):
        """With no filters the full catalog is returned."""
        from openbb_federal_reserve.models.regional.new_york_market_expectations_reports import (  # noqa: E501
            FederalReserveNewYorkMarketExpectationsReportsFetcher as Fetcher,
        )

        self._patch(monkeypatch)
        query = Fetcher.transform_query({})
        rows = Fetcher.transform_data(query, Fetcher.extract_data(query, None))
        assert len(rows) == 3

    def test_empty_raises(self, monkeypatch):
        """An empty catalog raises ``EmptyDataError``."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_federal_reserve.models.regional.new_york_market_expectations_reports import (  # noqa: E501
            FederalReserveNewYorkMarketExpectationsReportsFetcher as Fetcher,
        )

        monkeypatch.setattr(ny_surveys, "list_market_expectations", list)
        query = Fetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            Fetcher.extract_data(query, None)


def _sme_data_workbook() -> bytes:
    """Build a Survey of Market Expectations results workbook."""
    import io
    from datetime import datetime

    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.append(
        [
            "survey_release_date",
            "survey_due_date",
            "panel_type",
            "spd_question_number",
            "theme",
            "subject_group",
            "subject",
            "question_type",
            "question_mode",
            "question_text",
            "question_tag",
            "value_tag",
            "top_header_value",
            "left_header_value",
            "horizon",
            "horizon_date",
            "bucket_range",
            "bucket_low",
            "bucket_high",
            "aggregation",
            "aggregation_value",
        ]
    )
    common = [
        "economic_outlook",
        "recession",
        "global_recession",
        "probability",
        "levels",
        "What percent chance of recession?",
        "globalrecession_prob_6months",
        "globalrecession_prob_6months",
        None,
        "the global economy being in a recession",
        "6months",
        datetime(2026, 10, 20),
        None,
        None,
        None,
    ]
    sheet.append(
        [datetime(2026, 4, 15), datetime(2026, 4, 20), "Combined", "10", *common]
        + ["pctl50", 0.30]
    )
    sheet.append(
        [datetime(2026, 4, 15), datetime(2026, 4, 20), "Dealer", "10", *common]
        + ["count", 62]
    )
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


_SME_WORKBOOK = _sme_data_workbook()


def _sme_make_request(url, *args, **kwargs):
    """Path-aware fake: data-file HTML for the survey page, workbook bytes otherwise."""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    if url.endswith("survey-of-market-expectations"):
        response.text = (
            '<a href="/medialibrary/media/markets/survey/2026/apr-2026-data.xlsx">x</a>'
            '<a href="/medialibrary/media/markets/survey/2026/mar-2026-data.xlsx">x</a>'
        )
    else:
        response.content = _SME_WORKBOOK
    return response


class TestListSmeDataUrls:
    """Tests for ``list_sme_data_urls``."""

    def test_scrapes_and_orders(self, monkeypatch):
        """Every data workbook link is returned, deduped in page order."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _sme_make_request
        )
        urls = ny_surveys.list_sme_data_urls()
        assert urls == [
            "https://www.newyorkfed.org/medialibrary/media/markets/survey"
            "/2026/apr-2026-data.xlsx",
            "https://www.newyorkfed.org/medialibrary/media/markets/survey"
            "/2026/mar-2026-data.xlsx",
        ]


class TestParseSmeWorkbook:
    """Tests for ``_parse_sme_workbook``."""

    def test_renames_and_types_columns(self):
        """Columns rename, dates and numbers coerce, and NA becomes None."""
        records = ny_surveys._parse_sme_workbook(_SME_WORKBOOK)
        assert len(records) == 2
        first = records[0]
        assert first["date"] == date(2026, 4, 15)
        assert first["survey_due_date"] == date(2026, 4, 20)
        assert first["question_number"] == "10"
        assert first["panel_type"] == "Combined"
        assert first["horizon_date"] == date(2026, 10, 20)
        assert first["aggregation"] == "pctl50"
        assert first["aggregation_value"] == 0.30
        assert first["top_header_value"] is None
        assert first["bucket_low"] is None


class TestFetchSmeData:
    """Tests for ``fetch_sme_data``."""

    def test_downloads_and_concatenates(self, monkeypatch):
        """Every workbook is downloaded, parsed, and merged newest first."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _sme_make_request
        )
        records = ny_surveys.fetch_sme_data()
        assert len(records) == 4
        assert all(r["date"] == date(2026, 4, 15) for r in records)
        assert {r["panel_type"] for r in records} == {"Combined", "Dealer"}

    def test_no_urls_returns_empty(self, monkeypatch):
        """When no workbooks are listed, the combined result is empty."""
        monkeypatch.setattr(ny_surveys, "list_sme_data_urls", list)
        assert ny_surveys.fetch_sme_data() == []


class TestMarketExpectationsData:
    """Tests for the Survey of Market Expectations data model."""

    def _records(self):
        """Return parsed synthetic survey records."""
        return ny_surveys._parse_sme_workbook(_SME_WORKBOOK)

    def test_panel_filter(self, monkeypatch):
        """The panel_type filter narrows to one respondent panel."""
        from openbb_federal_reserve.models.regional.new_york_market_expectations import (
            FederalReserveNewYorkMarketExpectationsData as DataModel,
            FederalReserveNewYorkMarketExpectationsFetcher as Fetcher,
        )

        monkeypatch.setattr(ny_surveys, "fetch_sme_data", self._records)
        query = Fetcher.transform_query({"panel_type": "Combined"})
        rows = Fetcher.transform_data(query, Fetcher.extract_data(query, None))
        assert all(isinstance(r, DataModel) for r in rows)
        assert [r.panel_type for r in rows] == ["Combined"]
        assert rows[0].aggregation_value == 0.30

    def test_date_filters(self, monkeypatch):
        """The start and end date filters narrow the releases."""
        from openbb_federal_reserve.models.regional.new_york_market_expectations import (
            FederalReserveNewYorkMarketExpectationsFetcher as Fetcher,
        )

        monkeypatch.setattr(ny_surveys, "fetch_sme_data", self._records)
        query = Fetcher.transform_query(
            {"start_date": "2026-04-01", "end_date": "2026-04-30"}
        )
        rows = Fetcher.transform_data(query, Fetcher.extract_data(query, None))
        assert len(rows) == 2

    def test_empty_raises(self, monkeypatch):
        """An empty download raises ``EmptyDataError``."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_federal_reserve.models.regional.new_york_market_expectations import (
            FederalReserveNewYorkMarketExpectationsFetcher as Fetcher,
        )

        monkeypatch.setattr(ny_surveys, "fetch_sme_data", list)
        query = Fetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            Fetcher.extract_data(query, None)

    def test_all_filtered_raises(self, monkeypatch):
        """A filter that removes every row raises ``EmptyDataError``."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_federal_reserve.models.regional.new_york_market_expectations import (
            FederalReserveNewYorkMarketExpectationsFetcher as Fetcher,
        )

        monkeypatch.setattr(ny_surveys, "fetch_sme_data", self._records)
        query = Fetcher.transform_query({"start_date": "2030-01-01"})
        with pytest.raises(EmptyDataError):
            Fetcher.transform_data(query, Fetcher.extract_data(query, None))
