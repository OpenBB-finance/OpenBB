import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_oecd.models.gdpforecast import OECDGDPForecastFetcher
from openbb_oecd.models.gdpnom import OECDGDPNomFetcher
from openbb_oecd.models.gdpreal import OECDGDPRealFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.mark.record_http
def test_oecdgdp_nom_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2020, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = OECDGDPNomFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecdgdp_real_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2020, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }
    fetcher = OECDGDPRealFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_oecdgdp_forecast_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2020, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = OECDGDPForecastFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
