"""Unit tests for FMP provider modules."""

import re
from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_fmp.models.senate_trading_rss import FMPSenateTradingRSSFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


def response_filter(response):
    """Filter the response."""
    if "Location" in response["headers"]:
        response["headers"]["Location"] = [
            re.sub(r"apikey=[^&]+", "apikey=MOCK_API_KEY", x)
            for x in response["headers"]["Location"]
        ]
    return response


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ],
        "before_record_response": response_filter,
    }



@pytest.mark.record_http
def test_senate_rss_fetcher(credentials=test_credentials):
    """Test FMP company filings fetcher."""
    params = {}
    fetcher = FMPSenateTradingRSSFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

