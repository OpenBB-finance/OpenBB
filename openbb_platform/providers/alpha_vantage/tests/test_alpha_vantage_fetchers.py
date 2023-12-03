from datetime import date

import pytest
from openbb_alpha_vantage.models.equity_historical import AVEquityHistoricalFetcher
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
@pytest.mark.skip(reason="This is a premium endpoint.")
def test_av_equity_historical_fetcher(credentials=test_credentials):
    params = params = {
        "symbol": "AAPL",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
        "interval": "1d",
    }

    fetcher = AVEquityHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
