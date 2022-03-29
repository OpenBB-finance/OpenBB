# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.technical_analysis import tradingview_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ]
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "interval",
    ["1d", ""],
)
def test_get_tradingview_recommendation(interval, recorder):
    result = tradingview_model.get_tradingview_recommendation(
        ticker="AAPL",
        exchange="",
        screener="america",
        interval=interval,
    )
    recorder.capture(result)
