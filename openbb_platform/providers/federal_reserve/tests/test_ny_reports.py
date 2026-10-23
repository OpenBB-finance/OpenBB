"""Tests for the NY Fed survey report (PDF) helpers and commands."""

import base64
from unittest.mock import MagicMock

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_federal_reserve.utils import ny_reports

_OVERVIEW = (
    '<a href="/medialibrary/media/survey/business_leaders/2026/'
    '202606-blsreport.pdf?sc_lang=en&amp;hash=ABC">x</a>'
    '<a href="/medialibrary/media/survey/business_leaders/2026/'
    '202605-blsreport.pdf?hash=DEF">y</a>'
)


def _make_request(url, *args, **kwargs):
    """Path-aware fake: overview HTML for the survey page, PDF bytes otherwise."""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    if url.endswith("bls_overview"):
        response.text = _OVERVIEW
    else:
        response.content = b"%PDF-1.7 fake report"
    return response


class TestListReports:
    """Tests for ``list_business_leaders_reports``."""

    def test_lists_periods_newest_first(self, monkeypatch):
        """Report periods parse from the overview page, newest first."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        reports = ny_reports.list_business_leaders_reports()
        assert [r["period"] for r in reports] == ["202606", "202605"]
        assert reports[0]["url"].startswith("https://www.newyorkfed.org/medialibrary")


class TestFetchReport:
    """Tests for ``fetch_business_leaders_report``."""

    def test_latest(self, monkeypatch):
        """The latest report downloads as a base64 PDF payload."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        out = ny_reports.fetch_business_leaders_report()
        assert out["data_format"]["data_type"] == "pdf"
        assert out["data_format"]["filename"] == "NY_BLS_202606.pdf"
        assert base64.b64decode(out["content"]).startswith(b"%PDF")

    def test_specific_period(self, monkeypatch):
        """A requested period selects that report."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        out = ny_reports.fetch_business_leaders_report("202605")
        assert out["data_format"]["filename"] == "NY_BLS_202605.pdf"

    def test_unknown_period_raises(self, monkeypatch):
        """A missing period raises ``OpenBBError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        with pytest.raises(OpenBBError):
            ny_reports.fetch_business_leaders_report("999999")

    def test_no_reports_raises(self, monkeypatch):
        """No discovered reports raises ``OpenBBError``."""
        monkeypatch.setattr(ny_reports, "list_business_leaders_reports", list)
        with pytest.raises(OpenBBError):
            ny_reports.fetch_business_leaders_report()
