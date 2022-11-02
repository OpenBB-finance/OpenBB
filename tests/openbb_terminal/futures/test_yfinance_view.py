# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest
import yfinance

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


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "tickers",
    [
        ["BLK", "SB"],
        ["ES", "SF"],
    ],
)
def test_display_historical(mocker, tickers):
    yf_download = yfinance_view.yfinance_model.yf.download
    # yf_download = yfinance.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch(
        # "openbb_terminal.futures.yfinance_view.yfinance_model.yf.download",
        "openbb_terminal.futures.yfinance_model.yf.download",
        side_effect=mock_yf_download,
    )
    # mocker.patch("yfinance.download", side_effect=mock_yf_download)

    yfinance_view.display_historical(
        tickers=tickers,
        start_date="2022-10-10",
        raw=True,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "ticker",
    ["ES", "YI"],
)
def test_display_curve(mocker, ticker):
    yf_download = yfinance.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    yfinance_view.display_curve(
        ticker=ticker,
        raw=True,
    )
