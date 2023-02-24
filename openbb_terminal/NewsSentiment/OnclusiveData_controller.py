"""Onclusive Data Controller Module"""
__docformat__ = "numpy"

import argparse
import logging
import os
from typing import List
import pandas as pd
from openbb_terminal.NewsSentiment import Onclusivedata_view
from openbb_terminal import feature_flags as obbff
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_non_negative,
    check_positive,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class OnclusiveDataController(BaseController):
    CHOICES_COMMANDS = [
        "show",
        "-t",
        "--ticker",
        "-l",
        "--limit",
        "-sd",
        "--start_date",
        "-ed",
        "--end_date",
        "-d",
        "--date",
    ]
    PATH = "/newssentiment/"

    CHOICES_GENERATION = True

    def __init__(self, queue: List[str] = None) -> None:
        """Construct News Sentiment controller."""
        super().__init__(queue)

    def print_help(self):
        """Print help"""
        mt = MenuText("newssentiment/")
        mt.add_cmd("show", "InvisagePlotform")
        mt.add_raw("\n")
        console.print(text=mt.menu_text, menu="newssentiment")

    @log_start_end(log=logger)
    def call_show(self, other_args: List[str]):
        """Process show command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="show",
            description="Shows the News Sentiment articles data",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-sd",
            "--start_date",
            dest="start_date",
            type=str,
            default=False,
            help="The starting date (format YYYY-MM-DD) to search articles from",
        )
        parser.add_argument(
            "-ed",
            "--end_date",
            dest="end_date",
            type=str,
            default=False,
            help="The end date (format YYYY-MM-DD) to search articles upto",
        )
        parser.add_argument(
            "-d",
            "--date",
            dest="date",
            type=str,
            default=False,
            help="Show that the article data on this day (format YYYY-MM-DD).",
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=100,
            dest="limit",
            type=check_non_negative,
            help="Number of arctiles to be display",
        )
        parser.add_argument(
            "-o",
            "--offset",
            default=0,
            dest="offset",
            type=check_non_negative,
            help="offset indicates the starting position of article records",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            Onclusivedata_view.display_articles_data(
                ticker=ns_parser.ticker,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                date=ns_parser.date,
                limit=ns_parser.limit,
                offset=ns_parser.offset,
                export=ns_parser.export,
            )

        return
