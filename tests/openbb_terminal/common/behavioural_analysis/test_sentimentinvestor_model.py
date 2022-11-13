# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.common.behavioural_analysis import sentimentinvestor_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "ticker",
    [
        ("BTC"),
        ("BTC-USD"),
    ],
)
def test_check_supported_ticker(ticker, recorder):
    df = sentimentinvestor_model.check_supported_ticker(ticker)
    recorder.capture(df)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "symbol, start_date, end_date, limit",
    [("AAPL", "2020-12-1", "2020-12-7", 100)],
)
def test_get_historical(symbol, start_date, end_date, limit, recorder):
    df = sentimentinvestor_model.get_historical(symbol, start_date, end_date, limit)
    recorder.capture(df)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "start, hour, number",
    [("2021-12-21", 9, 10)],
)
def test_get_trending(start, hour, number, recorder):
    df = sentimentinvestor_model.get_trending(start, hour, number)
    recorder.capture(df)


@pytest.mark.vcr(record_mode="none")
def test_get_trending_status_400(mocker):
    # MOCK GET
    attrs = {
        "json.return_value": {"error": "mock error message"},
    }

    mock_response = mocker.Mock(**attrs)
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    mock_response.status_code = 400

    df = sentimentinvestor_model.get_trending(
        start_date="2021-12-21",
        hour=9,
        number=10,
    )

    assert isinstance(df, pd.DataFrame)
    assert df.empty
