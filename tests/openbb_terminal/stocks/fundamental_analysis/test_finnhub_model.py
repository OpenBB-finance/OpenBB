# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import finnhub_model


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_query_parameters": [("token", "MOCK_TOKEN")]}


@pytest.mark.vcr
def test_get_rating_over_time(recorder):
    result_df = finnhub_model.get_rating_over_time(symbol="TSLA")

    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_rating_over_time_invalid_ticker():
    result_df = finnhub_model.get_rating_over_time(symbol="INVALID_TICKER")

    assert result_df.empty


@pytest.mark.vcr(mode="none")
def test_get_rating_over_time_invalid_status(mocker):
    attrs = {
        "status_code": 400,
        "json.return_value": {"error": "mock error message"},
    }

    mock_response = mocker.Mock(**attrs)

    mocker.patch(
        target="openbb_terminal.helper_funcs.requests.get",
        new=mocker.Mock(return_value=mock_response),
    )
    result_df = finnhub_model.get_rating_over_time(symbol="FAILING_REQUEST")

    assert result_df.empty
