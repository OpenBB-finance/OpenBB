import argparse
import logging
import textwrap
from typing import Any, List

from colorama import Style
from sentipy.sentipy import Sentipy
from tabulate import tabulate

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn

sentipy: Sentipy = Sentipy(
    token=cfg.API_SENTIMENTINVESTOR_TOKEN, key=cfg.API_SENTIMENTINVESTOR_KEY
)
"""Initialise SentiPy with the user's API token and key"""


__command_descriptions = {
    "popular": f"""
        The {Style.BRIGHT}popular{Style.RESET_ALL} command prints the stocks with highest Average Hype Index right now.

        {Style.BRIGHT}AHI (Absolute Hype Index){Style.RESET_ALL}
        ---
        AHI is a measure of how much people are talking about a stock on social media.
        It is calculated by dividing the total number of mentions for the chosen stock
        on a social network by the mean number of mentions any stock receives on that
        social medium.

        ===

        {Style.BRIGHT}Sentiment Investor{Style.RESET_ALL} analyzes data from four major social media platforms to
        generate hourly metrics on over 2,000 stocks. Sentiment provides volume and
        sentiment metrics powered by proprietary NLP models.
        """,
    "emerging": f"""
        The {Style.BRIGHT}emerging{Style.RESET_ALL} command prints the stocks with highest Relative Hype Index right now.

        {Style.BRIGHT}RHI (Relative Hype Index){Style.RESET_ALL}
        ---
        RHI is a measure of whether people are talking about a stock more or less than
        usual, calculated by dividing the mean AHI for the past day by the mean AHI for
        for the past week for that stock.

        ===

        {Style.BRIGHT}Sentiment Investor{Style.RESET_ALL} analyzes data from four major social media platforms to
        generate hourly metrics on over 2,000 stocks. Sentiment provides volume and
        sentiment metrics powered by proprietary NLP models.
        """,
}


def sort(metric: str, other_args: List[str], command_name: str) -> None:
    parser = argparse.ArgumentParser(
        add_help=False,
        prog=command_name,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(__command_descriptions[command_name]),
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        data = sentipy.sort(metric, ns_parser.limit)

        table: List[List[Any]] = []
        for index, stock in enumerate(data):
            if not hasattr(stock, "symbol") or not hasattr(stock, metric):
                logging.warning("data for stock %s is incomplete, ignoring", index + 1)
                table.append([])
            else:
                table.append([index + 1, stock.symbol, stock.__getattribute__(metric)])

        print(tabulate(table, headers=["Rank", "Ticker", metric], floatfmt=".3f"))
        print()
    except Exception as e:
        logging.error(e)
        print(e, "\n")
