"""Tests for the USDA FAS Bell Report utils and model."""

import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.bell_report import (
    FasBellReportFetcher,
    FasBellReportQueryParams,
)
from openbb_government_us.usda.utils import fas_bell_report as B


class TestYearAgoDate:
    """Tests for the year-ago derivation."""

    def test_preserves_weekday(self):
        """The year-ago date is 52 weeks back and lands on the same weekday."""
        wed = date(2026, 7, 9)
        ago = B.year_ago_date(wed)
        assert ago == date(2025, 7, 10)
        assert ago.weekday() == wed.weekday()

    def test_not_365_days(self):
        """Subtracting a calendar year would shift the weekday and is wrong."""
        assert B.year_ago_date(date(2026, 7, 9)) != date(2025, 7, 9)


class TestFormatDate:
    """Tests for the report's date format."""

    def test_month_day_year(self):
        """Dates render as MM/DD/YYYY, the only format the report accepts."""
        assert B.format_date(date(2026, 7, 9)) == "07/09/2026"
        assert B.format_date(date(2026, 12, 31)) == "12/31/2026"


class TestBuildReportUrl:
    """Tests for the report session URL."""

    def test_my1_sends_year_ago_and_id_based_cid(self):
        """MY1 carries YGO, and CID uses commodity ids with a trailing comma."""
        url = B.build_report_url("my1", date(2026, 7, 9), date(2026, 7, 16), [1])
        assert "RN=BR" in url
        assert "wed=07%2F09%2F2026" in url
        assert "YGO=07%2F10%2F2025" in url
        assert "RD=07%2F16%2F2026" in url
        assert "MY=N" in url
        assert "CID=1%2C" in url
        assert "AppUserId=0" in url

    def test_my2_and_my3_omit_year_ago(self):
        """Only MY1 takes the year-ago param."""
        for report, name in [("my2", "BRMY2"), ("my3", "BRMY3")]:
            url = B.build_report_url(report, date(2026, 7, 9), date(2026, 7, 16), [1])
            assert f"RN={name}" in url
            assert "YGO" not in url

    def test_multiple_commodities_each_get_a_trailing_comma(self):
        """Each commodity id is suffixed with a comma."""
        url = B.build_report_url("my1", date(2026, 7, 9), date(2026, 7, 16), [1, 12])
        assert "CID=1%2C12%2C" in url


class TestReportFromUrl:
    """Tests for reading a report back out of its URL."""

    def test_each_marketing_year_round_trips(self):
        """A URL built for a report resolves back to that report."""
        for report in ("my1", "my2", "my3"):
            url = B.build_report_url(report, date(2026, 7, 9), date(2026, 7, 16), [1])
            assert B.report_from_url(url) == report

    def test_foreign_host_raises(self):
        """Only the FAS report viewer is fetched, so other hosts are rejected."""
        with pytest.raises(OpenBBError, match="Invalid Bell Report URL"):
            B.report_from_url("https://evil.example.com/esrqs/ReportsHome.aspx?RN=BR")

    def test_other_path_on_the_same_host_raises(self):
        """A FAS URL that is not the report viewer is rejected."""
        with pytest.raises(OpenBBError, match="Invalid Bell Report URL"):
            B.report_from_url(f"https://{B.REPORT_HOST}/esrqs/api/lookups/Commodities")

    def test_unknown_report_name_raises(self):
        """A report name the viewer does not publish is rejected."""
        with pytest.raises(OpenBBError, match="Unknown Bell Report"):
            B.report_from_url(f"{B.BASE_URL}ReportsHome.aspx?RN=NOPE")


class TestReportFileName:
    """Tests for the downloaded file's name."""

    def test_names_the_report_commodities_and_week(self):
        """The file name is derived entirely from the URL."""
        url = B.build_report_url("my2", date(2026, 7, 9), date(2026, 7, 16), [1, 12])
        assert B.report_file_name(url) == "bell_report_my2_1_12_07092026.pdf"


class TestBuildExportUrl:
    """Tests for the report viewer export URL."""

    def test_carries_session_control_and_pdf_format(self):
        """The export URL requests a PDF for the given session."""
        url = B.build_export_url("SESS1", "CTRL1", "BellMY1")
        assert "ReportSession=SESS1" in url
        assert "ControlID=CTRL1" in url
        assert "OpType=Export" in url
        assert "Format=PDF" in url


class TestGetToken:
    """Tests for the anonymous token."""

    def setup_method(self):
        """Clear the cached token."""
        B._TOKEN.clear()

    def teardown_method(self):
        """Clear the cached token."""
        B._TOKEN.clear()

    def test_posts_public_client_credentials(self, monkeypatch):
        """The token is minted with the app's public client credentials."""
        captured: dict = {}

        async def fake_request(url, method="GET", **kwargs):
            captured["url"] = url
            captured["method"] = method
            captured["data"] = kwargs.get("data")
            return {"access_token": "TOK", "expires_in": 50399}

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", fake_request
        )
        assert asyncio.run(B.get_token()) == "TOK"
        assert captured["url"] == B.TOKEN_URL
        assert captured["method"] == "POST"
        assert "client_id=eAuth_Client" in captured["data"]
        assert "grant_type=client_credentials" in captured["data"]

    def test_caches_until_expiry(self, monkeypatch):
        """A cached token is reused without another request."""
        calls: list = []

        async def fake_request(url, method="GET", **kwargs):
            calls.append(url)
            return {"access_token": "TOK", "expires_in": 50399}

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", fake_request
        )
        asyncio.run(B.get_token())
        asyncio.run(B.get_token())
        assert len(calls) == 1

    def test_bad_response_raises(self, monkeypatch):
        """A response without an access token raises."""

        async def fake_request(url, method="GET", **kwargs):
            return {"error": "nope"}

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", fake_request
        )
        with pytest.raises(OpenBBError, match="token request failed"):
            asyncio.run(B.get_token())


class TestLookups:
    """Tests for the API lookups."""

    def test_commodities_map_code_to_id(self, monkeypatch):
        """The lookup exposes both the published code and the report's id."""

        async def fake_lookup(path, authorize=True, timeout=120):
            assert path == "lookups/Commodities"
            assert authorize is False
            return [
                {
                    "id": 12,
                    "commodityCode": 401,
                    "commodityName": "CORN  ",
                },
                {
                    "id": 1,
                    "commodityCode": 101,
                    "commodityName": "WHEAT - HARD RED WINTER",
                },
            ]

        monkeypatch.setattr(B, "get_lookup", fake_lookup)
        rows = asyncio.run(B.get_commodities())
        assert rows[0] == {
            "id": 1,
            "commodity_code": 101,
            "commodity_name": "WHEAT - HARD RED WINTER",
        }
        assert rows[1]["commodity_name"] == "CORN"

    def test_published_weeks_exclude_unpublished(self, monkeypatch):
        """Weeks that are not published are never offered."""

        async def fake_lookup(path, authorize=True, timeout=120):
            return [
                {
                    "weekEndingDate": "2026-07-02T00:00:00",
                    "weekEndingDateStatusId": 2,
                    "publishedDatetime": "2026-07-09T08:30:00",
                },
                {
                    "weekEndingDate": "2026-07-09T00:00:00",
                    "weekEndingDateStatusId": 2,
                    "publishedDatetime": "2026-07-16T08:30:00",
                },
                {
                    "weekEndingDate": "2026-07-16T00:00:00",
                    "weekEndingDateStatusId": 0,
                    "publishedDatetime": None,
                },
            ]

        monkeypatch.setattr(B, "get_lookup", fake_lookup)
        weeks = asyncio.run(B.get_published_weeks())
        assert [w["week_ending"] for w in weeks] == [date(2026, 7, 9), date(2026, 7, 2)]

    def test_get_lookup_attaches_bearer_token(self, monkeypatch):
        """Authorized lookups carry the bearer token."""
        captured: dict = {}

        async def fake_request(url, **kwargs):
            captured.update(url=url, headers=kwargs.get("headers"))
            return []

        async def fake_token():
            return "TOK"

        monkeypatch.setattr(B, "get_token", fake_token)
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", fake_request
        )
        asyncio.run(B.get_lookup("lookups/X"))
        assert captured["headers"]["Authorization"] == "Bearer TOK"

    def test_get_lookup_public_skips_token(self, monkeypatch):
        """Public lookups do not request a token."""

        async def fake_request(url, **kwargs):
            assert "Authorization" not in kwargs["headers"]
            return []

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", fake_request
        )
        asyncio.run(B.get_lookup("lookups/Commodities", authorize=False))


class TestGetSession:
    """Tests for the session accessor."""

    def test_delegates_to_the_platform_session(self, monkeypatch):
        """The report fetch uses a platform session that keeps cookies."""

        async def fake_session():
            return "session"

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.get_async_requests_session",
            fake_session,
        )
        assert asyncio.run(B._get_session()) == "session"


class _FakeResponse:
    """Mirrors the platform session's response, whose readers are awaited."""

    def __init__(self, text=None, body=None):
        self._text = text
        self._body = body

    async def text(self):
        return self._text

    async def read(self):
        return self._body


class _FakeSession:
    """Mirrors the platform session, whose get() is a coroutine, not a manager."""

    def __init__(self, html, pdf):
        self.html = html
        self.pdf = pdf
        self.urls: list = []
        self.closed = False

    async def get(self, url, **kwargs):
        self.urls.append(url)
        if "ReportsHome" in url:
            return _FakeResponse(text=self.html)
        return _FakeResponse(body=self.pdf)

    async def close(self):
        self.closed = True


class TestAfetchReport:
    """Tests for the two-step report fetch."""

    HTML = "x ReportSession=SESS1 y ControlID=CTRL1 z"
    URL = B.build_report_url("my1", date(2026, 7, 9), date(2026, 7, 16), [1])

    def _patch(self, monkeypatch, html, pdf):
        session = _FakeSession(html, pdf)

        async def fake_get_session():
            return session

        monkeypatch.setattr(B, "_get_session", fake_get_session)
        return session

    def test_returns_pdf_bytes(self, monkeypatch):
        """A successful fetch opens a session then exports the PDF."""
        session = self._patch(monkeypatch, self.HTML, b"%PDF-1.4 data")
        content = asyncio.run(B.afetch_report(self.URL))
        assert content == b"%PDF-1.4 data"
        assert "ReportsHome.aspx" in session.urls[0]
        assert "Reserved.ReportViewerWebControl.axd" in session.urls[1]
        assert "ReportSession=SESS1" in session.urls[1]
        assert session.closed is True

    def test_rejects_a_foreign_url_before_fetching(self, monkeypatch):
        """A URL outside the report viewer never reaches the network."""
        session = self._patch(monkeypatch, self.HTML, b"%PDF")
        with pytest.raises(OpenBBError, match="Invalid Bell Report URL"):
            asyncio.run(B.afetch_report("https://evil.example.com/ReportsHome.aspx"))
        assert session.urls == []

    def test_missing_session_raises(self, monkeypatch):
        """Failing to open a report session raises."""
        self._patch(monkeypatch, "no ids here", b"%PDF")
        with pytest.raises(OpenBBError, match="did not open a session"):
            asyncio.run(B.afetch_report(self.URL))

    def test_non_pdf_raises(self, monkeypatch):
        """A response that is not a PDF raises rather than returning junk."""
        self._patch(monkeypatch, self.HTML, b"<html>error</html>")
        with pytest.raises(OpenBBError, match="not a PDF"):
            asyncio.run(B.afetch_report(self.URL))

    def test_session_is_closed_when_the_fetch_fails(self, monkeypatch):
        """A failed fetch still releases the session."""
        session = self._patch(monkeypatch, "no ids here", b"%PDF")
        with pytest.raises(OpenBBError):
            asyncio.run(B.afetch_report(self.URL))
        assert session.closed is True


class TestFasBellReport:
    """Tests for the FasBellReport model."""

    URL_MY1 = B.build_report_url("my1", date(2026, 7, 9), date(2026, 7, 16), [1])
    URL_MY2 = B.build_report_url("my2", date(2026, 7, 9), date(2026, 7, 16), [1, 12])

    def test_urls_are_required(self):
        """A request without a file selection is rejected."""
        with pytest.raises(ValueError, match="urls"):
            FasBellReportQueryParams()

    def test_multiple_items_are_allowed_for_urls(self):
        """The Workspace reads the multi-file contract off the schema."""
        assert FasBellReportQueryParams.__json_schema_extra__["urls"] == {
            "multiple_items_allowed": True
        }

    @staticmethod
    def _patch(monkeypatch, pdf=b"%PDF-1.4 report"):
        requested: list = []

        async def fake_fetch(url):
            requested.append(url)
            if isinstance(pdf, Exception):
                raise pdf
            return pdf

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.fas_bell_report.afetch_report",
            fake_fetch,
        )
        return requested

    @staticmethod
    def _fetch(urls, monkeypatch, pdf=b"%PDF-1.4 report"):
        requested = TestFasBellReport._patch(monkeypatch, pdf)
        query = FasBellReportFetcher.transform_query({"urls": urls})
        raw = asyncio.run(FasBellReportFetcher.aextract_data(query, None))
        return requested, FasBellReportFetcher.transform_data(query, raw)

    def test_urls_accepts_a_list(self, monkeypatch):
        """Each URL in a list is downloaded."""
        requested, results = self._fetch([self.URL_MY1, self.URL_MY2], monkeypatch)
        assert requested == [self.URL_MY1, self.URL_MY2]
        assert len(results) == 2

    def test_urls_accepts_a_comma_separated_string(self, monkeypatch):
        """A single string of URLs is split and whitespace is trimmed."""
        requested, results = self._fetch(
            f" {self.URL_MY1} , {self.URL_MY2} ", monkeypatch
        )
        assert requested == [self.URL_MY1, self.URL_MY2]
        assert len(results) == 2

    def test_urls_accepts_the_workspace_dict_form(self, monkeypatch):
        """The Workspace posts the file selection as a dict."""
        requested, results = self._fetch({"urls": [self.URL_MY1]}, monkeypatch)
        assert requested == [self.URL_MY1]
        assert len(results) == 1

    def test_encodes_the_pdf_with_a_descriptive_filename(self, monkeypatch):
        """The PDF is base64 encoded and named after the report it addresses."""
        import base64

        _, results = self._fetch([self.URL_MY2], monkeypatch)
        row = results[0]
        assert base64.b64decode(row.content) == b"%PDF-1.4 report"
        assert row.error_type is None
        assert row.filename == "bell_report_my2_1_12_07092026.pdf"
        assert row.data_format == {
            "data_type": "pdf",
            "filename": "bell_report_my2_1_12_07092026.pdf",
        }

    def test_an_invalid_url_reports_without_downloading(self, monkeypatch):
        """A URL the viewer does not serve is reported, not fetched."""
        requested, results = self._fetch(
            ["https://evil.example.com/ReportsHome.aspx"], monkeypatch
        )
        assert requested == []
        assert results[0].error_type == "invalid_url"
        assert results[0].filename is None
        assert "Invalid Bell Report URL" in results[0].content

    def test_a_download_failure_reports_that_url_only(self, monkeypatch):
        """One failed report does not discard the reports that succeeded."""
        calls: list = []

        async def fake_fetch(url):
            calls.append(url)
            if url == self.URL_MY1:
                raise OpenBBError("the FAS report viewer returned 0 bytes")
            return b"%PDF-1.4 report"

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.fas_bell_report.afetch_report",
            fake_fetch,
        )
        query = FasBellReportFetcher.transform_query(
            {"urls": [self.URL_MY1, self.URL_MY2]}
        )
        raw = asyncio.run(FasBellReportFetcher.aextract_data(query, None))
        results = FasBellReportFetcher.transform_data(query, raw)
        assert calls == [self.URL_MY1, self.URL_MY2]
        assert results[0].error_type == "download_error"
        assert results[0].filename == "bell_report_my1_1_07092026.pdf"
        assert "returned 0 bytes" in results[0].content
        assert results[1].error_type is None
