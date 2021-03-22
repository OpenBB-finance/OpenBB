import requests
import json
import argparse
from datetime import datetime, timedelta
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
)


def news(l_args, s_ticker):
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

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)
        if not ns_parser:
            return

        s_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        response = requests.get(
            f"https://newsapi.org/v2/everything?q={s_ticker}&from={s_from}"
            f"&sortBy=publishedAt&language=en&apiKey={cfg.API_NEWS_TOKEN}",
        )

        # Check that the API response was successful
        if response.status_code != 200:
            print("Invalid News API token\n")

        else:
            print(
                f"{response.json()['totalResults']} news articles from {s_ticker} were found since {s_from}\n"
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