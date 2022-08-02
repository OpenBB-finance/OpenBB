"""Backtesting Model"""
__docformat__ = "numpy"

import logging

import bt
import pandas as pd
import pandas_ta as ta
import yfinance as yf

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import is_intraday

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_data(ticker: str, start_date: str) -> pd.DataFrame:
    """Function to replace bt.get,  Gets Adjusted close of ticker using yfinance

    Parameters
    ----------
    ticker: str
        Ticker to get data for
    start_date: str
        Start date

    Returns
    -------
    prices: pd.DataFrame
        Dataframe of Adj Close with columns = [ticker]
    """
    prices = yf.download(ticker, start=start_date, progress=False)
    prices = pd.DataFrame(prices["Adj Close"])
    prices.columns = [ticker]
    return prices


@log_start_end(log=logger)
def buy_and_hold(ticker: str, start_date: str, name: str) -> bt.Backtest:
    """Generates a buy and hold backtest object for the given ticker

    Parameters
    ----------
    ticker: str
        Stock to test
    start:str
        Backtest start date.  Can be either string or datetime
    name: str
        Name of the backtest (for labeling purposes)

    Returns
    -------
    bt.Backtest
        Backtest object for buy and hold strategy
    """
    prices = get_data(ticker, start_date)
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
    ticker: str,
    df_stock: pd.DataFrame,
    ema_length: int,
    spy_bt: bool = True,
    no_bench: bool = False,
) -> bt.backtest.Result:
    """Perform backtest for simple EMA strategy.  Buys when price>EMA(l)

    Parameters
    ----------
    ticker : str
        Stock ticker
    df_stock : pd.DataFrame
        Dataframe of prices
    ema_length : int
        Length of ema window
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison

    Returns
    -------
    bt.backtest.Result
        Backtest results
    """

    # TODO: Help Wanted!
    # Implement support for backtesting on intraday data
    if is_intraday(df_stock):
        return None
    df_stock.index = pd.to_datetime(df_stock.index.date)

    ticker = ticker.lower()
    ema = pd.DataFrame()
    start_date = df_stock.index[0]
    prices = pd.DataFrame(df_stock["Adj Close"])
    prices.columns = [ticker]
    ema[ticker] = ta.ema(prices[ticker], ema_length)
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
        stock_bt = buy_and_hold(ticker, start_date, ticker.upper() + " Hold")
        backtests.append(stock_bt)

    res = bt.run(*backtests)
    return res


@log_start_end(log=logger)
def ema_cross_strategy(
    ticker: str,
    df_stock: pd.DataFrame,
    short_length: int,
    long_length: int,
    spy_bt: bool = True,
    no_bench: bool = False,
    shortable: bool = True,
) -> bt.backtest.Result:
    """Perform backtest for simple EMA strategy. Buys when price>EMA(l)

    Parameters
    ----------
    ticker : str
        Stock ticker
    df_stock : pd.DataFrame
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
    ticker = ticker.lower()
    start_date = df_stock.index[0]
    prices = pd.DataFrame(df_stock["Adj Close"])
    prices.columns = [ticker]
    short_ema = pd.DataFrame(ta.ema(prices[ticker], short_length))
    short_ema.columns = [ticker]
    long_ema = pd.DataFrame(ta.ema(prices[ticker], long_length))
    long_ema.columns = [ticker]

    # signals
    signals = long_ema.copy()
    signals[short_ema > long_ema] = 1.0
    signals[short_ema <= long_ema] = -1.0 * shortable
    signals[long_ema.isnull()] = 0.0

    combined_data = bt.merge(signals, prices, short_ema, long_ema)
    combined_data.columns = ["signal", "price", "ema_short", "ema_long"]
    bt_strategy = bt.Strategy(
        "EMA_Cross",
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
        stock_bt = buy_and_hold(ticker, start_date, ticker.upper() + " Hold")
        backtests.append(stock_bt)

    res = bt.run(*backtests)
    return res


@log_start_end(log=logger)
def rsi_strategy(
    ticker: str,
    df_stock: pd.DataFrame,
    periods: int,
    low_rsi: int,
    high_rsi: int,
    spy_bt: bool = True,
    no_bench: bool = False,
    shortable: bool = True,
) -> bt.backtest.Result:
    """Perform backtest for simple EMA strategy. Buys when price>EMA(l)

    Parameters
    ----------
    ticker : str
        Stock ticker
    df_stock : pd.DataFrame
        Dataframe of prices
    periods : int
        Number of periods for RSI calculation
    low_rsi : int
        Low RSI value to buy
    hirh_rsi : int
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
    ticker = ticker.lower()
    start_date = df_stock.index[0]
    prices = pd.DataFrame(df_stock["Adj Close"])
    prices.columns = [ticker]
    rsi = pd.DataFrame(ta.rsi(prices[ticker], periods))
    rsi.columns = [ticker]

    signal = 0 * rsi.copy()
    signal[rsi > high_rsi] = -1 * shortable
    signal[rsi < low_rsi] = 1
    signal[rsi.isnull()] = 0

    merged_data = bt.merge(signal, prices)
    merged_data.columns = ["signal", "price"]

    bt_strategy = bt.Strategy(
        "RSI Reversion", [bt.algos.WeighTarget(signal), bt.algos.Rebalance()]
    )
    bt_backtest = bt.Backtest(bt_strategy, prices)
    bt_backtest = bt.Backtest(bt_strategy, prices)
    backtests = [bt_backtest]
    if spy_bt:
        spy_bt = buy_and_hold("spy", start_date, "SPY Hold")
        backtests.append(spy_bt)
    if not no_bench:
        stock_bt = buy_and_hold(ticker, start_date, ticker.upper() + " Hold")
        backtests.append(stock_bt)

    res = bt.run(*backtests)
    return res
