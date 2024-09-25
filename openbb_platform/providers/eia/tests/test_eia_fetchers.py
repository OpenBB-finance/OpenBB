"""EIA Fetcher Tests."""

import pytest

from openbb_core.app.service.user_service import UserService
from openbb_eia.models.petroleum_status_report import EiaPetroleumStatusReportFetcher

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
            ("api_key", "MOCK_API_KEY"),
        ],
        "before_record_response": [
            scrub_string("X-Amz-Cf-Id"),
            scrub_string("Etag"),
            scrub_string("Via"),
            scrub_string("X-Amz-Cf-Pop"),
            scrub_string("X-Cache"),
        ],
    }


@pytest.mark.record_http
def test_eia_petroleum_status_report_fetcher(credentials=None):
    """Test EIA petroleum status report fetcher."""
    params = {"category": "crude_petroleum_stocks", "table": "all"}

    fetcher = EiaPetroleumStatusReportFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
