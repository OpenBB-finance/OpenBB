# IMPORTATION STANDARD
import json

# IMPORTATION THIRDPARTY
import pytest
import requests

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.technical_analysis import finnhub_model

RESPONSE_SAMPLE = """{
    "points": [
        {
        "aprice": 1.09236,
        "atime": 1567458000,
        "bprice": 1.1109,
        "btime": 1568322000,
        "cprice": 1.09897,
        "ctime": 1568667600,
        "dprice": 0,
        "dtime": 0,
        "end_price": 1.1109,
        "end_time": 1568926800,
        "entry": 1.1109,
        "eprice": 0,
        "etime": 0,
        "mature": 0,
        "patternname": "Double Bottom",
        "patterntype": "bullish",
        "profit1": 1.1294,
        "profit2": 0,
        "sortTime": 1568926800,
        "start_price": 1.1109,
        "start_time": 1566853200,
        "status": "incomplete",
        "stoploss": 1.0905,
        "symbol": "EUR_USD",
        "terminal": 0
        },
        {
        "aprice": 1.09236,
        "atime": 1567458000,
        "bprice": 1.1109,
        "btime": 1568322000,
        "cprice": 1.09897,
        "ctime": 1568667600,
        "dprice": 1.13394884,
        "dtime": 1568926800,
        "entry": 1.1339,
        "mature": 0,
        "patternname": "Bat",
        "patterntype": "bearish",
        "profit1": 1.1181,
        "profit2": 1.1082,
        "przmax": 1.1339,
        "przmin": 1.129,
        "rrratio": 3.34,
        "sortTime": 1568667600,
        "status": "incomplete",
        "stoploss": 1.1416,
        "symbol": "EUR_USD",
        "terminal": 0,
        "xprice": 1.1393,
        "xtime": 1561669200
        }
    ]
}"""


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ]
    }


@pytest.mark.vcr(record_mode="none")
def test_get_pattern_recognition(recorder, mocker):
    # MOCK RESPONSE
    mock_response = requests.Response()
    mock_response.status_code = 200
    mocker.patch.object(
        target=mock_response,
        attribute="json",
        side_effect=lambda: json.loads(RESPONSE_SAMPLE),
    )
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    result_df = finnhub_model.get_pattern_recognition(ticker="PM", resolution="D")
    recorder.capture(result_df)


@pytest.mark.vcr(record_mode="none")
def test_get_pattern_recognition_invalid_status(mocker):
    # MOCK RESPONSE
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))
    result = finnhub_model.get_pattern_recognition(ticker="PM", resolution="D")

    assert result.empty


@pytest.mark.vcr(record_mode="none")
def test_get_pattern_recognition_invalid_json(mocker):
    # MOCK RESPONSE
    mock_response = requests.Response()
    mock_response.status_code = 200
    mocker.patch.object(
        target=mock_response,
        attribute="json",
        side_effect=lambda: dict(),
    )
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    result = finnhub_model.get_pattern_recognition(ticker="PM", resolution="D")

    assert result.empty
