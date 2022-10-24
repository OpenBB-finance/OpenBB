# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.futures import yfinance_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "category",
    ["agriculture", "metals"],
)
def test_display_search(category):
    yfinance_view.display_search(
        category=category, exchange="", description="", export=""
    )


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "tickers",
    [["BLK"]],
)
def test_display_historical(tickers):
    yfinance_view.display_historical(
        tickers=tickers,
        start_date="2022-10-10",
        raw=True,
    )


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "ticker",
    ["ES"],
)
def test_display_curve(ticker):
    yfinance_view.display_curve(
        ticker=ticker,
        raw=True,
    )
