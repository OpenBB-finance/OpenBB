""" Fred View """
__docformat__ = "numpy"

import argparse
from typing import List
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
from fredapi import Fred
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    valid_date,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()


fred_series_description = {
    "VIXCLS": "Volatility Index",
    "GDP": "Gross Domestic Product",
    "UNRATE": "Unemployment Rate",
    "DGS1": "1-Year Treasury Constant Maturity Rate",
    "DGS5": "5-Year Treasury Constant Maturity Rate",
    "DGS10": "10-Year Treasury Constant Maturity Rate",
    "DGS30": "30-Year Treasury Constant Maturity Rate",
    "MORTGAGE30US": "30-Year Mortgage Rate",
    "FEDFUNDS": "Effective Federal Funds Rate",
    "AAA": "Moody's Seasoned AAA Corporate Bond Yield",
    "DEXCAUS": "Canada / U.S. Foreign Exchange Rate",
}


def display_fred(other_args: List[str], choice: str):
    """Display customized Federal Reserve Economic Data (FRED) from https://fred.stlouisfed.org.
    It is possible to display multiple series.

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    choice : str
        Fred data series: "VIXCLS", "GDP", "DGS1", "DGS5", "DGS10", "DGS30", "MORTGAGE30US", "FEDFUNDS",
        "AAA", "DEXCAUS", "UNRATE",
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        prog=choice if choice else "fred",
        description="""
            Display customized Federal Reserve Economic Data (FRED) from https://fred.stlouisfed.org.
            It is possible to display multiple series.
        """,
    )

    parser.add_argument(
        "-i",
        "--id",
        dest="series_id",
        required=not bool(choice) and "-h" not in other_args,
        type=str,
        default=choice.upper(),
        help="FRED Series ID from https://fred.stlouisfed.org. For multiple series use: series1,series2,series3",
    )

    parser.add_argument(
        "-s",
        dest="start_date",
        type=valid_date,
        default="2019-01-01",
        help="Starting date (YYYY-MM-DD) of data",
    )

    parser.add_argument(
        "-t",
        "--text",
        action="store_true",
        dest="text",
        help="Only output text data",
    )

    try:
        if not choice:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        fred = Fred(api_key=cfg.API_FRED_KEY)

        if "," in ns_parser.series_id:
            if not ns_parser.text:
                l_colors = [
                    "tab:blue",
                    "tab:orange",
                    "tab:green",
                    "tab:red",
                    "tab:purple",
                    "tab:brown",
                    "tab:pink",
                    "tab:gray",
                    "tab:olive",
                    "tab:cyan",
                ]
                l_ts_start = list()
                l_ts_end = list()
                p = {}
                _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
                ax.axes.get_yaxis().set_visible(False)
                plt.subplots_adjust(right=0.9 - ns_parser.series_id.count(",") * 0.1)

            series = ns_parser.series_id.split(",")

            success = -1
            success_series = list()
            for series_id in series:
                try:
                    d_data = fred.get_series(series_id, ns_parser.start_date)
                    success += 1
                    success_series.append(series_id.upper())
                except Exception:
                    print(f"Series '{series_id}' doesn't exist!")
                    continue

                df_fred = pd.DataFrame(d_data, columns=[f"{series_id}"])
                df_fred.index.name = "Date"

                if ns_parser.text:
                    print(df_fred.dropna().to_string(), "\n")

                else:
                    axes = ax.twinx()
                    axes.spines["right"].set_position(("axes", 1 + success * 0.15))
                    axes.spines["right"].set_color(l_colors[success])
                    (p[success],) = axes.plot(
                        df_fred.index,
                        df_fred.iloc[:, 0],
                        c=l_colors[success],
                        label=series_id.upper(),
                    )

                    axes.yaxis.label.set_color(l_colors[success])

                    l_ts_start.append(df_fred.index[0])
                    l_ts_end.append(df_fred.index[-1])

            if not ns_parser.text and success:
                plt.title("FRED: " + ", ".join(success_series))
                plt.xlim(min(l_ts_start), max(l_ts_end))
                plt.gcf().autofmt_xdate()
                plt.xlabel("Time")
                plt.legend([val for _, val in p.items()], success_series)
                plt.gca().spines["left"].set_visible(False)
                plt.show()
            print("")

        else:
            d_data = fred.get_series(ns_parser.series_id, ns_parser.start_date)

            df_fred = pd.DataFrame(d_data, columns=[f"{ns_parser.series_id}"])
            df_fred.index.name = "Date"

            if ns_parser.text:
                print(df_fred.to_string())

            else:
                plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
                plt.plot(df_fred.index, df_fred.iloc[:, 0])
                plt.xlabel("Time")
                plt.xlim(df_fred.index[0], df_fred.index[-1])
                plt.ylabel(f"{ns_parser.series_id.upper()}")
                plt.grid(b=True, which="major", color="#666666", linestyle="-")
                plt.minorticks_on()
                plt.grid(
                    b=True, which="minor", color="#999999", linestyle="-", alpha=0.2
                )
                if choice:
                    plt.title(fred_series_description[ns_parser.series_id])
                if gtff.USE_ION:
                    plt.ion()
                plt.show()
            print("")

    except SystemExit:
        print("")
    except Exception as e:
        print(e, "\n")
        return
