# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks import stocks_helper
from openbb_terminal.stocks.insider import businessinsider_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.vcr
# @pytest.mark.record_stdout
@pytest.mark.parametrize(
    "raw",
    [True, False],
)
def test_insider_activity(mocker, raw):
    yf_download = stocks_helper.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    ticker = "AAPL"
    stock = stocks_helper.load(symbol=ticker)
    businessinsider_view.insider_activity(
        data=stock,
        symbol=ticker,
        start_date=None,
        interval="1440min",
        limit=5,
        raw=raw,
        export="",
    )
