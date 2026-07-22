"""USDA fetcher tests."""

import csv
import gzip
from io import StringIO

import pytest
from openbb_core.app.service.user_service import UserService

from openbb_government_us.usda.models.commodity_psd_data import (
    UsdaCommodityPsdDataFetcher,
)
from openbb_government_us.usda.models.dairy_data import DairyDataFetcher
from openbb_government_us.usda.models.major_land_uses import MajorLandUsesFetcher
from openbb_government_us.usda.models.milk_cost_of_production import (
    MilkCostOfProductionFetcher,
)
from openbb_government_us.usda.models.price_spreads import (
    FarmToConsumerPriceSpreadsFetcher,
)
from openbb_government_us.usda.models.report_calendar import FasReportCalendarFetcher
from openbb_government_us.usda.models.us_agricultural_trade import (
    UsAgriculturalTradeFetcher,
)
from openbb_government_us.usda.models.weather_bulletin import (
    UsdaWeatherBulletinFetcher,
)
from openbb_government_us.usda.models.weather_bulletin_download import (
    UsdaWeatherBulletinDownloadFetcher,
)

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


def _redact_binary_response(response: dict) -> dict:
    headers = response.get("headers", {})
    content_type_values = (
        headers.get("Content-Type") or headers.get("content-type") or []
    )
    content_type = " ".join(content_type_values).lower()
    content_encoding_values = (
        headers.get("Content-Encoding") or headers.get("content-encoding") or []
    )
    content_encoding = " ".join(content_encoding_values).lower()
    body = response.get("body", {})
    payload = body.get("string")
    if isinstance(payload, str):
        payload_bytes = payload.encode("utf-8", errors="ignore")
    else:
        payload_bytes = payload
    is_pdf = (
        "application/pdf" in content_type or "application/octet-stream" in content_type
    )
    if is_pdf and isinstance(payload_bytes, (bytes, bytearray)):
        body["string"] = b"%PDF-1.4\n%OpenBB VCR redacted binary body\n%%EOF\n"
        response["body"] = body
        return response

    if "text/csv" not in content_type or not isinstance(
        payload_bytes, (bytes, bytearray)
    ):
        return response

    decoded_bytes = bytes(payload_bytes)
    if "gzip" in content_encoding:
        try:
            decoded_bytes = gzip.decompress(decoded_bytes)
        except OSError:
            return response

    try:
        text = decoded_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        return response

    reader = csv.DictReader(StringIO(text))
    raw_fieldnames = reader.fieldnames
    if not raw_fieldnames:
        return response
    fieldnames = [name.strip() for name in raw_fieldnames]

    rows = [
        {((key or "").strip()): value for key, value in row.items()} for row in reader
    ]
    reduced_rows: list[dict[str, str]] | None = None

    if {"Year", "Region or State", "Land use", "Value"}.issubset(fieldnames):
        reduced_rows = []
        for row in rows:
            year_text = (row.get("Year") or "").strip()
            geography = (row.get("Region or State") or "").strip()
            try:
                year_value = int(year_text)
            except ValueError:
                continue
            if year_value >= 2010 and geography in {"48 States", "U.S. total"}:
                reduced_rows.append(row)

    elif {
        "Source_table",
        "Commodity",
        "Year",
        "Time_period",
        "US_Trade",
        "Value_type",
        "Value",
    }.issubset(fieldnames):
        reduced_rows = []
        target_table = "Top 10 U.S. export markets for soybeans, corn, wheat, and cotton, by volume"
        for row in rows:
            if (row.get("Source_table") or "").strip() != target_table:
                continue
            if (row.get("Commodity") or "").strip() != "Corn":
                continue
            if (row.get("Country") or "").strip() != "World total":
                continue
            if (row.get("US_Trade") or "").strip() != "Exports":
                continue
            if (row.get("Value_type") or "").strip() != "Volume":
                continue
            year_text = (row.get("Year") or "").strip()
            if len(year_text) < 4 or not year_text[:4].isdigit():
                continue
            if int(year_text[:4]) in {2025, 2026}:
                reduced_rows.append(row)

    if reduced_rows is None or not reduced_rows:
        return response

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(reduced_rows)
    new_payload = output.getvalue().encode("utf-8")

    if "Content-Encoding" in headers:
        headers["Content-Encoding"] = []
    if "content-encoding" in headers:
        headers["content-encoding"] = []
    if "Content-Length" in headers:
        headers["Content-Length"] = [str(len(new_payload))]
    if "content-length" in headers:
        headers["content-length"] = [str(len(new_payload))]

    body["string"] = new_payload
    response["headers"] = headers
    response["body"] = body
    return response


@pytest.fixture(scope="module")
def vcr_config():
    """VCR config."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            None,
        ],
        "before_record_response": _redact_binary_response,
    }


class TestUsdaFetchers:
    """Tests for the USDA provider fetchers."""

    @pytest.mark.record_http
    def test_weather_bulletin_fetcher(self, credentials=test_credentials):
        """Test UsdaWeatherBulletinFetcher."""
        params = {"year": 2024, "month": 12, "week": 2}

        fetcher = UsdaWeatherBulletinFetcher()
        result = fetcher.test(params, credentials)
        assert result is None

    @pytest.mark.record_http
    def test_weather_bulletin_download_fetcher(self, credentials=test_credentials):
        """Test UsdaWeatherBulletinDownloadFetcher."""
        params = {
            "urls": [
                "https://esmis.nal.usda.gov/sites/default/release-files/cj82k728n/9w033w568/x059f4232/wwcb0125.pdf"
            ],
        }

        fetcher = UsdaWeatherBulletinDownloadFetcher()
        result = fetcher.test(params, credentials)
        assert result is None

    @pytest.mark.record_http
    def test_commodity_psd_data_fetcher(self, credentials=test_credentials):
        """Test UsdaCommodityPsdDataFetcher."""
        params = {
            "report_id": "coffee_summary",
        }

        fetcher = UsdaCommodityPsdDataFetcher()
        result = fetcher.test(params, credentials)
        assert result is None

        time_series_params = {
            "report_id": "world_crop_production_summary",
            "commodity": "coffee",
            "attribute": ["exports"],
            "country": "BR",
            "start_year": 2025,
            "end_year": 2025,
            "aggregate_regions": False,
        }
        result = fetcher.test(time_series_params, credentials)
        assert result is None

    @pytest.mark.record_http
    def test_price_spreads_fetcher(self, credentials=test_credentials):
        """Test FarmToConsumerPriceSpreadsFetcher."""
        params = {"item": "milk_and_dairy_basket,fresh_apples", "start_year": 2015}

        fetcher = FarmToConsumerPriceSpreadsFetcher()
        result = fetcher.test(params, credentials)
        assert result is None

    def test_fas_report_calendar_fetcher(
        self, monkeypatch, credentials=test_credentials
    ):
        """Test FasReportCalendarFetcher."""
        from openbb_government_us.usda.utils import fas_report_calendar

        html = (
            '<div class="source-summary-count">1 results found</div>'
            '<div  class="c-view__row"><div  class="c-card">'
            '<div class="fas-date__month-day">Jul 22</div>'
            '<span class="fas-date__dow">Wed</span>'
            '<span class="fas-date__time">3:00 PM</span>'
            '<div class="c-card__tags"><span>World Production, Markets, and'
            " Trade Report</span></div>"
            '<a href="/report-release-announcement/coffee-10" class="c-card__url">'
            '<h3 class="c-card__title">Coffee: World Markets and Trade</h3></a>'
            '<a href="data:text/calendar;charset=utf8,DTSTART%3A20260722T190000Z">'
            "iCalendar</a></div></div>"
        )

        async def fake_afetch(url):
            return html

        monkeypatch.setattr(fas_report_calendar, "afetch_calendar", fake_afetch)
        params = {"report_type": "world_markets_trade"}

        fetcher = FasReportCalendarFetcher()
        result = fetcher.test(params, credentials)
        assert result is None

    @pytest.mark.record_http
    def test_dairy_data_fetcher(self, credentials=test_credentials):
        """Test DairyDataFetcher."""
        params = {"start_year": 2024}

        fetcher = DairyDataFetcher()
        result = fetcher.test(params, credentials)
        assert result is None

    @pytest.mark.record_http
    def test_milk_cost_of_production_fetcher(self, credentials=test_credentials):
        """Test MilkCostOfProductionFetcher."""
        params = {"state": "wisconsin", "start_year": 2024}

        fetcher = MilkCostOfProductionFetcher()
        result = fetcher.test(params, credentials)
        assert result is None

    @pytest.mark.record_http
    def test_major_land_uses_fetcher(self, credentials=test_credentials):
        """Test MajorLandUsesFetcher."""
        params = {"start_year": 2010}

        fetcher = MajorLandUsesFetcher()
        result = fetcher.test(params, credentials)
        assert result is None

    @pytest.mark.record_http
    def test_us_agricultural_trade_fetcher(self, credentials=test_credentials):
        """Test UsAgriculturalTradeFetcher."""
        params = {
            "table": "top_export_markets",
            "commodity": "Corn",
            "start_year": 2025,
        }

        fetcher = UsAgriculturalTradeFetcher()
        result = fetcher.test(params, credentials)
        assert result is None
