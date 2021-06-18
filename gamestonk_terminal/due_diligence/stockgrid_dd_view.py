"""Stockgrid DD View"""
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import timedelta
import requests
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.feature_flags import USE_ION
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
    check_positive,
)


def shortview(ticker: str, other_args: List[str]):
    """Plot price vs short interest volume

    Parameters
    ----------
    ticker: str
        Stock to plot for
    other_args : List[str]
        Argparse arguments

    """
    parser = argparse.ArgumentParser(
        prog="shortvol",
        add_help=False,
        description="Shows price vs short interest volume. [Source: Stockgrid]",
    )
    parser.add_argument(
        "-n",
        "--number",
        help="Number of last open market days to show",
        type=check_positive,
        default=10 if "-r" in other_args else 120,
        dest="num",
    )
    parser.add_argument(
        "-r",
        action="store_true",
        default=False,
        help="Flag to print raw data instead",
        dest="raw",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        link = f"https://stockgridapp.herokuapp.com/get_dark_pool_individual_data?ticker={ticker}"
        response = requests.get(link)

        df = pd.DataFrame(response.json()["individual_short_volume_table"]["data"])
        df["date"] = pd.to_datetime(df["date"])

        if ns_parser.raw:
            df = df.sort_values(by="date", ascending=False)

            df["Short Vol. (1M)"] = df["short_volume"] / 1_000_000
            df["Short Vol. %"] = df["short_volume%"] * 100
            df["Short Exempt Vol. (1K)"] = df["short_exempt_volume"] / 1_000
            df["Total Vol. (1M)"] = df["total_volume"] / 1_000_000

            df = df[
                [
                    "date",
                    "Short Vol. (1M)",
                    "Short Vol. %",
                    "Short Exempt Vol. (1K)",
                    "Total Vol. (1M)",
                ]
            ]

            df.date = df.date.dt.date

            print(
                tabulate(
                    df.iloc[: ns_parser.num],
                    tablefmt="fancy_grid",
                    floatfmt=".2f",
                    headers=list(df.columns),
                    showindex=False,
                )
            )
        else:
            prices = response.json()["prices"]["prices"]

            fig = plt.figure(figsize=(plot_autoscale()), dpi=PLOT_DPI)

            ax = fig.add_subplot(111)
            ax.bar(
                df["date"],
                df["total_volume"],
                width=timedelta(days=1),
                color="b",
                alpha=0.4,
                label="Total Volume",
            )
            ax.bar(
                df["date"],
                df["short_volume"],
                width=timedelta(days=1),
                color="r",
                alpha=0.4,
                label="Short Volume",
            )

            ax.set_ylabel("Volume")
            ax2 = ax.twinx()
            ax2.plot(
                df["date"].values, prices[len(prices) - len(df) :], c="k", label="Price"
            )
            ax2.set_ylabel("Price ($)")

            ax3 = ax.twinx()
            ax3.plot(
                df["date"].values,
                100 * df["short_volume%"],
                c="green",
                label="Short Vol. %",
            )
            ax3.set_ylabel("Short Volume %")
            ax3.spines["right"].set_position(("outward", 50))
            ax3.yaxis.label.set_color("green")

            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            lines3, labels3 = ax3.get_legend_handles_labels()
            ax3.legend(
                lines + lines2 + lines3, labels + labels2 + labels3, loc="upper left"
            )

            ax.set_xlim(
                df["date"].values[max(0, len(df) - ns_parser.num)],
                df["date"].values[len(df) - 1],
            )

            ax.grid(b=True, which="major", color="#666666", linestyle="-")
            ax.minorticks_on()
            ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
            plt.suptitle(f"Price vs Short Volume Interest for {ticker}")
            plt.gcf().autofmt_xdate()
            if USE_ION:
                plt.ion()

            plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
