import argparse
import textwrap
from typing import List
import itertools
from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import check_positive, parse_known_args_and_warn

d_open_insider = {
    "lcb": "latest-cluster-buys",
    "lpsb": "latest-penny-stock-buys",
    "lit": "latest-insider-trading",
    "lip": "insider-purchases",
    "blip": "latest-insider-purchases-25k",
    "blop": "latest-officer-purchases-25k",
    "blcp": "latest-ceo-cfo-purchases-25k",
    "lis": "insider-sales",
    "blis": "latest-insider-sales-100k",
    "blos": "latest-officer-sales-100k",
    "blcs": "latest-ceo-cfo-sales-100k",
    "topt": "top-officer-purchases-of-the-day",
    "toppw": "top-officer-purchases-of-the-week",
    "toppm": "top-officer-purchases-of-the-month",
    "tipt": "top-insider-purchases-of-the-day",
    "tippw": "top-insider-purchases-of-the-week",
    "tippm": "top-insider-purchases-of-the-month",
    "tist": "top-insider-sales-of-the-day",
    "tispw": "top-insider-sales-of-the-week",
    "tispm": "top-insider-sales-of-the-month",
}

d_notes = {
    "A": "A: Amended filing",
    "D": "D: Derivative transaction in filing (usually option exercise)",
    "E": "E: Error detected in filing",
    "M": "M: Multiple transactions in filing; earliest reported transaction date and weighted average transaction price",
}


def print_insider_data(other_args: List[str], type_insider: str):
    """Corporate lobbying details

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    type_insider: str
        Insider type of data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog=type_insider,
        description=f"Print {d_open_insider[type_insider].replace('-', ' ')} [Source: OpenInsider]",
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="num",
        type=check_positive,
        default=20,
        help="Number of datarows to display",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        response = requests.get(
            f"http://openinsider.com/{d_open_insider[type_insider]}"
        )
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"class": "tinytable"})

        if not table:
            print("No insider information found", "\n")
            return

        table_rows = table.find_all("tr")

        res = []
        for tr in table_rows:
            td = tr.find_all("td")
            row = [tr.text.strip() for tr in td if tr.text.strip()]
            res.append(row)

        df = pd.DataFrame(res).dropna().head(n=ns_parser.num)

        df.columns = [
            "X",
            "Filing Date",
            "Trade Date",
            "Ticker",
            "Company Name",
            "Industry" if type_insider == "lcb" else "Insider Name",
            "Title",
            "Trade Type",
            "Price",
            "Qty",
            "Owned",
            "Diff Own",
            "Value",
        ]

        df["Filing Date"] = df["Filing Date"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=10)) if isinstance(x, str) else x
        )
        df["Company Name"] = df["Company Name"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=20)) if isinstance(x, str) else x
        )
        df["Title"] = df["Title"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=10)) if isinstance(x, str) else x
        )
        if type_insider == "lcb":
            df["Industry"] = df["Industry"].apply(
                lambda x: "\n".join(textwrap.wrap(x, width=20))
                if isinstance(x, str)
                else x
            )
        else:
            df["Insider Name"] = df["Insider Name"].apply(
                lambda x: "\n".join(textwrap.wrap(x, width=20))
                if isinstance(x, str)
                else x
            )

        print(
            tabulate(
                df,
                headers=df.columns,
                tablefmt="fancy_grid",
                stralign="right",
                showindex=False,
            )
        )
        l_chars = [list(chars) for chars in df["X"].values]
        l_uchars = np.unique(list(itertools.chain(*l_chars)))

        for char in l_uchars:
            print(d_notes[char])
        print("")

    except Exception as e:
        print(e, "\n")
