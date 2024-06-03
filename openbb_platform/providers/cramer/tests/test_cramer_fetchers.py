"""Pyth2 Fetchers tests."""
import pytest
from openbb_providers.models.cramer import CramerData,CramerFetcher
from openbb_core.app.service.user_service import UserService
import re
from datetime import date

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)

def response_filter(response):
    if "Location" in response["headers"]:
        response["headers"]["Location"] = [
            re.sub(r"apikey=[^&]+", "apikey=MOCK_API_KEY", x)
            for x in response["headers"]["Location"]
        ]
    return response

@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ],
        "before_record_response": response_filter,
    }

#
@pytest.mark.record_http
def test_cramer_fetcher(credentials=test_credentials):
    params = {'lookback' : 10}
    fetcher = CramerFetcher()
    result = fetcher.test(params, credentials)
    assert result is None

def test_cramer_data():

    test_dict = {'as_of_date': date(2024,5,17),
                  'ticker': 'FTAI',
                  'recommendation': 'Strong buy',

                 }


    cd = CramerData(**test_dict)

    assert cd.ticker == test_dict['ticker']
    assert cd.as_of_date == test_dict['as_of_date']
    assert cd.recommendation == test_dict['recommendation']

