""" Financial Modeling Prep View """
__docformat__ = "numpy"

import argparse
from typing import List
import FundamentalAnalysis as fa  # Financial Modeling Prep
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_fa = fa.rating(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
        print(df_fa)

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
