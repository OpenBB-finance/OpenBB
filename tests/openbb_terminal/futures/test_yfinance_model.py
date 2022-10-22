# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.futures import yfinance_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
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
    "tickers",
    [
        ["BLK"],
    ],
)
def test_get_historical_futures(recorder, tickers):
    result = yfinance_model.get_historical_futures(tickers).head()

    recorder.capture(result)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "ticker",
    [
        ["ES"],
    ],
)
def test_get_curve_futures(recorder, ticker):
    result = yfinance_model.get_curve_futures(ticker)

    recorder.capture(result)
