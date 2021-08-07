""" Financial Modeling Prep View """
__docformat__ = "numpy"

import argparse
from typing import List
from tabulate import tabulate
import FundamentalAnalysis as fa
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn, check_positive


def rating(other_args: List[str], ticker: str):
    """Display ratings for a given ticker

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Stock ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="rating",
        description="""
            Based on specific ratios, prints information whether the company
            is a (strong) buy, neutral or a (strong) sell. The following fields are expected:
            P/B, ROA, DCF, P/E, ROE, and D/E. [Source: Financial Modeling Prep]
        """,
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="number of regions to plot that show highest interest.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_fa = fa.rating(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

        # TODO: This could be displayed in a nice rating plot over time

        l_recoms = [col for col in df_fa.columns if "Recommendation" in col]
        l_recoms_show = [
            recom.replace("rating", "")
            .replace("Details", "")
            .replace("Recommendation", " Recommendation")
            for recom in l_recoms
        ]
        print(
            tabulate(
                df_fa[l_recoms].head(ns_parser.n_num),
                headers=l_recoms_show,
                floatfmt=".2f",
                showindex=True,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except KeyError:
        print(
            f"Financialmodelingprep.com is returning empty response the ticker {ticker}."
        )
        print("")
        return

    except Exception as e:
        print(e)
        print("")
        return
