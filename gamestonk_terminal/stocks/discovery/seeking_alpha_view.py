""" Seeking Alpha View """
__docformat__ = "numpy"

import argparse
import os
from typing import List
from datetime import datetime
from tabulate import tabulate
import pandas as pd
from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
    valid_date,
    export_data,
)

from gamestonk_terminal.stocks.discovery import seeking_alpha_model


def upcoming_earning_release_dates(num_pages: int, num_earnings: int, export: str):
    """Displays upcoming earnings release dates

    Parameters
    ----------
    num_pages: int
        Number of pages to scrap
    num_earnings: int
        Number of upcoming earnings release dates
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    # TODO: Check why there are repeated companies
    # TODO: Create a similar command that returns not only upcoming, but antecipated earnings
    # i.e. companies where expectation on their returns are high

    df_earnings = seeking_alpha_model.get_next_earnings(num_pages)

    pd.set_option("display.max_colwidth", None)
    if export:
        l_earnings = list()
        l_earnings_dates = list()

    for n_days, earning_date in enumerate(df_earnings.index.unique()):
        if n_days > (num_earnings - 1):
            break

        df_earn = df_earnings[earning_date == df_earnings.index][
            ["Ticker", "Name"]
        ].dropna()

        if export:
            l_earnings_dates.append(earning_date.date())
            l_earnings.append(df_earn)

        df_earn.index = df_earn["Ticker"].values
        df_earn.drop(columns=["Ticker"], inplace=True)

        print(
            tabulate(
                df_earn,
                showindex=True,
                headers=[f"Earnings on {earning_date.date()}"],
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    if export:
        for i, _ in enumerate(l_earnings):
            l_earnings[i].reset_index(drop=True, inplace=True)
        df_data = pd.concat(l_earnings, axis=1, ignore_index=True)
        df_data.columns = l_earnings_dates

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "upcoming",
            df_data,
        )


def latest_news_view(other_args: List[str]):
    """Prints the latest news article list

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-i", "123123", "-n", "5"]
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="latest",
        description="""Latest news articles. [Source: Seeking Alpha]""",
    )
    parser.add_argument(
        "-i",
        "--id",
        action="store",
        dest="n_id",
        type=check_positive,
        default=-1,
        help="article ID number",
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="number of articles being printed",
    )
    parser.add_argument(
        "-d",
        "--date",
        action="store",
        dest="n_date",
        type=valid_date,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="starting date",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-i")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # User wants to see all latest news
        if ns_parser.n_id == -1:
            articles = seeking_alpha_model.get_article_list(
                ns_parser.n_date, ns_parser.n_num
            )
            for idx, article in enumerate(articles):
                print(
                    article["publishedAt"].replace("T", " ").replace("Z", ""),
                    "-",
                    article["id"],
                    "-",
                    article["title"],
                )
                print(article["url"])
                print("")

                if idx >= ns_parser.n_num - 1:
                    break

        # User wants to access specific article
        else:
            article = seeking_alpha_model.get_article_data(ns_parser.n_id)
            print(
                article["publishedAt"][: article["publishedAt"].rfind(":") - 3].replace(
                    "T", " "
                ),
                " ",
                article["title"],
            )
            print(article["url"])
            print("")
            print(article["content"])

    except Exception as e:
        print(e, "\n")


def trending_news_view(other_args: List[str]):
    """Prints the trending news article list

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["i", "123123", "-n", "5"]
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="trending",
        description="""Trending news articles. [Source: Seeking Alpha]""",
    )
    parser.add_argument(
        "-i",
        "--id",
        action="store",
        dest="n_id",
        type=check_positive,
        default=-1,
        help="article ID number",
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="number of articles being printed",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-i")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # User wants to see all trending articles
        if ns_parser.n_id == -1:
            articles = seeking_alpha_model.get_trending_list(ns_parser.n_num)
            for idx, article in enumerate(articles):
                print(
                    article["publishedAt"].replace("T", " ").replace("Z", ""),
                    "-",
                    article["id"],
                    "-",
                    article["title"],
                )
                print(article["url"])
                print("")

                if idx >= ns_parser.n_num - 1:
                    break

        # User wants to access specific article
        else:
            article = seeking_alpha_model.get_article_data(ns_parser.n_id)
            print(
                article["publishedAt"][: article["publishedAt"].rfind(":") - 3].replace(
                    "T", " "
                ),
                " ",
                article["title"],
            )
            print(article["url"])
            print("")
            print(article["content"])

    except Exception as e:
        print(e, "\n")
