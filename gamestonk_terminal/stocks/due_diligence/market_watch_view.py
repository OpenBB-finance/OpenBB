""" Market Watch View """
__docformat__ = "numpy"

import argparse
from typing import List
import requests
import pandas as pd
from bs4 import BeautifulSoup
from gamestonk_terminal.helper_funcs import (
    check_positive,
    get_user_agent,
    parse_known_args_and_warn,
)

# pylint: disable=too-many-branches


def sec_fillings(other_args: List[str], ticker: str):
    """Display SEC filings for a given stock ticker

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-n", "10"]
    ticker : str
        Stock ticker
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        prog="sec",
        description="""
            Prints SEC filings of the company. The following fields are expected: Filing Date,
            Document Date, Type, Category, Amended, and Link. [Source: Market Watch]
        """,
    )

    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=5,
        help="number of latest SEC filings.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pd.set_option("display.max_colwidth", None)

        url_financials = f"https://www.marketwatch.com/investing/stock/{ticker}/financials/secfilings"

        text_soup_financials = BeautifulSoup(
            requests.get(url_financials, headers={"User-Agent": get_user_agent()}).text,
            "lxml",
        )

        # a_financials_header = []
        df_financials = None
        b_ready_to_process_info = False
        soup_financials = text_soup_financials.findAll("tr", {"class": "table__row"})
        for financials_info in soup_financials:
            a_financials = financials_info.text.split("\n")

            # If header has been processed and dataframe created ready to populate the SEC information
            if b_ready_to_process_info:
                l_financials_info = [a_financials[2]]
                l_financials_info.extend(a_financials[5:-1])
                l_financials_info.append(financials_info.a["href"])
                # Append data values to financials
                df_financials.loc[len(df_financials.index)] = l_financials_info  # type: ignore

            if "Filing Date" in a_financials:
                l_financials_header = [a_financials[2]]
                l_financials_header.extend(a_financials[5:-1])
                l_financials_header.append("Link")

                df_financials = pd.DataFrame(columns=l_financials_header)
                df_financials.set_index("Filing Date")
                b_ready_to_process_info = True

        # Set Filing Date as index
        df_financials = df_financials.set_index("Filing Date")  # type: ignore

        print(df_financials.head(n=ns_parser.n_num).to_string())
        print("")

    except Exception as e:
        print(e)
        print("")
        return
