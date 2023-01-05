# IMPORTATION STANDARD
from datetime import datetime

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
import bt
from openbb_terminal.stocks import stocks_helper
from openbb_terminal.stocks.backtesting import bt_model


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
def test_get_data(recorder):
    df_stock = bt_model.get_data(symbol="TSLA", start_date="2021-12-05")
    recorder.capture(df_stock)


@pytest.mark.vcr
def test_buy_and_hold(mocker):
    yf_download = stocks_helper.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    back_test_instance = bt_model.buy_and_hold(
        symbol="TSLA",
        start_date="2021-12-05",
        name="MOCK_NAME",
    )
    assert isinstance(back_test_instance, bt.Backtest)


@pytest.mark.skip
def test_ema_strategy(mocker):
    yf_download = stocks_helper.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    ticker = "PM"
    start = datetime.strptime("2020-12-01", "%Y-%m-%d")
    end = datetime.strptime("2020-12-02", "%Y-%m-%d")
    df_stock = stocks_helper.load_ticker(ticker=ticker, start_date=start, end_date=end)
    back_test_instance = bt_model.ema_strategy(
        symbol=ticker,
        data=df_stock,
        ema_length=2,
        spy_bt=True,
        no_bench=False,
    )
    assert isinstance(back_test_instance, bt.backtest.Result)


@pytest.mark.skip
def test_emacross_strategy(mocker):
    yf_download = stocks_helper.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    ticker = "PM"
    start = datetime.strptime("2020-12-01", "%Y-%m-%d")
    end = datetime.strptime("2020-12-02", "%Y-%m-%d")
    df_stock = stocks_helper.load_ticker(ticker=ticker, start_date=start, end_date=end)
    back_test_instance = bt_model.emacross_strategy(
        symbol=ticker,
        data=df_stock,
        short_length=2,
        long_length=2,
        spy_bt=True,
        no_bench=False,
        shortable=True,
    )
    assert isinstance(back_test_instance, bt.backtest.Result)


@pytest.mark.skip
def test_rsi_strategy(mocker):
    yf_download = stocks_helper.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    ticker = "PM"
    start = datetime.strptime("2020-12-01", "%Y-%m-%d")
    end = datetime.strptime("2020-12-02", "%Y-%m-%d")
    df_stock = stocks_helper.load_ticker(ticker=ticker, start_date=start, end_date=end)
    back_test_instance = bt_model.rsi_strategy(
        symbol=ticker,
        data=df_stock,
        periods=2,
        low_rsi=2,
        high_rsi=2,
        spy_bt=True,
        no_bench=False,
        shortable=True,
    )
    assert isinstance(back_test_instance, bt.backtest.Result)
