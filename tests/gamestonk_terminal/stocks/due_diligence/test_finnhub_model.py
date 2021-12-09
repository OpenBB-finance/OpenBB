# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest
import requests

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import finnhub_model


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_query_parameters": [("token", "MOCK_TOKEN")]}


@pytest.mark.vcr
def test_get_rating_over_time(recorder):
    result_df = finnhub_model.get_rating_over_time(ticker="TSLA")

    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_rating_over_time_invalid_ticker():
    result_df = finnhub_model.get_rating_over_time(ticker="INVALID_TICKER")

    assert result_df.empty


@pytest.mark.vcr(mode="none")
def test_get_rating_over_time_invalid_status(mocker):
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(
        target="requests.get",
        new=mocker.Mock(return_value=mock_response),
    )
    result_df = finnhub_model.get_rating_over_time(ticker="FAILING_REQUEST")

    assert result_df.empty
