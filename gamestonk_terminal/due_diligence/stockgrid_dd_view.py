"""Stockgrid DD View"""
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import timedelta
import requests
import pandas as pd
import matplotlib.pyplot as plt
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.feature_flags import USE_ION
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn, plot_autoscale


def shortview(ticker: str, other_args: List[str]):
    """
    Plot price vs short volume over last year
    Parameters
    ----------
    ticker: str
        Stock to plot for
    other_args : List[str]
        Argparse arguments

    """

    parser = argparse.ArgumentParser(
        prog="shortview", add_help=False, description="Shows price vs short interest"
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        link = f"https://stockgridapp.herokuapp.com/get_dark_pool_individual_data?ticker={ticker}"
        response = requests.get(link)
        response.json().keys()
        df1 = pd.DataFrame(response.json()["individual_dark_pool_position_data"])
        df2 = pd.DataFrame(response.json()["individual_short_volume"])
        prices = response.json()["prices"]["prices"]

        dates = pd.to_datetime(df1.dates)

        fig = plt.figure(figsize=(plot_autoscale()), dpi=PLOT_DPI)

        ax = fig.add_subplot(111)

        ax.bar(
            dates,
            df2["total_volume"],
            width=timedelta(days=1),
            color="b",
            alpha=0.4,
            label="Total Volume",
        )
        ax.bar(
            dates,
            df2["short_volume"],
            width=timedelta(days=1),
            color="r",
            alpha=0.4,
            label="Short Volume",
        )

        ax.set_ylabel("Volume")
        ax2 = ax.twinx()

        ax2.plot(dates, prices, c="k", label="Price")
        ax2.set_ylabel("Price ($)")

        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc="upper left")

        ax.set_xlim(dates[0], dates[251])

        ax.grid(b=True, which="major", color="#666666", linestyle="-")
        ax.minorticks_on()
        ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        plt.suptitle(f"Price vs Short Volume for {ticker}")
        plt.gcf().autofmt_xdate()
        if USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
