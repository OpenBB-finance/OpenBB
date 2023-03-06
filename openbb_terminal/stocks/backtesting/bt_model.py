"""Backtesting Model"""
__docformat__ = "numpy"

import logging
import warnings

import bt
import pandas as pd
import pandas_ta as ta
import yfinance as yf

from openbb_terminal.common.technical_analysis import ta_helpers
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import is_intraday

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_data(symbol: str, start_date: str = "2019-01-01") -> pd.DataFrame:
    """Function to replace bt.get, gets Adjusted close of symbol using yfinance.

    Parameters
    ----------
    symbol: str
        Ticker to get data for
    start_date: str
        Start date in YYYY-MM-DD format

    Returns
    -------
    prices: pd.DataFrame
        Dataframe of Adj Close with columns = [ticker]
    """
    data = yf.download(symbol, start=start_date, progress=False, ignore_tz=True)
    close_col = ta_helpers.check_columns(data, high=False, low=False)
    if close_col is None:
        return pd.DataFrame()
    df = pd.DataFrame(data[close_col])
    df.columns = [symbol]

    return df


@log_start_end(log=logger)
def buy_and_hold(symbol: str, start_date: str, name: str = "") -> bt.Backtest:
    """Generates a buy and hold backtest object for the given ticker.

    Parameters
    ----------
    symbol: str
        Stock to test
    start_date: str
        Backtest start date, in YYYY-MM-DD format. Can be either string or datetime
    name: str
        Name of the backtest (for labeling purposes)

    Returns
    -------
    bt.Backtest
        Backtest object for buy and hold strategy
    """
    prices = get_data(symbol, start_date)
    bt_strategy = bt.Strategy(
        name,
        [
            bt.algos.RunOnce(),
            bt.algos.SelectAll(),
            bt.algos.WeighEqually(),
            bt.algos.Rebalance(),
        ],
    )
    return bt.Backtest(bt_strategy, prices)


@log_start_end(log=logger)
def ema_strategy(
    symbol: str,
    data: pd.DataFrame,
    ema_length: int = 20,
    spy_bt: bool = True,
    no_bench: bool = False,
) -> bt.backtest.Result:
    """Perform backtest for simple EMA strategy.  Buys when price>EMA(l).

    Parameters
    ----------
    symbol: str
        Stock ticker
    data: pd.DataFrame
        Dataframe of prices
    ema_length: int
        Length of ema window
    spy_bt: bool
        Boolean to add spy comparison
    no_bench: bool
        Boolean to not show buy and hold comparison

    Returns
    -------
    bt.backtest.Result
        Backtest results
    """

    # TODO: Help Wanted!
    # Implement support for backtesting on intraday data
    if is_intraday(data):
        return None
    data.index = pd.to_datetime(data.index.date)

    symbol = symbol.lower()
    ema = pd.DataFrame()
    start_date = data.index[0]
    close_col = ta_helpers.check_columns(data, high=False, low=False)
    if close_col is None:
        return bt.backtest.Result()
    prices = pd.DataFrame(data[close_col])
    prices.columns = [symbol]
    ema[symbol] = ta.ema(prices[symbol], ema_length)
    bt_strategy = bt.Strategy(
        "AboveEMA",
        [
            bt.algos.SelectWhere(prices >= ema),
            bt.algos.WeighEqually(),
            bt.algos.Rebalance(),
        ],
    )
    bt_backtest = bt.Backtest(bt_strategy, prices)
    backtests = [bt_backtest]
    if spy_bt:
        spy_bt = buy_and_hold("spy", start_date, "SPY Hold")
        backtests.append(spy_bt)
    if not no_bench:
        stock_bt = buy_and_hold(symbol, start_date, symbol.upper() + " Hold")
        backtests.append(stock_bt)

    res = bt.run(*backtests)
    return res


@log_start_end(log=logger)
def emacross_strategy(
    symbol: str,
    data: pd.DataFrame,
    short_length: int = 20,
    long_length: int = 50,
    spy_bt: bool = True,
    no_bench: bool = False,
    shortable: bool = True,
) -> bt.backtest.Result:
    """Perform backtest for simple EMA strategy. Buys when price>EMA(l).

    Parameters
    ----------
    symbol : str
        Stock ticker
    data : pd.DataFrame
        Dataframe of prices
    short_length : int
        Length of short ema window
    long_length : int
        Length of long ema window
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison
    shortable : bool
        Boolean to allow for selling of the stock at cross

    Returns
    -------
    Result
        Backtest results
    """
    symbol = symbol.lower()
    start_date = data.index[0]
    close_col = ta_helpers.check_columns(data, low=False, high=False)
    if close_col is None:
        return bt.backtest.Result()
    prices = pd.DataFrame(data[close_col])
    prices.columns = [symbol]
    short_ema = pd.DataFrame(ta.ema(prices[symbol], short_length))
    short_ema.columns = [symbol]
    long_ema = pd.DataFrame(ta.ema(prices[symbol], long_length))
    long_ema.columns = [symbol]

    # signals
    signals = long_ema.copy()
    signals[short_ema > long_ema] = 1.0
    signals[short_ema <= long_ema] = -1.0 * shortable
    signals[long_ema.isnull()] = 0.0

    combined_data = bt.merge(signals, prices, short_ema, long_ema)
    combined_data.columns = ["signal", "price", "ema_short", "ema_long"]
    bt_strategy = bt.Strategy(
        "EMACross",
        [
            bt.algos.WeighTarget(signals),
            bt.algos.Rebalance(),
        ],
    )
    bt_backtest = bt.Backtest(bt_strategy, prices)
    backtests = [bt_backtest]
    if spy_bt:
        spy_bt = buy_and_hold("spy", start_date, "SPY Hold")
        backtests.append(spy_bt)
    if not no_bench:
        stock_bt = buy_and_hold(symbol, start_date, symbol.upper() + " Hold")
        backtests.append(stock_bt)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        res = bt.run(*backtests)
    return res


@log_start_end(log=logger)
def rsi_strategy(
    symbol: str,
    data: pd.DataFrame,
    periods: int = 14,
    low_rsi: int = 30,
    high_rsi: int = 70,
    spy_bt: bool = True,
    no_bench: bool = False,
    shortable: bool = True,
) -> bt.backtest.Result:
    """Perform backtest for simple EMA strategy. Buys when price>EMA(l).

    Parameters
    ----------
    symbol : str
        Stock ticker
    data : pd.DataFrame
        Dataframe of prices
    periods : int
        Number of periods for RSI calculation
    low_rsi : int
        Low RSI value to buy
    high_rsi : int
        High RSI value to sell
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison
    shortable : bool
        Flag to disable the ability to short sell

    Returns
    -------
    Result
        Backtest results
    """
    symbol = symbol.lower()
    start_date = data.index[0]
    close_col = ta_helpers.check_columns(data, high=False, low=False)
    if close_col is None:
        return pd.DataFrame()
    prices = pd.DataFrame(data[close_col])
    prices.columns = [symbol]
    rsi = pd.DataFrame(ta.rsi(prices[symbol], periods))
    rsi.columns = [symbol]

    signal = 0 * rsi.copy()
    signal[rsi > high_rsi] = -1 * shortable
    signal[rsi < low_rsi] = 1
    signal[rsi.isnull()] = 0

    merged_data = bt.merge(signal, prices)
    merged_data.columns = ["signal", "price"]

    warnings.simplefilter(action="ignore", category=FutureWarning)
    bt_strategy = bt.Strategy(
        "RSI Reversion", [bt.algos.WeighTarget(signal), bt.algos.Rebalance()]
    )
    bt_backtest = bt.Backtest(bt_strategy, prices)
    bt_backtest = bt.Backtest(bt_strategy, prices)
    backtests = [bt_backtest]
    # Once the bt package replaces pd iteritems with items we can remove this
    with warnings.catch_warnings():
        if spy_bt:
            spy_bt = buy_and_hold("spy", start_date, "SPY Hold")
            backtests.append(spy_bt)
        if not no_bench:
            stock_bt = buy_and_hold(symbol, start_date, symbol.upper() + " Hold")
            backtests.append(stock_bt)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        res = bt.run(*backtests)
    return res
