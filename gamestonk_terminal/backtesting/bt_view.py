"""bt view module"""
__docformat__ = "numpy"
import argparse
from typing import List, Union
from datetime import datetime
import numpy as np
import pandas as pd
import bt
import pandas_ta as ta
from gamestonk_terminal.helper_funcs import check_positive, parse_known_args_and_warn
from gamestonk_terminal.backtesting.bt_helper import buy_and_hold, plot_bt, get_data

np.seterr(divide="ignore")


def simple_ema(ticker: str, start_date: Union[str, datetime], other_args: List[str]):
    """Strategy where stock is bought when Price > EMA(l)

    Parameters
    ----------
    ticker : str
        Stock to test
    start : Union[str, datetime]
        Backtest start date.  Can be either string or datetime
    other_args : List[str]
        List of argparse arguments
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="ema",
        description="Strategy where stock is bought when Price > EMA(l)",
    )
    parser.add_argument(
        "-l",
        default=20,
        dest="length",
        type=check_positive,
        help="EMA period to consider",
    )
    parser.add_argument(
        "--spy",
        action="store_true",
        default=False,
        help="Flag to add spy hold comparison",
        dest="spy",
    )
    parser.add_argument(
        "--no_bench",
        action="store_true",
        default=False,
        help="Flag to not show buy and hold comparison",
        dest="no_bench",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        ticker = ticker.lower()
        ema = pd.DataFrame()
        # prices = bt.get(ticker, start=start_date)
        # bt.get not working
        prices = get_data(ticker, start_date)
        ema[ticker] = ta.ema(prices[ticker], ns_parser.length)
        bt_strategy = bt.Strategy(
            "AboveEMA",
            [
                bt.algos.SelectWhere(prices >= ema),
                bt.algos.WeighEqually(),
                bt.algos.Rebalance(),
            ],
        )
        bt_backtest = bt.Backtest(bt_strategy, prices)

        if ns_parser.spy:
            spy_bt = buy_and_hold("spy", start_date, "SPY Hold")
            if ns_parser.no_bench:
                res = bt.run(bt_backtest, spy_bt)
            else:
                stock_bt = buy_and_hold(ticker, start_date, ticker.upper() + " Hold")
                res = bt.run(bt_backtest, spy_bt, stock_bt)
        else:
            if ns_parser.no_bench:
                res = bt.run(bt_backtest)
            else:
                stock_bt = buy_and_hold(ticker, start_date, ticker.upper() + " Hold")
                res = bt.run(bt_backtest, stock_bt)

        plot_bt(res, f"Equity for EMA({ns_parser.length})")
        print(res.display(), "\n")

    except Exception as e:
        print(e, "\n")


def ema_cross(ticker: str, start_date: Union[str, datetime], other_args: List[str]):
    """Strategy where we go long/short when EMA(short) is greater than/less than EMA(short)

    Parameters
    ----------
    ticker : str
        Stock to test
    start : Union[str, datetime]
        Backtest start date.  Can be either string or datetime
    other_args : List[str]
        List of argparse arguments
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="ema_cross",
        description="Cross between a long and a short Exponential Moving Average.",
    )
    parser.add_argument(
        "-l",
        "--long",
        default=50,
        dest="long",
        type=check_positive,
        help="Long EMA period",
    )
    parser.add_argument(
        "-s",
        "--short",
        default=20,
        dest="short",
        type=check_positive,
        help="Short EMA period",
    )
    parser.add_argument(
        "--spy",
        action="store_true",
        default=False,
        help="Flag to add spy hold comparison",
        dest="spy",
    )
    parser.add_argument(
        "--no_bench",
        action="store_true",
        default=False,
        help="Flag to not show buy and hold comparison",
        dest="no_bench",
    )
    parser.add_argument(
        "--no_short",
        action="store_false",
        default=True,
        dest="shortable",
        help="Flag that disables the short sell",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.long < ns_parser.short:
            print("Short EMA period is longer than Long EMA period\n")
            return

        ticker = ticker.lower()
        # prices = bt.get(ticker, start=start_date)
        prices = get_data(ticker, start_date)
        short_ema = pd.DataFrame(ta.ema(prices[ticker], ns_parser.short))
        short_ema.columns = [ticker]
        long_ema = pd.DataFrame(ta.ema(prices[ticker], ns_parser.long))
        long_ema.columns = [ticker]

        # signals
        signals = long_ema.copy()
        signals[short_ema > long_ema] = 1.0
        signals[short_ema <= long_ema] = -1.0 * ns_parser.shortable
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

        if ns_parser.spy:
            spy_bt = buy_and_hold("spy", start_date, "SPY Hold")
            if ns_parser.no_bench:
                res = bt.run(bt_backtest, spy_bt)
            else:
                stock_bt = buy_and_hold(ticker, start_date, ticker.upper() + " Hold")
                res = bt.run(bt_backtest, spy_bt, stock_bt)
        else:
            if ns_parser.no_bench:
                res = bt.run(bt_backtest)
            else:
                stock_bt = buy_and_hold(ticker, start_date, ticker.upper() + " Hold")
                res = bt.run(bt_backtest, stock_bt)

        plot_bt(res, f"EMA Cross for EMA({ns_parser.short})/EMA({ns_parser.long})")
        print(res.display(), "\n")

    except Exception as e:
        print(e, "\n")


def rsi_strat(ticker: str, start_date: Union[datetime, str], other_args: List[str]):
    """Strategy that buys when the stock is less than a threshold and shorts when it exceeds a threshold.

    Parameters
    ----------
    ticker : str
        Stock to test
    start : Union[str, datetime]
        Backtest start date.  Can be either string or datetime
    other_args : List[str]
        List of argparse arguments
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="rsi_strat",
        description="""Strategy that buys when the stock is less than a threshold
        and shorts when it exceeds a threshold.""",
    )
    parser.add_argument(
        "-p",
        "--periods",
        dest="periods",
        help="Number of periods for RSI calculation",
        type=check_positive,
        default=14,
    )
    parser.add_argument(
        "-u",
        "--high",
        default=70,
        dest="high",
        type=check_positive,
        help="High (upper) RSI Level",
    )
    parser.add_argument(
        "-l", "--low", default=30, dest="low", type=check_positive, help="Low RSI Level"
    )
    parser.add_argument(
        "--spy",
        action="store_true",
        default=False,
        help="Flag to add spy hold comparison",
        dest="spy",
    )
    parser.add_argument(
        "--no_bench",
        action="store_true",
        default=False,
        help="Flag to not show buy and hold comparison",
        dest="no_bench",
    )
    parser.add_argument(
        "--no_short",
        action="store_false",
        default=True,
        dest="shortable",
        help="Flag that disables the short sell",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.high < ns_parser.low:
            print("Low RSI value is higher than Low RSI value\n")
            return

        ticker = ticker.lower()
        # prices = bt.get(ticker, start=start_date)
        prices = get_data(ticker, start_date)
        rsi = pd.DataFrame(ta.rsi(prices[ticker], ns_parser.periods))
        rsi.columns = [ticker]

        signal = 0 * rsi.copy()
        signal[rsi > ns_parser.high] = -1
        signal[rsi < ns_parser.low] = 1
        signal[rsi.isnull()] = 0

        merged_data = bt.merge(signal, prices)
        merged_data.columns = ["signal", "price"]

        bt_strategy = bt.Strategy(
            "RSI Reversion", [bt.algos.WeighTarget(signal), bt.algos.Rebalance()]
        )
        bt_backtest = bt.Backtest(bt_strategy, prices)

        if ns_parser.spy:
            spy_bt = buy_and_hold("spy", start_date, "SPY Hold")
            if ns_parser.no_bench:
                res = bt.run(bt_backtest, spy_bt)
            else:
                stock_bt = buy_and_hold(ticker, start_date, ticker.upper() + " Hold")
                res = bt.run(bt_backtest, spy_bt, stock_bt)
        else:
            if ns_parser.no_bench:
                res = bt.run(bt_backtest)
            else:
                stock_bt = buy_and_hold(ticker, start_date, ticker.upper() + " Hold")
                res = bt.run(bt_backtest, stock_bt)

        plot_bt(res, f"RSI Strategy between ({ns_parser.low}, {ns_parser.high})")
        print(res.display(), "\n")

    except Exception as e:
        print(e, "\n")
