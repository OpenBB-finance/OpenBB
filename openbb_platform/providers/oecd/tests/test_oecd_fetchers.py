import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_oecd.models.gdp_forecast import OECDGdpForecastFetcher
from openbb_oecd.models.gdp_nominal import OECDGdpNominalFetcher
from openbb_oecd.models.gdp_real import OECDGdpRealFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.mark.record_http
def test_oecd_nominal_gdp_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2020, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = OECDGdpNominalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_real_gdp_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2020, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }
    fetcher = OECDGdpRealFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecd_forecast_gdp_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2020, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = OECDGdpForecastFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
