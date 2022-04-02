from datetime import datetime
import pytest

try:
    from bots.load_candle import dt_utcnow_local_tz, stock_data
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.bots
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


@pytest.mark.bots
def test_dt_utcnow_local_tz():
    value = dt_utcnow_local_tz()
    assert isinstance(value, datetime)


@pytest.mark.bots
@pytest.mark.vcr
@pytest.mark.parametrize(
    "ticker, candles, news, interval, start, end",
    [
        ("TSLA", False, False, 1, "", ""),
        ("TSLA", True, False, 1, "", ""),
        ("TSLA", False, True, 1, "", ""),
        ("TSLA", True, True, 1, "", ""),
        ("TSLA", False, False, 1440, "2019-10-10", "2020-10-10"),
    ],
)
def test_stock_data(mocker, recorder, ticker, candles, news, interval, start, end):
    mocker.patch("bots.load_candle.imps.API_BINANCE_SECRET", "1")
    mocker.patch("bots.load_candle.imps.API_BINANCE_KEY", "1")
    value = stock_data(
        ticker,
        news=news,
        heikin_candles=candles,
        interval=interval,
        start=start,
        end=end,
    )
    df = value[0]
    df.index = df.index.strftime("%Y-%m-%d")
    recorder.capture(df)


@pytest.mark.bots
@pytest.mark.parametrize("ticker", ["ZZZZ", "-BTC"])
def test_stock_data_exception(ticker):
    with pytest.raises(Exception):
        stock_data(ticker)
