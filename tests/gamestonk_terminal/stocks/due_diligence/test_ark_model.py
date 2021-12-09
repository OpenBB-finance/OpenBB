# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import requests
import pandas as pd
import pytest
import vcr

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
def test_get_ark_trades_by_ticker(default_csv_path):
    result_df = ark_model.get_ark_trades_by_ticker(ticker="TSLA")

    # result_df.to_csv(default_csv_path, index=True)
    expected_df = pd.read_csv(default_csv_path, index_col="Date", parse_dates=["Date"])

    assert not result_df.empty
    pd.testing.assert_frame_equal(result_df, expected_df)


@pytest.mark.xfail(raises=vcr.errors.CannotOverwriteExistingCassetteException)
@pytest.mark.default_cassette("test_get_ark_trades_by_ticker_AAPL")
@pytest.mark.vcr(record_mode="none")
def test_get_ark_trades_by_ticker_not_recorded():
    ark_model.get_ark_trades_by_ticker(ticker="AAPL")


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
