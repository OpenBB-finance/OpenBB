""" SEC View """
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_user_agent,
    check_positive,
    parse_known_args_and_warn,
)


def fails_to_deliver(other_args: List[str], ticker: str):
    """Display fails-to-deliver data for a given ticker

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-n", "10"]
    ticker : str
        Stock ticker
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        prog="ftd",
        description="""Prints latest fails-to-deliver data. [Source: SEC]""",
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="number of latest fails-to-deliver being printed",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        url_ftds = "https://www.sec.gov/data/foiadocsfailsdatahtm"
        text_soup_ftds = BeautifulSoup(
            requests.get(url_ftds, headers={"User-Agent": get_user_agent()}).text,
            "lxml",
        )

        table = text_soup_ftds.find("table", {"class": "list"})
        links = table.findAll("a")
        link_idx = 0
        ftds_data = pd.DataFrame()
        while len(ftds_data) < ns_parser.n_num:
            if link_idx > len(links):
                break
            link = links[link_idx]
            url = "https://www.sec.gov" + link["href"]
            all_ftds = pd.read_csv(
                url,
                compression="zip",
                sep="|",
                engine="python",
                skipfooter=2,
                usecols=[0, 2, 3, 5],
                dtype={"QUANTITY (FAILS)": "int"},
            )
            tmp_ftds = all_ftds[all_ftds["SYMBOL"] == ticker]
            del tmp_ftds["PRICE"]
            del tmp_ftds["SYMBOL"]
            # merge the data from this archive
            ftds_data = pd.concat([ftds_data, tmp_ftds], ignore_index=True)
            link_idx += 1

        # clip away extra rows
        ftds_data = ftds_data.sort_values("SETTLEMENT DATE")[-ns_parser.n_num :]
        ftds_data["SETTLEMENT DATE"] = ftds_data["SETTLEMENT DATE"].apply(
            lambda x: datetime.strptime(str(x), "%Y%m%d").strftime("%Y-%m-%d")
        )

        plt.bar(
            ftds_data["SETTLEMENT DATE"],
            ftds_data["QUANTITY (FAILS)"],
        )
        plt.ylabel("Number of shares")
        plt.title(f"Fails-to-deliver Data for {ticker}")
        plt.gcf().autofmt_xdate()
        plt.xlabel("Days")

        if gtff.USE_ION:
            plt.ion()

        plt.show()

    except Exception as e:
        print(e, "\n")
