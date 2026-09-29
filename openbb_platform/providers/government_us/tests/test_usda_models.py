"""Tests for the openbb_government_us USDA model modules."""

import asyncio
import base64
from datetime import datetime

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils import helpers as core_helpers
from pydantic import ValidationError

from openbb_government_us.usda.models.commodity_psd_data import (
    UsdaCommodityPsdData,
    UsdaCommodityPsdDataFetcher,
    UsdaCommodityPsdDataQueryParams,
)
from openbb_government_us.usda.models.weather_bulletin import (
    UsdaWeatherBulletinData,
    UsdaWeatherBulletinFetcher,
    UsdaWeatherBulletinQueryParams,
)
from openbb_government_us.usda.models.weather_bulletin_download import (
    UsdaWeatherBulletinDownloadData,
    UsdaWeatherBulletinDownloadFetcher,
    UsdaWeatherBulletinDownloadQueryParams,
)
from openbb_government_us.usda.utils import psd_data_downloader as downloader
from openbb_government_us.usda.utils.psd_codes import PSD_REPORT_NAMES


class _FakeBulletinResponse:
    """Awaitable-get response exposing a status and text body."""

    def __init__(self, status=200, body=""):
        self.status = status
        self._body = body

    async def text(self):
        """Return the canned HTML body."""
        return self._body


class _FakeBulletinSession:
    """Fake aiohttp session whose awaited get yields a fixed response."""

    def __init__(self, response=None, get_exc=None):
        self._response = response
        self._get_exc = get_exc
        self.requested = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def get(self, url):
        """Return the canned response (or raise)."""
        self.requested.append(url)
        if self._get_exc is not None:
            raise self._get_exc
        return self._response


class _FakeDownloadResponse:
    """Async context-manager response with a status and readable body."""

    def __init__(self, status=200, body=b""):
        self.status = status
        self._body = body

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def read(self):
        """Return the canned body bytes."""
        return self._body


class _FakeDownloadSession:
    """Fake aiohttp session whose awaited get yields a context-manager response."""

    def __init__(self, response):
        self._response = response
        self.requested = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def get(self, url):
        """Return the canned context-manager response."""
        self.requested.append(url)
        return self._response


def _patch_session(monkeypatch, session):
    """Point helpers.get_async_requests_session at the supplied fake session."""

    async def _get_session(**kwargs):
        return session

    monkeypatch.setattr(core_helpers, "get_async_requests_session", _get_session)


def _bulletin_html(entries):
    """Build publication-page HTML with PDF links and time tags."""
    parts = [
        f'<a href="{path}" class="lnk">Bulletin</a>'
        f'<time datetime="{stamp}T05:00:00Z">d</time>'
        for path, stamp in entries
    ]
    return "<html><body>" + "".join(parts) + "</body></html>"


class TestUsdaCommodityPsdData:
    """Tests for the commodity PSD data query params and fetcher."""

    def test_report_id_falsy_defaults(self):
        """An empty report_id falls back to the world crop production summary."""
        query = UsdaCommodityPsdDataQueryParams(report_id="")
        assert query.report_id == "world_crop_production_summary"

    def test_report_id_invalid_raises(self):
        """An unknown report_id raises a validation error."""
        with pytest.raises(ValidationError, match="Invalid report_id"):
            UsdaCommodityPsdDataQueryParams(report_id="bogus_report")

    def test_commodity_falsy_returns_none(self):
        """An empty commodity normalizes to None."""
        query = UsdaCommodityPsdDataQueryParams(commodity="")
        assert query.commodity is None

    def test_commodity_invalid_raises(self):
        """An unknown commodity raises a validation error."""
        with pytest.raises(ValidationError, match="Invalid commodity"):
            UsdaCommodityPsdDataQueryParams(commodity="unobtainium")

    def test_attribute_empty_string_returns_none(self):
        """An empty attribute normalizes to None."""
        query = UsdaCommodityPsdDataQueryParams(attribute="")
        assert query.attribute is None

    def test_attribute_empty_list_returns_none(self):
        """A list with an empty first item normalizes to None."""
        query = UsdaCommodityPsdDataQueryParams(attribute=[""])
        assert query.attribute is None

    def test_attribute_string_forms(self):
        """Single and comma-separated attribute strings become lists."""
        single = UsdaCommodityPsdDataQueryParams(attribute="production")
        assert single.attribute == ["production"]
        multi = UsdaCommodityPsdDataQueryParams(attribute="production,exports")
        assert multi.attribute == ["production", "exports"]

    def test_attribute_single_item_list_with_comma_splits(self):
        """A one-element list containing a comma is split into items."""
        query = UsdaCommodityPsdDataQueryParams(attribute=["production,exports"])
        assert query.attribute == ["production", "exports"]

    def test_attribute_wrong_type_raises(self):
        """A non-string non-list attribute raises a validation error."""
        with pytest.raises(ValidationError, match="string or list of strings"):
            UsdaCommodityPsdDataQueryParams(attribute=123)

    def test_attribute_invalid_raises(self):
        """An unknown attribute raises a validation error."""
        with pytest.raises(ValidationError, match="Invalid attribute"):
            UsdaCommodityPsdDataQueryParams(attribute="bogus_attr")

    def test_country_empty_string_returns_none(self):
        """An empty country normalizes to None."""
        query = UsdaCommodityPsdDataQueryParams(country="")
        assert query.country is None

    def test_country_empty_list_returns_none(self):
        """A list with an empty first item normalizes to None."""
        query = UsdaCommodityPsdDataQueryParams(country=[""])
        assert query.country is None

    def test_country_wrong_type_raises(self):
        """A non-string non-list country raises a validation error."""
        with pytest.raises(ValidationError, match="string or list of strings"):
            UsdaCommodityPsdDataQueryParams(country=123)

    def test_country_single_item_list_with_comma(self):
        """A one-element list containing a comma validates each code."""
        query = UsdaCommodityPsdDataQueryParams(country=["AF,AL"])
        assert query.country == ["AF,AL"]

    def test_country_invalid_raises(self):
        """An unknown country code raises a validation error."""
        with pytest.raises(ValidationError, match="Invalid country code"):
            UsdaCommodityPsdDataQueryParams(country="atlantis")

    def test_start_year_too_early_raises(self):
        """A start year before 1960 raises a validation error."""
        with pytest.raises(ValidationError, match="Earliest possible year is 1960"):
            UsdaCommodityPsdDataQueryParams(start_year=1900)

    def test_model_requires_report_or_commodity(self):
        """A model with neither report_id nor commodity fails validation."""
        query = UsdaCommodityPsdDataQueryParams.model_construct(
            report_id=None, commodity=None
        )
        with pytest.raises(ValueError, match="Either 'report_id' or 'commodity'"):
            query._validate_model()

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = UsdaCommodityPsdDataFetcher.transform_query({"commodity": "corn"})
        assert query.commodity == "corn"

    def test_aextract_timeseries_success(self, monkeypatch):
        """The commodity path delegates to get_timeseries with the query fields."""
        captured = {}

        def _fake_timeseries(**kwargs):
            captured.update(kwargs)
            return [{"commodity": "corn", "value": 1}]

        monkeypatch.setattr(downloader, "get_timeseries", _fake_timeseries)
        query = UsdaCommodityPsdDataQueryParams(
            commodity="corn",
            attribute="production",
            country="AF",
            aggregate_regions=True,
            start_year=2000,
            end_year=2020,
        )
        data = asyncio.run(UsdaCommodityPsdDataFetcher.aextract_data(query, None))
        assert data == [{"commodity": "corn", "value": 1}]
        assert captured == {
            "commodity": "corn",
            "attribute": ["production"],
            "country": "AF",
            "aggregate_region": True,
            "start_year": 2000,
            "end_year": 2020,
        }

    def test_year_columns_match_marketing_and_calendar_headers(self):
        """Year columns are detected for both marketing-year and calendar-year headers."""
        assert downloader._year_columns(
            ["commodity", "attribute", "country", "2023/2024", "2024/2025", "unit"]
        ) == ["2023/2024", "2024/2025"]
        assert downloader._year_columns(
            ["commodity", "attribute", "country", "2022", "2023", "unit Description"]
        ) == ["2022", "2023"]

    def test_aextract_timeseries_error_wraps(self, monkeypatch):
        """A ValueError from get_timeseries is wrapped in OpenBBError."""

        def _boom(**kwargs):
            raise ValueError("bad attribute for commodity")

        monkeypatch.setattr(downloader, "get_timeseries", _boom)
        query = UsdaCommodityPsdDataQueryParams(commodity="corn")
        with pytest.raises(OpenBBError, match="bad attribute for commodity"):
            asyncio.run(UsdaCommodityPsdDataFetcher.aextract_data(query, None))

    def test_aextract_report_success(self, monkeypatch):
        """The report path resolves the report_id and returns the data rows."""
        captured = {}

        async def _fake_report(report_id):
            captured["report_id"] = report_id
            return {"data": [{"country": "World", "value": 2}]}

        monkeypatch.setattr(downloader, "get_psd_report_data", _fake_report)
        query = UsdaCommodityPsdDataQueryParams()
        data = asyncio.run(UsdaCommodityPsdDataFetcher.aextract_data(query, None))
        assert data == [{"country": "World", "value": 2}]
        assert (
            captured["report_id"] == PSD_REPORT_NAMES["world_crop_production_summary"]
        )

    def test_aextract_report_no_data_raises(self, monkeypatch):
        """An empty report payload raises OpenBBError."""

        async def _fake_report(report_id):
            return {"data": []}

        monkeypatch.setattr(downloader, "get_psd_report_data", _fake_report)
        query = UsdaCommodityPsdDataQueryParams()
        with pytest.raises(OpenBBError, match="no data was returned"):
            asyncio.run(UsdaCommodityPsdDataFetcher.aextract_data(query, None))

    def test_aextract_report_error_field_raises(self, monkeypatch):
        """A report payload carrying an error message raises OpenBBError."""

        async def _fake_report(report_id):
            return {"data": [{"country": "World"}], "error": "parse failed"}

        monkeypatch.setattr(downloader, "get_psd_report_data", _fake_report)
        query = UsdaCommodityPsdDataQueryParams()
        with pytest.raises(OpenBBError, match="parse failed"):
            asyncio.run(UsdaCommodityPsdDataFetcher.aextract_data(query, None))

    def test_transform_data(self):
        """transform_data pivots the marketing-year observations into columns."""
        query = UsdaCommodityPsdDataQueryParams(commodity="corn")
        rows = [
            {
                "country": "Afghanistan",
                "commodity": "corn",
                "attribute": "Production",
                "marketing_year": "2024/25",
                "value": 3.5,
            },
            {
                "country": "Afghanistan",
                "commodity": "corn",
                "attribute": "Production",
                "marketing_year": "2025/26",
                "value": 4.0,
            },
        ]
        out = UsdaCommodityPsdDataFetcher.transform_data(query, rows)
        assert isinstance(out[0], UsdaCommodityPsdData)
        assert len(out) == 1
        dumped = out[0].model_dump()
        assert dumped["2024/25"] == 3.5
        assert dumped["2025/26"] == 4.0


class TestUsdaWeatherBulletin:
    """Tests for the weather bulletin query params and fetcher."""

    def test_year_before_1974_raises(self):
        """A year before 1974 raises a validation error."""
        with pytest.raises(ValidationError, match="not be before 1974"):
            UsdaWeatherBulletinQueryParams(year=1970)

    def test_year_in_future_raises(self):
        """A future year raises OpenBBError."""
        with pytest.raises(OpenBBError, match="cannot be in the future"):
            UsdaWeatherBulletinQueryParams(year=datetime.now().year + 1)

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = UsdaWeatherBulletinFetcher.transform_query({"year": 2024, "month": 3})
        assert query.year == 2024
        assert query.month == 3

    def test_aextract_filters_and_dedupes(self, monkeypatch):
        """Bad dates, wrong years, wrong months, and duplicates are filtered out."""
        html = _bulletin_html(
            [
                ("/sites/default/release-files/101/wwcb_1.pdf", "2024-03-05"),
                ("/sites/default/release-files/795708/wwcb.pdf", "2024-03-06"),
                ("/sites/default/release-files/102/wwcb_2.pdf", "2024-02-30"),
                ("/sites/default/release-files/103/wwcb_3.pdf", "2023-03-05"),
                ("/sites/default/release-files/104/wwcb_4.pdf", "2024-04-02"),
                ("/sites/default/release-files/105/wwcb_dup.pdf", "2024-03-05"),
                ("/sites/default/release-files/106/wwcb_5.pdf", "2024-03-12"),
            ]
        )
        session = _FakeBulletinSession(response=_FakeBulletinResponse(body=html))
        _patch_session(monkeypatch, session)
        query = UsdaWeatherBulletinQueryParams(year=2024, month=3)
        data = asyncio.run(UsdaWeatherBulletinFetcher.aextract_data(query))
        assert [b["date"].strftime("%Y-%m-%d") for b in data] == [
            "2024-03-12",
            "2024-03-05",
        ]
        assert data[0]["week_of_month"] == 2
        assert data[0]["filename"] == "wwcb_5.pdf"
        assert data[0]["pdf_url"] == (
            "https://esmis.nal.usda.gov/sites/default/release-files/106/wwcb_5.pdf"
        )
        assert data[1]["label"] == "Weekly Weather Bulletin - 2024-03-05"
        assert session.requested == [
            "https://esmis.nal.usda.gov/publication/weekly-weather-and-crop-bulletin?date=2024-03"
        ]

    def test_aextract_week_filter(self, monkeypatch):
        """A week filter keeps only bulletins from that week of the month."""
        html = _bulletin_html(
            [
                ("/sites/default/release-files/101/wwcb_1.pdf", "2024-03-05"),
                ("/sites/default/release-files/106/wwcb_5.pdf", "2024-03-12"),
            ]
        )
        session = _FakeBulletinSession(response=_FakeBulletinResponse(body=html))
        _patch_session(monkeypatch, session)
        query = UsdaWeatherBulletinQueryParams(year=2024, month=3, week=2)
        data = asyncio.run(UsdaWeatherBulletinFetcher.aextract_data(query))
        assert [b["day"] for b in data] == [12]

    def test_aextract_non_200_returns_empty(self, monkeypatch):
        """A non-200 publication page yields no bulletins."""
        session = _FakeBulletinSession(response=_FakeBulletinResponse(status=500))
        _patch_session(monkeypatch, session)
        query = UsdaWeatherBulletinQueryParams(year=2024, month=1)
        assert asyncio.run(UsdaWeatherBulletinFetcher.aextract_data(query)) == []

    def test_aextract_get_error_returns_empty(self, monkeypatch):
        """A request error for a month yields no bulletins."""
        session = _FakeBulletinSession(get_exc=RuntimeError("timeout"))
        _patch_session(monkeypatch, session)
        query = UsdaWeatherBulletinQueryParams(year=2024, month=1)
        assert asyncio.run(UsdaWeatherBulletinFetcher.aextract_data(query)) == []

    def test_aextract_session_error_raises(self, monkeypatch):
        """A session construction failure is wrapped in OpenBBError."""

        async def _boom(**kwargs):
            raise RuntimeError("session down")

        monkeypatch.setattr(core_helpers, "get_async_requests_session", _boom)
        query = UsdaWeatherBulletinQueryParams(year=2024, month=1)
        with pytest.raises(OpenBBError, match="session down"):
            asyncio.run(UsdaWeatherBulletinFetcher.aextract_data(query))

    def test_transform_data(self):
        """transform_data maps bulletins to label/value records."""
        query = UsdaWeatherBulletinQueryParams(year=2024)
        rows = [
            {
                "label": "Weekly Weather Bulletin - 2024-03-05",
                "pdf_url": "https://esmis.nal.usda.gov/sites/default/release-files/101/wwcb_1.pdf",
            }
        ]
        out = UsdaWeatherBulletinFetcher.transform_data(query, rows)
        assert isinstance(out[0], UsdaWeatherBulletinData)
        assert out[0].label == "Weekly Weather Bulletin - 2024-03-05"
        assert out[0].value.endswith("/101/wwcb_1.pdf")


class TestUsdaWeatherBulletinDownload:
    """Tests for the weather bulletin download query params and fetcher."""

    def test_transform_query_splits(self):
        """A comma-separated urls string becomes a list."""
        query = UsdaWeatherBulletinDownloadFetcher.transform_query(
            {
                "urls": "https://esmis.nal.usda.gov/a.pdf,https://esmis.nal.usda.gov/b.pdf"
            }
        )
        assert query.urls == [
            "https://esmis.nal.usda.gov/a.pdf",
            "https://esmis.nal.usda.gov/b.pdf",
        ]

    def test_aextract_rejects_foreign_domain(self):
        """A URL outside esmis.nal.usda.gov raises OpenBBError."""
        query = UsdaWeatherBulletinDownloadQueryParams(
            urls="https://example.com/file.pdf"
        )
        with pytest.raises(OpenBBError, match="esmis.nal.usda.gov"):
            asyncio.run(UsdaWeatherBulletinDownloadFetcher.aextract_data(query, None))

    def test_aextract_rejects_non_pdf(self):
        """A non-PDF URL raises OpenBBError."""
        query = UsdaWeatherBulletinDownloadQueryParams(
            urls="https://esmis.nal.usda.gov/file.txt"
        )
        with pytest.raises(OpenBBError, match="Only PDF documents"):
            asyncio.run(UsdaWeatherBulletinDownloadFetcher.aextract_data(query, None))

    def test_aextract_non_200_raises(self, monkeypatch):
        """A failed download status raises OpenBBError."""
        session = _FakeDownloadSession(_FakeDownloadResponse(status=404))
        _patch_session(monkeypatch, session)
        query = UsdaWeatherBulletinDownloadQueryParams(
            urls="https://esmis.nal.usda.gov/sites/default/release-files/101/wwcb.pdf"
        )
        with pytest.raises(OpenBBError, match="Status code: 404"):
            asyncio.run(UsdaWeatherBulletinDownloadFetcher.aextract_data(query, None))

    def test_aextract_success(self, monkeypatch):
        """A successful download returns the body keyed by URL."""
        url = "https://esmis.nal.usda.gov/sites/default/release-files/101/wwcb.pdf"
        session = _FakeDownloadSession(
            _FakeDownloadResponse(status=200, body=b"%PDF-1.7 body")
        )
        _patch_session(monkeypatch, session)
        query = UsdaWeatherBulletinDownloadQueryParams(urls=url)
        data = asyncio.run(
            UsdaWeatherBulletinDownloadFetcher.aextract_data(query, None)
        )
        assert data == {url: b"%PDF-1.7 body"}
        assert session.requested == [url]

    def test_transform_data(self):
        """transform_data base64-encodes each document with its filename."""
        url = "https://esmis.nal.usda.gov/sites/default/release-files/101/wwcb.pdf"
        query = UsdaWeatherBulletinDownloadQueryParams(urls=url)
        out = UsdaWeatherBulletinDownloadFetcher.transform_data(
            query, {url: b"%PDF-1.7 body"}
        )
        assert isinstance(out[0], UsdaWeatherBulletinDownloadData)
        assert base64.b64decode(out[0].content) == b"%PDF-1.7 body"
        assert out[0].data_format == {"data_type": "pdf", "filename": "wwcb.pdf"}
