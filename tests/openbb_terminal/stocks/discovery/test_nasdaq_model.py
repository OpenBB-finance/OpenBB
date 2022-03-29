# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest
import requests

# IMPORTATION INTERNAL
from openbb_terminal.stocks.discovery import nasdaq_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("api_key", "MOCK_API"),
        ]
    }


@pytest.mark.vcr
def test_get_retail_tickers(recorder):
    retail_tickers = nasdaq_model.get_retail_tickers()

    recorder.capture(retail_tickers)


@pytest.mark.vcr(record_mode="none")
def test_get_ipo_calendar_400(mocker):
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    retail_tickers = nasdaq_model.get_retail_tickers()

    assert retail_tickers.empty


@pytest.mark.vcr(record_mode="none")
def test_dividend_fails(mocker):
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    retail_tickers = nasdaq_model.get_dividend_cal("2021-01-01")

    assert retail_tickers.empty
