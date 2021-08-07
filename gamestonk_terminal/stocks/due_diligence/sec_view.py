""" SEC View """
__docformat__ = "numpy"

import argparse
import os
from typing import List
from datetime import datetime, timedelta
from tabulate import tabulate
import requests
import pandas as pd
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_user_agent,
    check_positive,
    parse_known_args_and_warn,
    valid_date,
    export_data,
)


def fails_to_deliver(other_args: List[str], ticker: str, stock: pd.DataFrame):
    """Display fails-to-deliver data for a given ticker

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-n", "10"]
    ticker : str
        Stock ticker
    stock : pd.DataFrame
        Stock data
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        prog="ftd",
        description="""Prints latest fails-to-deliver data. [Source: SEC]""",
    )
    parser.add_argument(
        "-s",
        "--start",
        action="store",
        dest="start",
        type=valid_date,
        default=(datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
        help="start of datetime to see FTD",
    )
    parser.add_argument(
        "-e",
        "--end",
        action="store",
        dest="end",
        type=valid_date,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="end of datetime to see FTD",
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=0,
        help="number of latest fails-to-deliver being printed",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        default=False,
        dest="raw",
        help="Print raw data.",
    )
    parser.add_argument(
        "--export",
        choices=["csv", "json", "xlsx"],
        default="",
        dest="export",
        help="Export dataframe data to csv,json,xlsx file",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        ftds_data = pd.DataFrame()

        # Filter by number of last FTD
        if ns_parser.n_num > 0:
            url_ftds = "https://www.sec.gov/data/foiadocsfailsdatahtm"
            text_soup_ftds = BeautifulSoup(
                requests.get(url_ftds, headers={"User-Agent": get_user_agent()}).text,
                "lxml",
            )

            table = text_soup_ftds.find("table", {"class": "list"})
            links = table.findAll("a")
            link_idx = 0

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
                lambda x: datetime.strptime(str(x), "%Y%m%d")
            )

        # Filter by start and end dates for FTD
        else:

            base_url = "https://www.sec.gov/files/data/fails-deliver-data/cnsfails"
            ftd_dates = list()

            for y in range(ns_parser.start.year, ns_parser.end.year + 1):
                if y < ns_parser.end.year:
                    for m in range(ns_parser.start.month, 13):
                        month = "%02d" % m
                        if m == ns_parser.start.month and y == ns_parser.start.year:
                            if ns_parser.start.day < 16:
                                ftd_dates.append(str(y) + month + "a")
                            ftd_dates.append(str(y) + month + "b")
                        else:
                            ftd_dates.append(str(y) + month + "a")
                            ftd_dates.append(str(y) + month + "b")

                else:
                    for m in range(1, ns_parser.end.month):
                        month = "%02d" % m
                        if m == ns_parser.end.month - 1:
                            ftd_dates.append(str(y) + month + "a")
                            if ns_parser.end.day > 15:
                                ftd_dates.append(str(y) + month + "b")
                        else:
                            ftd_dates.append(str(y) + month + "a")
                            ftd_dates.append(str(y) + month + "b")

            ftd_urls = [base_url + ftd_date + ".zip" for ftd_date in ftd_dates]

            for ftd_link in ftd_urls:
                all_ftds = pd.read_csv(
                    ftd_link,
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

            ftds_data["SETTLEMENT DATE"] = ftds_data["SETTLEMENT DATE"].apply(
                lambda x: datetime.strptime(str(x), "%Y%m%d")
            )

            ftds_data = ftds_data[ftds_data["SETTLEMENT DATE"] > ns_parser.start]
            ftds_data = ftds_data[ftds_data["SETTLEMENT DATE"] < ns_parser.end]

        plt.bar(
            ftds_data["SETTLEMENT DATE"],
            ftds_data["QUANTITY (FAILS)"] / 1000,
        )
        plt.ylabel("Shares [K]")
        plt.title(f"Fails-to-deliver Data for {ticker}")
        plt.grid(b=True, which="major", color="#666666", linestyle="-", alpha=0.2)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y/%m/%d"))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
        plt.gcf().autofmt_xdate()
        plt.xlabel("Days")

        _ = plt.gca().twinx()

        if ns_parser.n_num > 0:
            stock_ftd = stock[
                stock.index > (datetime.now() - timedelta(days=ns_parser.n_num + 31))
            ]
        else:
            stock_ftd = stock[stock.index > ns_parser.start]
            stock_ftd = stock_ftd[stock_ftd.index < ns_parser.end]
        plt.plot(stock_ftd.index, stock_ftd["Adj Close"], color="tab:orange")
        plt.ylabel("Share Price [$]")

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

        if ns_parser.raw:
            print(
                tabulate(
                    ftds_data,
                    headers=ftds_data.columns,
                    tablefmt="fancy_grid",
                    stralign="right",
                    showindex=False,
                )
            )
            print("")

        export_data(
            ns_parser.export,
            os.path.dirname(os.path.abspath(__file__)),
            "ftd",
            ftds_data.reset_index(),
        )

    except Exception as e:
        print(e, "\n")
