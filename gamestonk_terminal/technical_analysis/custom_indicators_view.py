"""Custom TA indicators"""
__docformat__ = "numpy"

import argparse
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
    valid_date,
)

from gamestonk_terminal import config_plot as cfp
from gamestonk_terminal import feature_flags as gtff


def fibinocci_retracement(other_args: List[str], data: pd.DataFrame, ticker: str):
    """Calculate fibinocci retracement levels

    Parameters
    ----------
    other_args:List[str]
        Argparse arguments
    data: pd.DataFrame
        Stock data
    ticker:str
        Stock ticker
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="fib",
        description="Calculates the fibinocci retracement levels",
    )
    parser.add_argument(
        "-p",
        "--period",
        dest="period",
        type=int,
        help="Days to lookback for retracement",
        default=120,
    )

    parser.add_argument(
        "--start",
        dest="start",
        type=valid_date,
        help="Starting date to select",
        required="--end" in other_args,
    )

    parser.add_argument(
        "--end",
        dest="end",
        type=valid_date,
        help="Ending date to select",
        required="--start" in other_args,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.start and ns_parser.end:

            if ns_parser.start not in data.index:
                date0 = data.index[
                    data.index.get_loc(ns_parser.start, method="nearest")
                ]
                print(f"Start date not in data.  Using nearest: {date0}")
            else:
                date0 = ns_parser.start
            if ns_parser.end not in data.index:
                date1 = data.index[data.index.get_loc(ns_parser.end, method="nearest")]
                print(f"End date not in data.  Using nearest: {date1}")
            else:
                date1 = ns_parser.end

            data0 = data.loc[date0, "Adj Close"]
            data1 = data.loc[date1, "Adj Close"]

            min_pr = min(data0, data1)
            max_pr = max(data0, data1)

            if min_pr == data0:
                min_date = date0
                max_date = date1
            else:
                min_date = date1
                max_date = date0

        else:
            data_to_use = data.iloc[-ns_parser.period :]["Adj Close"]

            min_pr = data_to_use.min()
            min_date = data_to_use.idxmin()
            max_pr = data_to_use.max()
            max_date = data_to_use.idxmax()

        fib_levels = [0, 0.235, 0.382, 0.5, 0.618, 1]
        price_dif = max_pr - min_pr

        levels = [round(max_pr - price_dif * f_lev, 2) for f_lev in fib_levels]

        df = pd.DataFrame()
        df["Level"] = fib_levels
        df["Level"] = df["Level"].apply(lambda x: str(x * 100) + "%")
        df["Price"] = levels

        fig, ax = plt.subplots(figsize=(plot_autoscale()), dpi=cfp.PLOT_DPI)

        ax.plot(data["Adj Close"], "b")
        ax.plot([min_date, max_date], [min_pr, max_pr], c="k")

        for i in levels:
            ax.axhline(y=i, c="g", alpha=0.5)

        for i in range(5):
            ax.fill_between(data.index, levels[i], levels[i + 1], alpha=0.6)

        ax.set_ylabel("Price")
        ax.set_title(f"Fibonacci Support for {ticker.upper()}")
        ax.set_xlim(data.index[0], data.index[-1])

        ax1 = ax.twinx()
        ax1.set_ylim(ax.get_ylim())
        ax1.set_yticks(levels)
        ax1.set_yticklabels(fib_levels)

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)

        if gtff.USE_ION:
            plt.ion()
        plt.show()

        print(
            tabulate(
                df,
                headers=["Fib Level", "Price"],
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")
