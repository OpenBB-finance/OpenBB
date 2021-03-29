""" Seeking Alpha View """
__docformat__ = "numpy"

import argparse
from typing import List
import requests
from bs4 import BeautifulSoup
import pandas as pd
from gamestonk_terminal.helper_funcs import (
    check_positive,
    get_user_agent,
    parse_known_args_and_warn,
)


def earnings_release_dates_view(other_args: List[str]):
    """Prints a data frame with earnings release dates

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-p", "20", "-n", "5"]
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        prog="up_earnings",
        description="""Upcoming earnings release dates. [Source: Seeking Alpha]""",
    )

    parser.add_argument(
        "-p",
        "--pages",
        action="store",
        dest="n_pages",
        type=check_positive,
        default=10,
        help="Number of pages to read upcoming earnings from in Seeking Alpha website.",
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=3,
        help="Number of upcoming earnings release dates to print",
    )

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    l_earnings = list()
    for idx in range(0, ns_parser.n_pages):
        if idx == 0:
            url_next_earnings = "https://seekingalpha.com/earnings/earnings-calendar"
        else:
            url_next_earnings = (
                f"https://seekingalpha.com/earnings/earnings-calendar/{idx+1}"
            )
        text_soup_earnings = BeautifulSoup(
            requests.get(
                url_next_earnings, headers={"User-Agent": get_user_agent()}
            ).text,
            "lxml",
        )

        for bs_stock in text_soup_earnings.findAll("tr", {"data-exchange": "NASDAQ"}):
            l_stock = list()
            for stock in bs_stock.contents[:3]:
                l_stock.append(stock.text)
            l_earnings.append(l_stock)

    df_earnings = pd.DataFrame(l_earnings, columns=["Ticker", "Name", "Date"])
    df_earnings["Date"] = pd.to_datetime(df_earnings["Date"])
    df_earnings = df_earnings.set_index("Date")

    pd.set_option("display.max_colwidth", None)
    for n_days, earning_date in enumerate(df_earnings.index.unique()):
        if n_days > (ns_parser.n_num - 1):
            break

        print(f"Earning Release on {earning_date.date()}")
        print("----------------------------------------------")
        print(
            df_earnings[earning_date == df_earnings.index][
                ["Ticker", "Name"]
            ].to_string(index=False, header=False)
        )
        print("")
