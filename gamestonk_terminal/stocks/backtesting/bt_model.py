"""Backtesting Model"""
__docformat__ = "numpy"

from typing import Union
from datetime import datetime
import bt
from bt import Backtest
from bt.backtest import Result
import pandas as pd
import pandas_ta as ta
import yfinance as yf


def get_data(ticker: str, start_date: Union[str, datetime]) -> pd.DataFrame:
    """Function to replace bt.get,  Gets Adjusted close of ticker using yfinance
    Parameters
    ----------
    ticker: str
        Ticker to get data for
    start_date:
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


def buy_and_hold(ticker: str, start_date: Union[str, datetime], name: str) -> Backtest:
    """
    Generates a buy and hold backtest object for the given ticker
    Parameters
    ----------
    ticker: str
        Stock to test
    start: Union[str, datetime]
        Backtest start date.  Can be either string or datetime
    name:
        Name of the backtest (for labeling purposes)

    Returns
    -------
    bt.Backtest object for buy and hold strategy
    """
    # prices = bt.get(ticker, start=start)
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


def ema_strategy(
    ticker: str,
    start_date: Union[str, datetime],
    ema_length: int,
    spy_bt: bool = True,
    no_bench: bool = False,
) -> Result:
    """Perform backtest for simple EMA strategy.  Buys when price>EMA(l)

    Parameters
    ----------
    ticker : str
        Stock ticker
    start_date : Union[str, datetime]
        Start date of backtest
    ema_length : int
        Length of ema window
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison

    Returns
    -------
    Result
        Backtest results
    """
    ticker = ticker.lower()
    ema = pd.DataFrame()
    prices = get_data(ticker, start_date)
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


def ema_cross_strategy(
    ticker: str,
    start_date: Union[str, datetime],
    short_length: int,
    long_length: int,
    spy_bt: bool = True,
    no_bench: bool = False,
    shortable: bool = True,
) -> Result:
    """Perform backtest for simple EMA strategy.  Buys when price>EMA(l)

    Parameters
    ----------
    ticker : str
        Stock ticker
    start_date : Union[str, datetime]
        Start date of backtest
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
    prices = get_data(ticker, start_date)
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


def rsi_strategy(
    ticker: str,
    start_date: Union[str, datetime],
    periods: int,
    low_rsi: int,
    high_rsi: int,
    spy_bt: bool = True,
    no_bench: bool = False,
    shortable: bool = True,
) -> Result:
    """Perform backtest for simple EMA strategy.  Buys when price>EMA(l)

    Parameters
    ----------
    ticker : str
        Stock ticker
    start_date : Union[str, datetime]
        Start date of backtest
    periods : int
        Number of periods for RSI calculati
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
    prices = get_data(ticker, start_date)
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
