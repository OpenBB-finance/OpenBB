# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import requests
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import ark_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.default_cassette("test_get_ark_trades_by_ticker_TSLA")
@pytest.mark.vcr
def test_get_ark_trades_by_ticker(recorder):
    result_df = ark_model.get_ark_trades_by_ticker(ticker="TSLA")

    recorder.capture(result_df)


@pytest.mark.default_cassette("test_get_ark_trades_by_ticker_INVALID_TICKER")
@pytest.mark.vcr
def test_get_ark_trades_by_ticker_invalid_ticker():
    result_df = ark_model.get_ark_trades_by_ticker(ticker="INVALID_TICKER")
    assert result_df.empty


@pytest.mark.default_cassette("test_get_ark_trades_by_ticker_TSLA")
@pytest.mark.vcr(record_mode="none")
def test_get_ark_trades_by_ticker_invalid_json(mocker):
    mocker.patch(
        target="json.loads",
        new=mocker.Mock(
            return_value={
                "props": {
                    "pageProps": [],
                }
            }
        ),
    )
    result_df = ark_model.get_ark_trades_by_ticker(ticker="TSLA")

    assert result_df.empty


@pytest.mark.vcr(record_mode="none")
def test_get_ark_trades_by_ticker_invalid_status(mocker):
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(
        target="requests.get",
        new=mocker.Mock(return_value=mock_response),
    )
    result_df = ark_model.get_ark_trades_by_ticker(ticker="TSLA")

    assert result_df.empty


@pytest.mark.default_cassette("test_get_ark_trades_by_ticker_TSLA")
@pytest.mark.vcr(record_mode="none")
def test_get_ark_trades_by_ticker_json_normalize(mocker):
    mock_df = pd.DataFrame()
    mocker.patch(
        target="pandas.json_normalize",
        new=mocker.Mock(return_value=mock_df),
    )
    result_df = ark_model.get_ark_trades_by_ticker(ticker="TSLA")

    assert result_df.empty
