# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest
import requests

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.comparison_analysis import finnhub_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.mark.vcr
def test_get_similar_companies(recorder):
    result_tuple = finnhub_model.get_similar_companies(ticker="TSLA")

    recorder.capture(result_tuple)


@pytest.mark.vcr(record_mode="none")
def test_get_similar_companies_invalid_status(mocker, recorder):
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))
    result_tuple = finnhub_model.get_similar_companies(ticker="TSLA")

    recorder.capture(result_tuple)
