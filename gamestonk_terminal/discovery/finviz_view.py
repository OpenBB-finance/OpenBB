""" Finviz View """
__docformat__ = "numpy"

import argparse
from typing import List
import webbrowser
from finvizfinance.group import valuation, performance, spectrum
from PIL import Image

from gamestonk_terminal.helper_funcs import parse_known_args_and_warn

l_GROUPS = [
    "Sector",
    "Industry",
    "Industry (Basic Materials)",
    "Industry (Communication Services)",
    "Industry (Consumer Cyclical)",
    "Industry (Consumer Defensive)",
    "Industry (Energy)",
    "Industry (Financial)",
    "Industry (Healthcare)",
    "Industry (Industrials)",
    "Industry (Real Estate)",
    "Industry (Technology)",
    "Industry (Utilities)",
    "Country (U.S. listed stocks only)",
    "Capitalization",
]


def map_sp500_view(other_args: List[str]):
    """Opens Finviz website in a browser

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="map",
        description="""
            Performance index stocks map categorized by sectors and industries.
            Size represents market cap. Opens web-browser. [Source: Finviz]
        """,
    )
    parser.add_argument(
        "-p",
        "--period",
        action="store",
        dest="s_period",
        type=str,
        default="1d",
        choices=["1d", "1w", "1m", "3m", "6m", "1y"],
        help="Performance period.",
    )
    parser.add_argument(
        "-t",
        "--type",
        action="store",
        dest="s_type",
        type=str,
        default="sp500",
        choices=["sp500", "world", "full", "etf"],
        help="Map filter type.",
    )

    # Conversion from period and type, to fit url requirements
    d_period = {"1d": "", "1w": "w1", "1m": "w4", "3m": "w13", "6m": "w26", "1y": "w52"}
    d_type = {"sp500": "sec", "world": "geo", "full": "sec_all", "etf": "etf"}

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        webbrowser.open(
            f"https://finviz.com/map.ashx?t={d_type[ns_parser.s_type]}&st={d_period[ns_parser.s_period]}"
        )
        print("")

    except Exception as e:
        print(e, "\n")


def get_valuation_performance_data(group: str, data_type: str):
    """Get group (sectors, industry or country) valuation/performance data

    Parameters
    ----------
    group : str
       sectors, industry or country
    data_type : str
       valuation or performance

    Returns
    ----------
    pd.DataFrame
        dataframe with valuation/performance data
    """
    if data_type == "valuation":
        return valuation.Valuation().ScreenerView(group=group)
    return performance.Performance().ScreenerView(group=group)


def get_spectrum_data(group: str):
    """Get group (sectors, industry or country) valuation/performance data

    Parameters
    ----------
    group : str
       sectors, industry or country
    """
    spectrum.Spectrum().ScreenerView(group=group)


def view_group_data(other_args: List[str], data_type: str):
    """View group (sectors, industry or country) valuation/performance/spectrum data

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    data_type : str
        select data type to see data between valuation, performance and spectrum
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="group_data",
        description="""
            View group (sectors, industry or country) valuation/performance/spectrum data. [Source: Finviz]
        """,
    )
    parser.add_argument(
        "-g",
        "--group",
        nargs="+",
        type=str,
        default="Sector",
        dest="group",
        help="Data group (sector, industry or country)",
        choices=l_GROUPS,
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-g")
            other_args = [other_args[0], " ".join(other_args[1:])]

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return ""

        if isinstance(ns_parser.group, List):
            ns_parser.group = ns_parser.group[0]

        if data_type in ("valuation", "performance"):
            df_group = get_valuation_performance_data(ns_parser.group, data_type)
            print(df_group.to_string())

        elif data_type == "spectrum":
            get_spectrum_data(ns_parser.group)

            img = Image.open(ns_parser.group + ".jpg")
            img.show()

            return ns_parser.group

        else:
            print(
                "Invalid data type. Choose between valuation, performance and spectrum."
            )
        print("")
        return ""

    except SystemExit:
        print("")
        return ""
