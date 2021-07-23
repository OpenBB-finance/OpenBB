import argparse
import logging
from typing import Any

from sentipy.sentipy import Sentipy
from tabulate import tabulate

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn

sentipy: Sentipy = Sentipy(
    token=cfg.API_SENTIMENTINVESTOR_TOKEN, key=cfg.API_SENTIMENTINVESTOR_KEY
)
"""Initialise SentiPy with the user's API token and key"""


def sort(metric: str, other_args: list[str]) -> None:
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="metrics",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Print realtime sentiment and hype index for this stock, aggregated from social media.",
    )

    parser.add_argument(
        "-l",
        "--limit",
        action="store",
        dest="limit",
        type=int,
        default=10,
        help="the maximum number of stocks to retrieve",
    )

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    data = sentipy.sort(metric, ns_parser.limit)

    table: list[list[Any]] = []
    for index, stock in enumerate(data):
        if not hasattr(stock, "symbol") or not hasattr(stock, metric):
            logging.warning("data for stock %s is incomplete, ignoring", index + 1)
            table.append([])
        else:
            table.append([index + 1, stock.symbol, stock.__getattribute__(metric)])

    print(tabulate(table, headers=["Rank", "Ticker", metric], floatfmt=".3f"))
