# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.options import yfinance_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_option_expirations_no_dates(mocker):
    mock_yf_ticker = mocker.Mock()
    mock_yf_ticker.options = ()
    mocker.patch(
        target="gamestonk_terminal.stocks.options.yfinance_model.yf.Ticker",
        return_value=mock_yf_ticker,
    )
    yfinance_model.option_expirations(ticker="PM")


@pytest.mark.skip(
    "Something wrong with 'lastTradeDate' format while running on the server"
)
@pytest.mark.vcr
def test_get_option_chain(recorder):
    result_tuple = yfinance_model.get_option_chain(
        ticker="PM",
        expiration="2022-01-07",
    )
    result_tuple = (result_tuple.calls, result_tuple.puts)

    recorder.capture_list(result_tuple)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func",
    [
        "option_expirations",
        "get_dividend",
        "get_price",
        "get_info",
        "get_closing",
        "get_iv_surface",
    ],
)
def test_get_closing(func, recorder):
    result = getattr(yfinance_model, func)(ticker="PM")

    recorder.capture(result)
