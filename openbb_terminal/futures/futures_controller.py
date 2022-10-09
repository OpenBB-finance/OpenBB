""" Futures Controller """
__docformat__ = "numpy"

# pylint:disable=too-many-lines

import argparse
import logging
import os
import itertools
from datetime import date
from typing import List, Dict, Any

import pandas as pd

from openbb_terminal.custom_prompt_toolkit import NestedCompleter

from openbb_terminal.decorators import check_api_key
from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end

from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    print_rich_table,
    valid_date,
    parse_and_split_input,
    parse_simple_args,
)
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.menu import session

logger = logging.getLogger(__name__)


class FuturesController(BaseController):
    """Futures Controller class"""

    CHOICES_COMMANDS = [
        "search",
        "futures",
        "historical",
    ]

    curve_type = "futures"

    PATH = "/futures/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.futures_data = pd.read_csv(
            os.path.join("openbb_terminal", "futures", "futures.csv")
        )

        self.all_tickers = self.futures_data["Ticker"].tolist()
        self.all_exchanges = self.futures_data["Exchange"].unique().tolist()
        self.all_categories = self.futures_data["Category"].unique().tolist()

        if session and obbff.USE_PROMPT_TOOLKIT:
            self.choices: dict = {c: {} for c in self.controller_choices}

            self.choices["search"] = {
                "--category": {c: None for c in self.all_categories},
                "-c": "--category",
                "--exchange": {c: None for c in self.all_exchanges},
                "-e": "--exchange",
            }

            self.choices["support"] = self.SUPPORT_CHOICES
            self.choices["about"] = self.ABOUT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(self.choices)  # type: ignore

    def parse_input(self, an_input: str) -> List:
        """Parse controller input

        Overrides the parent class function to handle github org/repo path convention.
        See `BaseController.parse_input()` for details.
        """
        # Filtering out sorting parameters with forward slashes like P/E
        sort_filter = r"((\ -s |\ --sortby ).*?(P\/E|Fwd P\/E|P\/S|P\/B|P\/C|P\/FCF)*)"

        custom_filters = [sort_filter]

        commands = parse_and_split_input(
            an_input=an_input, custom_filters=custom_filters
        )
        return commands

    def update_runtime_choices(self):
        if session and obbff.USE_PROMPT_TOOLKIT:
            pass
        self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("futures/")
        mt.add_cmd("search")
        mt.add_raw("\n")
        mt.add_cmd("historical")
        mt.add_cmd("futures")
        console.print(text=mt.menu_text, menu="Futures")

    @log_start_end(log=logger)
    def call_curve(self, other_args: List[str]):
        """Process curve command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="curve",
            description="""Set type of curve to use. [Source: YahooFinance]""",
        )
        parser.add_argument(
            "-t",
            "--type",
            dest="type",
            help="Select between 'futures' and 'timeseries'",
            type=str,
            choices=["futures", "timeseries"],
            default="futures",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_simple_args(
            parser,
            other_args,
        )
        if ns_parser:
            self.curve_type = ns_parser.type
            console.print()

    @log_start_end(log=logger)
    def call_search(self, other_args: List[str]):
        """Process search command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="search",
            description="""Search futures. [Source: YahooFinance]""",
        )
        parser.add_argument(
            "-e",
            "--exchange",
            dest="exchange",
            type=str,
            choices=self.all_exchanges,
            default="",
            help="Select the exchange where the future exists",
        )
        parser.add_argument(
            "-c",
            "--category",
            dest="category",
            type=str,
            choices=self.all_categories,
            default="",
            help="Select the category where the future exists",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if ns_parser.category:
                print_rich_table(
                    self.futures_data[
                        self.futures_data["Category"] == ns_parser.category
                    ]
                )
            elif ns_parser.exchange:
                print_rich_table(
                    self.futures_data[
                        self.futures_data["Exchange"] == ns_parser.exchange
                    ]
                )
            elif ns_parser.category and ns_parser.exchange:
                print_rich_table(
                    self.futures_data[
                        (self.futures_data["Exchange"] == ns_parser.exchange)
                        and (self.futures_data["Category"] == ns_parser.category)
                    ]
                )
            else:
                print_rich_table(self.futures_data)
        console.print()

    @log_start_end(log=logger)
    def call_timeseries(self, other_args: List[str]):
        """Process timeseries command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="timeseries",
            description="""Display futures timeseres. [Source: YahooFinance]""",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            type=str,
            choices=self.all_tickers,
            default="",
            help="Future ticker to display timeseries",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            console.print("WORK IN PROGRESS")
