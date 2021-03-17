import argparse
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

api_map = {
    "gdp": "GDP",
    "t10": "DGS10",
    "t1": "DGS1",
    "t5": "DGS5",
    "t30": "DGS30",
    "mort30": "MORTGAGE30US",
    "fedrate": "FEDFUNDS",
    "moodAAA": "AAA",
    "usdcad": "DEXCAUS",
    "unemp": "UNRATE",
}
title_map = {
    "gdp": "Gross Domestic Product",
    "t10": "10-Year Treasury Constant Maturity Rate",
    "t1": "1-Year Treasury Constant Maturity Rate",
    "t5": "5-Year Treasury Constant Maturity Rate",
    "t30": "30-Year Treasury Constant Maturity Rate",
    "mort30": "30-Year Mortgage Rate",
    "fedrate": "Effective Federal Funds Rate",
    "moodAAA": "Moody's Seasoned AAA Corporate Bond Yield",
    "usdcad": "Canada / U.S. Foreign Exchange Rate",
    "unemp": "Unemployment Rate",
}


def get_fred_data(l_args, choice):
    fred = Fred(api_key=API_FRED_KEY)

    parser = argparse.ArgumentParser(
        add_help=False,
        prog="Custom",
        description="""
                        Custom Data
                    """,
    )

    parser.add_argument(
        "-s",
        dest="start_date",
        type=valid_date,
        default="2019-01-01",
        required=False,
        help="Starting date (YYYY-MM-DD) of data",
    )

    parser.add_argument(
        "--noplot",
        action="store_false",
        default=True,
        dest="noplot",
        help="Suppress output plot",
    )

    parser.add_argument(
        "--hidedata",
        action="store_false",
        default=True,
        dest="hidedata",
        help="Suppress data display plot",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)

        if not ns_parser:
            return

        string_to_get = api_map[choice]
        title = title_map[choice]
        data = fred.get_series(string_to_get, ns_parser.start_date)

        data = pd.DataFrame(data, columns=[f"{string_to_get}"])
        data.index.name = "Date"
        if ns_parser.hidedata:
            print(data)
            print("")
        if ns_parser.noplot:
            plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
            plt.plot(data.index, data.iloc[:, 0], "-ok")
            plt.xlabel("Time")
            plt.xlim(data.index[0], data.index[-1])
            plt.ylabel(f"{string_to_get}")
            plt.grid(b=True, which="major", color="#666666", linestyle="-")
            plt.minorticks_on()
            plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
            plt.title(title)
            plt.show()
            print("")

            if gtff.USE_ION:
                plt.ion()

    except SystemExit:
        print("")
    except Exception as e:
        print(e)
        print("")
        return


def custom_data(l_args):
    fred = Fred(api_key=API_FRED_KEY)

    parser = argparse.ArgumentParser(
        add_help=False,
        prog="Custom",
        description="""
                    Custom Data
                """,
    )
    parser.add_argument(
        "-i", "--id", dest="series_id", required=True, type=str, help="FRED Series ID"
    )

    parser.add_argument(
        "-s",
        dest="start_date",
        type=valid_date,
        default="2019-01-01",
        required=False,
        help="Starting date (YYYY-MM-DD) of data",
    )

    parser.add_argument(
        "--noplot",
        action="store_false",
        default=True,
        dest="noplot",
        help="Suppress output plot",
    )

    parser.add_argument(
        "--hidedata",
        action="store_false",
        default=True,
        dest="hidedata",
        help="Suppress data display plot",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)

        if not ns_parser:
            return

        data = fred.get_series(ns_parser.series_id, ns_parser.start_date)

        data = pd.DataFrame(data, columns=[f"{ns_parser.series_id}"])
        data.index.name = "Date"
        if ns_parser.hidedata:
            print(data)
            print("")
        if ns_parser.noplot:
            plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
            plt.plot(data.index, data.iloc[:, 0], "-ok")
            plt.xlabel("Time")
            plt.xlim(data.index[0], data.index[-1])
            plt.ylabel(f"{ns_parser.series_id}")
            plt.grid(b=True, which="major", color="#666666", linestyle="-")
            plt.minorticks_on()
            plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
            plt.title(f"FRED {ns_parser.series_id} Series")
            plt.show()
            print("")

            if gtff.USE_ION:
                plt.ion()

    except SystemExit:
        print("")
    except Exception as e:
        print(e)
        print("")
        return
