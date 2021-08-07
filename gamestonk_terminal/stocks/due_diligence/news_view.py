""" News View """
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime, timedelta
import requests
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
)


def news(other_args: List[str], ticker: str):
    """Display news for a given ticker

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-n", "10"]
    ticker : str
        Stock ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="news",
        description="""
            Prints latest news about company, including date, title and web link. [Source: News API]
        """,
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="Number of latest news being printed.",
    )
    # TODO: Add argument to specify news source being used
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        s_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        response = requests.get(
            f"https://newsapi.org/v2/everything?q={ticker}&from={s_from}"
            f"&sortBy=publishedAt&language=en&apiKey={cfg.API_NEWS_TOKEN}",
        )

        # Check that the API response was successful
        if response.status_code != 200:
            print("Invalid News API token\n")

        else:
            print(
                f"{response.json()['totalResults']} news articles from {ticker} were found since {s_from}\n"
            )

            for idx, article in enumerate(response.json()["articles"]):
                print(
                    article["publishedAt"].replace("T", " ").replace("Z", ""),
                    " ",
                    article["title"],
                )
                # Unnecessary to use name of the source because contained in link article["source"]["name"]
                print(article["url"])
                print("")

                if idx >= ns_parser.n_num - 1:
                    break

    except Exception as e:
        print(e, "\n")
