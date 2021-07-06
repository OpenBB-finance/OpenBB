"""Stockgrid DD View"""
__docformat__ = "numpy"

import argparse
import os
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
    export_data,
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
    parser.add_argument(
        "--export",
        choices=["csv", "json", "xlsx"],
        default="",
        dest="export",
        help="Export dataframe data to csv,json,xlsx file",
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

            _, axes = plt.subplots(
                2,
                1,
                figsize=(plot_autoscale()),
                dpi=PLOT_DPI,
                gridspec_kw={"height_ratios": [2, 1]},
            )

            axes[0].bar(
                df["date"],
                df["total_volume"] / 1_000_000,
                width=timedelta(days=1),
                color="b",
                alpha=0.4,
                label="Total Volume",
            )
            axes[0].bar(
                df["date"],
                df["short_volume"] / 1_000_000,
                width=timedelta(days=1),
                color="r",
                alpha=0.4,
                label="Short Volume",
            )

            axes[0].set_ylabel("Volume (1M)")
            ax2 = axes[0].twinx()
            ax2.plot(
                df["date"].values, prices[len(prices) - len(df) :], c="k", label="Price"
            )
            ax2.set_ylabel("Price ($)")

            lines, labels = axes[0].get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(lines + lines2, labels + labels2, loc="upper left")

            axes[0].set_xlim(
                df["date"].values[max(0, len(df) - ns_parser.num)],
                df["date"].values[len(df) - 1],
            )

            axes[0].grid()
            axes[0].ticklabel_format(style="plain", axis="y")
            plt.title(f"Price vs Short Volume Interest for {ticker}")
            plt.gcf().autofmt_xdate()

            axes[1].plot(
                df["date"].values,
                100 * df["short_volume%"],
                c="green",
                label="Short Vol. %",
            )

            axes[1].set_xlim(
                df["date"].values[max(0, len(df) - ns_parser.num)],
                df["date"].values[len(df) - 1],
            )
            axes[1].set_ylabel("Short Vol. %")

            axes[1].grid(axis="y")
            lines, labels = axes[1].get_legend_handles_labels()
            axes[1].legend(lines, labels, loc="upper left")
            axes[1].set_ylim([0, 100])

            if USE_ION:
                plt.ion()

            plt.show()
        print("")

        export_data(
            ns_parser.export,
            os.path.dirname(os.path.abspath(__file__)),
            "shortview",
            df,
        )

    except Exception as e:
        print(e, "\n")


def darkpos(ticker: str, other_args: List[str]):
    """Plot dark pool position

    Parameters
    ----------
    ticker: str
        Stock to plot for
    other_args : List[str]
        Argparse arguments

    """
    parser = argparse.ArgumentParser(
        prog="darkpos",
        add_help=False,
        description="Shows Net Short Vol. vs Position. [Source: Stockgrid]",
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
    parser.add_argument(
        "--export",
        choices=["csv", "json", "xlsx"],
        default="",
        dest="export",
        help="Export dataframe data to csv,json,xlsx file",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        link = f"https://stockgridapp.herokuapp.com/get_dark_pool_individual_data?ticker={ticker}"
        response = requests.get(link)

        df = pd.DataFrame(response.json()["individual_dark_pool_position_data"])
        df["dates"] = pd.to_datetime(df["dates"])

        if ns_parser.raw:
            df = df.sort_values(by="dates", ascending=False)

            df["Net Short Vol. (1k $)"] = df["dollar_net_volume"] / 1_000
            df["Position (1M $)"] = df["dollar_dp_position"]

            df = df[
                [
                    "dates",
                    "Net Short Vol. (1k $)",
                    "Position (1M $)",
                ]
            ]

            df["dates"] = df["dates"].dt.date

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
            fig = plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

            ax = fig.add_subplot(111)
            ax.bar(
                df["dates"],
                df["dollar_net_volume"] / 1_000,
                color="r",
                alpha=0.4,
                label="Net Short Vol. (1k $)",
            )
            ax.set_ylabel("Net Short Vol. (1k $)")

            ax2 = ax.twinx()
            ax2.plot(
                df["dates"].values,
                df["dollar_dp_position"],
                c="tab:blue",
                label="Position (1M $)",
            )
            ax2.set_ylabel("Position (1M $)")

            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(lines + lines2, labels + labels2, loc="upper left")

            ax.set_xlim(
                df["dates"].values[max(0, len(df) - ns_parser.num)],
                df["dates"].values[len(df) - 1],
            )

            ax.grid()
            plt.title(f"Net Short Vol. vs Position for {ticker}")
            plt.gcf().autofmt_xdate()

            if USE_ION:
                plt.ion()

            plt.show()
        print("")

        export_data(
            ns_parser.export,
            os.path.dirname(os.path.abspath(__file__)),
            "darkpos",
            df,
        )

    except Exception as e:
        print(e, "\n")
