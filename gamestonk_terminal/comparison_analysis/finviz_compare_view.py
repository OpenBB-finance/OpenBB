""" Finviz View """
__docformat__ = "numpy"

import argparse
from typing import List
import pandas as pd
from finvizfinance.screener import (
    technical,
    overview,
    valuation,
    financial,
    ownership,
    performance,
)
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
)


def get_comparison_data(data_type: str, similar: List[str]):
    """Screener Overview

    Parameters
    ----------
    data_type : str
        Data type between: overview, valuation, financial, ownership, performance, technical

    Returns
    ----------
    pd.DataFrame
        Dataframe with overview, valuation, financial, ownership, performance or technical
    """
    if data_type == "overview":
        screen = overview.Overview()
    elif data_type == "valuation":
        screen = valuation.Valuation()
    elif data_type == "financial":
        screen = financial.Financial()
    elif data_type == "ownership":
        screen = ownership.Ownership()
    elif data_type == "performance":
        screen = performance.Performance()
    elif data_type == "technical":
        screen = technical.Technical()
    else:
        print("Invalid selected screener type")
        return pd.DataFrame()

    screen.set_filter(ticker=",".join(similar))
    df_screen = screen.ScreenerView(verbose=0)

    return df_screen


def screener(other_args: List[str], data_type: str, ticker: str, similar: List[str]):
    """Screener

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    data_type : str
        Data type string between: overview, valuation, financial, ownership, performance, technical
    ticker : str
        Main ticker to compare income
    similar : List[str]
        Similar companies to compare income with
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog=data_type,
        description="""
            Prints screener data of similar companies. [Source: Finviz]
        """,
    )
    parser.add_argument(
        "-s",
        "--similar",
        dest="l_similar",
        type=lambda s: [str(item).upper() for item in s.split(",")],
        default=similar,
        help="similar companies to compare with.",
    )
    parser.add_argument(
        "-a",
        "--also",
        dest="l_also",
        type=lambda s: [str(item).upper() for item in s.split(",")],
        default=[],
        help="apart from loaded similar companies also compare with.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        l_similar = ns_parser.l_similar
        l_similar += ns_parser.l_also

        # Add main ticker to similar list of companies
        l_similar = [ticker] + l_similar

        df_screen = get_comparison_data(data_type, l_similar)

        if not df_screen.empty:
            print(df_screen.to_string())
        print("")

    except Exception as e:
        print(e, "\n")
