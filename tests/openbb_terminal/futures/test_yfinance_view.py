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
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
        ],
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
    "symbols",
    [
        ["BLK", "SB"],
        ["ES", "SF"],
    ],
)
def test_display_historical(mocker, symbols):
    yf_download = yfinance.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    yfinance_view.display_historical(
        symbols=symbols,
        start_date="2022-10-10",
        raw=True,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "symbol",
    ["ES", "YI"],
)
def test_display_curve(mocker, symbol):
    yf_download = yfinance.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    yfinance_view.display_curve(
        symbol=symbol,
        raw=True,
    )
