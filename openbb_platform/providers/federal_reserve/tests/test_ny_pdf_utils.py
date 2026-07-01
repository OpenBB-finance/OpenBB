"""Tests for the additional New York Fed PDF enumeration helpers and commands."""

import base64
from datetime import date
from unittest.mock import MagicMock

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.utils import ny_empire, ny_hhdc, ny_reports

_EMPIRE_ARCHIVES = (
    '<a href="/medialibrary/media/Survey/Empire/empire2025/'
    'ESMS_2025_12.pdf?sc_lang=en&amp;hash=ABC">x</a>'
    '<a href="/medialibrary/media/Survey/Empire/empire2025/'
    'esms_2025_11.pdf?hash=DEF">y</a>'
    '<a href="/medialibrary/media/survey/empire/2011/january2011.pdf">z</a>'
    '<a href="/medialibrary/media/survey/empire/seasonalc.pdf">noop</a>'
)
_HHDC_IFRAME = "<div>HHD_C_Report_2026Q1.xlsx HHDC_2026Q1.pdf HHDC_2025Q4.pdf</div>"
_SUPPLEMENTAL = (
    '<a href="/medialibrary/media/survey/business_leaders/2024/'
    '2024_05supplemental.pdf?sc_lang=en&amp;hash=ABC">x</a>'
    '<a href="/medialibrary/media/survey/business_leaders/2023/'
    '2023_11supplemental.pdf?hash=DEF">y</a>'
)


def _empire_request(url, *args, **kwargs):
    """Path-aware fake: archives HTML for the survey page, PDF bytes otherwise."""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    if url.endswith("empiresurvey_archives"):
        response.text = _EMPIRE_ARCHIVES
    else:
        response.content = b"%PDF-1.7 fake empire"
    return response


def _hhdc_request(url, *args, **kwargs):
    """Path-aware fake: iframe HTML for the report page, PDF bytes otherwise."""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    if url.endswith("hhdc-iframe"):
        response.text = _HHDC_IFRAME
    else:
        response.content = b"%PDF-1.7 fake hhdc"
    return response


def _supplemental_request(url, *args, **kwargs):
    """Path-aware fake: supplemental HTML for the page, PDF bytes otherwise."""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    if url.endswith("supplemental_survey_report"):
        response.text = _SUPPLEMENTAL
    else:
        response.content = b"%PDF-1.7 fake supp"
    return response


class TestEmpireClassify:
    """Tests for the Empire report filename classifier."""

    def test_underscore_numeric(self):
        """A ``YYYY_MM`` filename resolves to a period."""
        assert ny_empire._classify("ESMS_2025_12.pdf") == "202512"

    def test_month_word(self):
        """A month-name filename resolves to a period."""
        assert ny_empire._classify("january2011.pdf") == "201101"

    def test_unparseable_returns_none(self):
        """A filename with no resolvable month returns None."""
        assert ny_empire._classify("seasonalc.pdf") is None


class TestListEmpireStateReports:
    """Tests for ``list_empire_state_reports``."""

    def test_scrapes_dedups_and_sorts(self, monkeypatch):
        """The archives page classifies, dedups, and sorts newest first."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _empire_request
        )
        reports = ny_empire.list_empire_state_reports()
        assert [r["period"] for r in reports] == ["202512", "202511", "201101"]
        assert reports[0]["url"].startswith("https://www.newyorkfed.org/medialibrary")


class TestFetchEmpireStateReport:
    """Tests for ``fetch_empire_state_report``."""

    def test_latest(self, monkeypatch):
        """The latest report downloads as a base64 PDF payload."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _empire_request
        )
        out = ny_empire.fetch_empire_state_report()
        assert out["data_format"]["filename"] == "NY_ESMS_202512.pdf"
        assert base64.b64decode(out["content"]).startswith(b"%PDF")

    def test_specific_period(self, monkeypatch):
        """A requested period selects that report."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _empire_request
        )
        out = ny_empire.fetch_empire_state_report("202511")
        assert out["data_format"]["filename"] == "NY_ESMS_202511.pdf"

    def test_unknown_period_raises(self, monkeypatch):
        """A missing period raises ``OpenBBError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _empire_request
        )
        with pytest.raises(OpenBBError):
            ny_empire.fetch_empire_state_report("999999")

    def test_no_reports_raises(self, monkeypatch):
        """No discovered reports raises ``OpenBBError``."""
        monkeypatch.setattr(ny_empire, "list_empire_state_reports", list)
        with pytest.raises(OpenBBError):
            ny_empire.fetch_empire_state_report()


class TestEmpireReportsIndexModel:
    """Tests for the Empire State report index data model."""

    _CATALOG = [
        {"period": "202512", "url": "https://x/2025_12.pdf"},
        {"period": "202511", "url": "https://x/2025_11.pdf"},
        {"period": "202510", "url": "https://x/2025_10.pdf"},
    ]

    def test_filters_and_dates(self, monkeypatch):
        """The index model builds dated records and applies the start_date filter."""
        from openbb_federal_reserve.models.regional.new_york_empire_reports import (
            FederalReserveNewYorkEmpireReportsData as DataModel,
            FederalReserveNewYorkEmpireReportsFetcher as Fetcher,
        )

        monkeypatch.setattr(
            ny_empire, "list_empire_state_reports", lambda: list(self._CATALOG)
        )
        query = Fetcher.transform_query(
            {"start_date": "2025-11-01", "end_date": "2025-11-30"}
        )
        rows = Fetcher.transform_data(query, Fetcher.extract_data(query, None))
        assert all(isinstance(r, DataModel) for r in rows)
        assert [r.date for r in rows] == [date(2025, 11, 1)]

    def test_empty_raises(self, monkeypatch):
        """An empty catalog raises ``EmptyDataError``."""
        from openbb_federal_reserve.models.regional.new_york_empire_reports import (
            FederalReserveNewYorkEmpireReportsFetcher as Fetcher,
        )

        monkeypatch.setattr(ny_empire, "list_empire_state_reports", list)
        query = Fetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            Fetcher.extract_data(query, None)


class TestHouseholdDebtQuarters:
    """Tests for the HHDC quarter discovery helpers."""

    def test_lists_and_latest(self, monkeypatch):
        """The iframe lists quarters newest first and exposes the latest."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _hhdc_request
        )
        quarters = ny_hhdc.list_household_debt_quarters()
        assert quarters == ["2026Q1", "2025Q4"]
        assert ny_hhdc.latest_household_debt_quarter() == "2026Q1"

    def test_latest_no_quarters_raises(self, monkeypatch):
        """No discovered quarters raises ``OpenBBError``."""
        monkeypatch.setattr(ny_hhdc, "list_household_debt_quarters", list)
        with pytest.raises(OpenBBError):
            ny_hhdc.latest_household_debt_quarter()


class TestFetchHouseholdDebtReport:
    """Tests for ``fetch_household_debt_report``."""

    def test_latest(self, monkeypatch):
        """The latest report downloads as a base64 PDF payload."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _hhdc_request
        )
        out = ny_hhdc.fetch_household_debt_report()
        assert out["data_format"]["filename"] == "NY_HHDC_2026Q1.pdf"
        assert base64.b64decode(out["content"]).startswith(b"%PDF")

    def test_specific_quarter(self, monkeypatch):
        """A requested quarter selects that report without iframe discovery."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _hhdc_request
        )
        out = ny_hhdc.fetch_household_debt_report("2025Q4")
        assert out["data_format"]["filename"] == "NY_HHDC_2025Q4.pdf"


class TestSupplementalReports:
    """Tests for the Business Leaders Supplemental report helpers."""

    def test_lists_periods_newest_first(self, monkeypatch):
        """Supplemental periods parse from the page, newest first."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _supplemental_request
        )
        reports = ny_reports.list_business_leaders_supplemental_reports()
        assert [r["period"] for r in reports] == ["202405", "202311"]

    def test_fetch_latest(self, monkeypatch):
        """The latest supplemental report downloads as a base64 PDF payload."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _supplemental_request
        )
        out = ny_reports.fetch_business_leaders_supplemental_report()
        assert out["data_format"]["filename"] == "NY_BLS_Supplemental_202405.pdf"
        assert base64.b64decode(out["content"]).startswith(b"%PDF")

    def test_fetch_specific_period(self, monkeypatch):
        """A requested period selects that supplemental report."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _supplemental_request
        )
        out = ny_reports.fetch_business_leaders_supplemental_report("202311")
        assert out["data_format"]["filename"] == "NY_BLS_Supplemental_202311.pdf"

    def test_fetch_unknown_period_raises(self, monkeypatch):
        """A missing period raises ``OpenBBError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _supplemental_request
        )
        with pytest.raises(OpenBBError):
            ny_reports.fetch_business_leaders_supplemental_report("999999")

    def test_fetch_no_reports_raises(self, monkeypatch):
        """No discovered reports raises ``OpenBBError``."""
        monkeypatch.setattr(
            ny_reports, "list_business_leaders_supplemental_reports", list
        )
        with pytest.raises(OpenBBError):
            ny_reports.fetch_business_leaders_supplemental_report()
