# IMPORTATION STANDARD
from datetime import datetime

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
    "ticker, start, end, number",
    [("AAPL", "2020-12-1", "2020-12-7", 100)],
)
def test_get_historical(ticker, start, end, number, recorder):
    df = sentimentinvestor_model.get_historical(ticker, start, end, number)
    recorder.capture(df)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "start, hour, number",
    [(datetime(2021, 12, 21), 9, 10)],
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

    df = sentimentinvestor_model.get_trending(
        start=datetime(2021, 12, 21),
        hour=9,
        number=10,
    )

    assert isinstance(df, pd.DataFrame)
    assert df.empty
