"""IMF Fetcher Tests."""

from datetime import date

import pytest

from openbb_imf.models.available_indicators import ImfAvailableIndicatorsFetcher
from openbb_imf.models.economic_indicators import ImfEconomicIndicatorsFetcher
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


def scrub_string(key):
    """Scrub a string from the response."""

    def before_record_response(response):
        response["headers"][key] = response["headers"].update({key: None})
        return response

    return before_record_response


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [("User-Agent", None)],
        "before_record_response": [
            scrub_string("Set-Cookie"),
        ],
    }


@pytest.mark.record_http
def test_imf_economic_indicators_fetcher(credentials=test_credentials):
    """Test the IMF EconomicIndicators fetcher."""
    params = {
        "country": "JP",
        "frequency": "month",
        "symbol": "RAMFDA_USD",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 12, 31),
    }

    fetcher = ImfEconomicIndicatorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


# The data for this request are local files, so we can't record them.
def test_imf_available_indicators_fetcher(credentials=test_credentials):
    """Test the IMF Available Indicators fetcher."""
    params = {}

    fetcher = ImfAvailableIndicatorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
