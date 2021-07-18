import argparse
import os
from typing import List
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import alpaca_trade_api as alp_api
from termcolor import colored
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.brokers.brokers_helpers import (
    alpaca_positions_to_df,
)

register_matplotlib_converters()


def login():
    """Login to Alpaca account"""
    if not (
        os.getenv("APCA_API_KEY_ID")
        and os.getenv("APCA_API_SECRET_KEY")
        and os.getenv("APCA_API_BASE_URL")
    ):
        raise ValueError("Alpaca Keys not defined in env")


def show_holdings():
    """Show Alpaca holdings"""
    api = alp_api.REST()
    positions = api.list_positions()
    print("\n", "Stonk\t last price \t prev close \t equity \t % Change")

    for pos in positions:
        stonk = pos.symbol
        last_price = round(float(pos.current_price), 2)
        prev_close = round(float(pos.lastday_price), 2)
        eq = round(float(pos.market_value), 2)
        pct_change = round(float(pos.change_today), 3)
        to_print = f"{stonk}\t {last_price}\t\t {prev_close}\t\t {eq}\t\t {pct_change}"
        if pct_change >= 0:
            print(colored(to_print, "green"))
        else:
            print(colored(to_print, "red"))
    print("")


def return_holdings() -> pd.DataFrame:
    """Get Alpaca holdings

    Returns
    ----------
    pd.DataFrame
        Alpaca holdings
    """
    api = alp_api.REST()
    positions = api.list_positions()
    return alpaca_positions_to_df(positions)


def plot_historical(other_args: List[str]):
    """Historical Portfolio Info

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    api = alp_api.REST()
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="Port",
        description="""Historical Portfolio Info""",
    )
    parser.add_argument(
        "-p",
        "--period",
        dest="period",
        type=str,
        default="1M",
        help="Duration of data (<number> + <unit>)",
    )
    parser.add_argument(
        "-t",
        "--timeframe",
        dest="timeframe",
        default="1D",
        type=str,
        help="Resolution of data (<number> + <unit>)",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        port_hist = api.get_portfolio_history(
            period=ns_parser.period, timeframe=ns_parser.timeframe
        ).df

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
        plt.plot(port_hist.index, port_hist.equity)
        plt.xlim(port_hist.index[0], port_hist.index[-1])
        plt.ylabel("Equity")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        plt.show()

        if gtff.USE_ION:
            plt.ion()
        print("")

    except Exception as e:
        print(e, "\n")
