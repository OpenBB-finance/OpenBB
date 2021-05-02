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
from gamestonk_terminal.config_terminal import API_FRED_KEY
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
        """,
    )

    parser.add_argument(
        "-i",
        "--id",
        dest="series_id",
        required=bool(choice),
        type=str,
        default=choice.upper(),
        help="FRED Series ID from https://fred.stlouisfed.org",
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

        fred = Fred(api_key=API_FRED_KEY)
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
            plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
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
