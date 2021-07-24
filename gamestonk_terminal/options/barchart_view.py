"""Helper functions for scraping options data"""
__docformat__ = "numpy"

import argparse
from typing import List

import requests
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate

from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


def print_options_data(stock: str, other_args: List[str]):
    """Scrapes Barchart.com for the options information

    Parameters
    ----------
    stock: str
        Ticker to get options info for
    other_args: List[str]
        Other arguments.  Currently just accepts a browser flag for selenium
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="info",
        description="Display option data [Source: Barchart.com]",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        page = f"https://www.barchart.com/stocks/quotes/{stock}/overview"

        r = requests.get(page, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        tags = soup.find(
            "div",
            attrs={
                "class": "barchart-content-block symbol-fundamentals bc-cot-table-wrapper"
            },
        )
        data = tags.find_all("li")
        labels = []
        values = []
        for row in data:
            labels.append(row.find_all("span")[0].getText())
            values.append(row.find_all("span")[1].getText())

        df = pd.DataFrame(data=[labels, values]).T
        print(tabulate(df, tablefmt="fancy_grid", showindex=False))
        print("")

    except Exception as e:
        print(e, "\n")
