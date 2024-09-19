"""CFTC Fetcher Tests."""

from datetime import date

import pytest
from openbb_cftc.models.cot import CftcCotFetcher
from openbb_cftc.models.cot_search import CftcCotSearchFetcher
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


def scrub_string(key):
    """Scrub a string from the response."""

    def before_record_response(response):
        response["headers"][key] = response["headers"].update({key: "MOCK_VALUE"})
        return response

    return before_record_response


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("$$app_token", "MOCK_APP_TOKEN"),
            ("$limit", "MOCK_LIMIT"),
            ("$order", "MOCK_ORDER"),
            ("$where", "MOCK_WHERE"),
        ],
        "before_record_response": [
            scrub_string("Etag"),
            scrub_string("X-Socrata-RequestId"),
            scrub_string("X-Socrata-Region"),
        ],
    }


@pytest.mark.record_http
def test_cftc_cot_fetcher(credentials=test_credentials):
    """Test the CFTC COT fetcher."""
    params = {
        "id": "239747",
        "start_date": date(2024, 8, 19),
        "end_date": date(2024, 8, 21),
    }

    fetcher = CftcCotFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


# The data for this request are local files, so we can't record them.
def test_cftc_cot_sarch_fetcher(credentials=test_credentials):
    """Test the CFTC COT Search fetcher."""
    params = {"query": "S&P 500"}

    fetcher = CftcCotSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
