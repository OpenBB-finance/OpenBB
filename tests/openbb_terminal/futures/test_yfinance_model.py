# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.futures import yfinance_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "category",
    [
        "agriculture",
        "metals",
    ],
)
def test_get_search_futures(recorder, category):
    result = yfinance_model.get_search_futures(category)

    recorder.capture(result)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "symbols",
    [
        ["BLK"],
    ],
)
def test_get_historical_futures(recorder, symbols):
    result = yfinance_model.get_historical_futures(symbols)

    recorder.capture(result)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "symbol",
    [
        ["ES"],
    ],
)
def test_get_curve_futures(recorder, symbol):
    result = yfinance_model.get_curve_futures(symbol)

    recorder.capture(result)
