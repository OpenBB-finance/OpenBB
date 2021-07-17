import argparse
import datetime
from typing import List
from datetime import datetime as dt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np

from robin_stocks import robinhood
from termcolor import colored
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_terminal import RH_USERNAME as user, RH_PASSWORD as pw
from gamestonk_terminal.brokers.brokers_helpers import rh_positions_to_df

register_matplotlib_converters()

dt_format = "%Y-%m-%dT%H:%M:%SZ"
valid_span = ["day", "week", "month", "3month", "year", "5year", "all"]
valid_interval = ["5minute", "10minute", "hour", "day", "week"]

span_title_dict = {
    "day": "Day",
    "week": "Week",
    "month": "Month",
    "3month": "3 Months",
    "year": "Year",
    "5year": "5 Years",
    "all": "All Time",
}


def login():
    """Robinhood login"""
    robinhood.login(user, pw)


def logoff():
    """Robinhood logoff"""
    robinhood.logout()


def show_holdings():
    """Show Robinhood holdings"""
    holds = robinhood.account.build_holdings()
    stocks = []
    equity = []
    for stock, data in holds.items():
        stocks.append(stock)
        equity.append(round(float(data["equity"]), 2))

    print("\n", "Stonk\t last price \t prev close \t equity \t % Change", "\n")
    for stonk, eq in zip(stocks, equity):
        stonk_data = robinhood.stocks.get_quotes(stonk)[0]
        prev_close = round(float(stonk_data["adjusted_previous_close"]), 2)
        last_price = round(float(stonk_data["last_trade_price"]), 2)
        pct_change = round((last_price - prev_close) / prev_close, 3)
        to_print = f"{stonk}\t {last_price}\t\t {prev_close}\t\t {eq}\t\t {pct_change}"

        if last_price >= prev_close:
            print(colored(to_print, "green"))
        else:
            print(colored(to_print, "red"))
    print("")


def return_holdings() -> pd.DataFrame:
    """Return Robinhood holdings

    Returns
    ----------
    pd.DataFrame
        Robinhood holdings
    """
    holds = robinhood.account.build_holdings()
    return rh_positions_to_df(holds)


def plot_historical(other_args: List[str]):
    """Historical Portfolio Info

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="Port",
        description="""Historical Portfolio Info""",
    )
    parser.add_argument(
        "-s",
        "--span",
        dest="span",
        type=str,
        default="day",
        help="Span of historical data",
    )
    parser.add_argument(
        "-i",
        "--interval",
        dest="interval",
        default="10minute",
        type=str,
        help="Interval to look at portfolio",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        if ns_parser.interval not in valid_interval:
            raise ValueError(
                "Invalid Interval: Must be one of: 5minute, 10minute, hour, day, week"
            )
        if ns_parser.span not in valid_span:
            raise ValueError(
                "Invalid Span: Must be one of : day, week, month, 3month, year, 5year, all"
            )

        rhhist = robinhood.account.get_historical_portfolio(
            ns_parser.interval, span=ns_parser.span
        )
        rhhist_eq = rhhist["equity_historicals"]
        open_eq = []
        close_eq = []
        time = []

        for h in rhhist_eq:
            time.append(
                dt.strptime(h["begins_at"], dt_format) - datetime.timedelta(hours=4)
            )
            close_eq.append(float(h["adjusted_close_equity"]))
            open_eq.append(float(h["adjusted_open_equity"]))

        close_eq = np.asarray(close_eq)
        open_eq = np.asarray(open_eq)
        high = np.maximum(open_eq, close_eq)
        low = np.minimum(open_eq, close_eq)

        df = pd.DataFrame(index=time)
        df["High"] = high
        df["Low"] = low
        df["Open"] = open_eq
        df["Close"] = close_eq

        mc = mpf.make_marketcolors(
            up="green", down="red", edge="black", wick="black", ohlc="i"
        )
        s = mpf.make_mpf_style(marketcolors=mc, gridstyle=":", y_on_right=False)

        mpf.plot(
            df,
            type="candle",
            style=s,
            title=f"Portfolio for {span_title_dict[ns_parser.span]}",
            ylabel="Equity ($)",
            figsize=(plot_autoscale()),
            update_width_config=dict(
                candle_linewidth=1.0,
                candle_width=0.8,
            ),
        )
        if gtff.USE_ION:
            plt.ion()
        print("")

    except Exception as e:
        print(e, "\n")
        return
