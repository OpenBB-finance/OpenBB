""" Finviz View """
__docformat__ = "numpy"

import argparse
from typing import List
import webbrowser
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn
from finvizfinance.group import valuation, performance, spectrum
from PIL import Image


def map_sp500_view(other_args: List[str]):
    """Opens Finviz website in a browser

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-p", "6m", "-t", "sp500"]
    """

    parser = argparse.ArgumentParser(
        add_help=False,
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

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    webbrowser.open(
        f"https://finviz.com/map.ashx?t={d_type[ns_parser.s_type]}&st={d_period[ns_parser.s_period]}"
    )
    print("")


def get_valuation_performance_data(group: str, data_type: str):
    """Get group (sectors, industry or country) valuation/performance data

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    group : str
        select group to see data between sectors, industry or country
    data_type : str
        select data type to see data between valuation or performance

    Returns
    ----------
    pd.DataFrame
        dataframe with valuation/performance data
    """
    if data_type == "valuation":
        df_group = valuation.Valuation().ScreenerView(group=group)
    elif data_type == "performance":
        df_group = performance.Performance().ScreenerView(group=group)

    return df_group


def get_spectrum_data(group: str):
    """Get group (sectors, industry or country) valuation/performance data

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    group : str
        select group to see data between sectors, industry or country
    data_type : str
        select data type to see data between valuation or performance
    """
    spectrum.Spectrum().ScreenerView(group=group)


def view_group_data(other_args: List[str], group: str, data_type: str):
    """View group (sectors, industry or country) valuation/performance/spectrum data

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    group : str
        select group to see data between sectors, industry and country
    data_type : str
        select data type to see data between valuation, performance and spectrum
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="group_data",
        description="""
            View group (sectors, industry or country) valuation/performance/spectrum data. [Source: Finviz]
        """,
    )
    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    if data_type == "valuation":
        df_group = get_valuation_performance_data(group, "valuation")
        print(df_group.to_string())

    elif data_type == "performance":
        df_group = get_valuation_performance_data(group, "performance")
        print(df_group.to_string())

    elif data_type == "spectrum":
        get_spectrum_data(group)

        img = Image.open(group + ".jpg")
        img.show()
    else:
        print("Invalid data type. Choose between valuation, performance and spectrum.")

    print("")
