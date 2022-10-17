""" Futures Controller """
__docformat__ = "numpy"

# pylint:disable=too-many-lines

import argparse
import logging
import os
import itertools
from datetime import datetime, timedelta
from secrets import choice
from typing import List, Dict, Any

import pandas as pd

from openbb_terminal.custom_prompt_toolkit import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end

from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    print_rich_table,
    valid_date,
    parse_and_split_input,
    parse_simple_args,
)
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.menu import session
from openbb_terminal.futures import yfinance_model, yfinance_view

logger = logging.getLogger(__name__)


class FuturesController(BaseController):
    """Futures Controller class"""

    CHOICES_COMMANDS = [
        "search",
        "curve",
        "historical",
    ]

    curve_type = "futures"

    PATH = "/futures/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.all_tickers = yfinance_model.FUTURES_DATA["Ticker"].unique().tolist()
        self.all_exchanges = yfinance_model.FUTURES_DATA["Exchange"].unique().tolist()
        self.all_categories = yfinance_model.FUTURES_DATA["Category"].unique().tolist()

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

            self.choices["historical"] = {"-t": {c: None for c in self.all_tickers}}
            self.choices["curve"] = {"-t": {c: None for c in self.all_tickers}}

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

    def print_help(self):
        """Print help"""
        mt = MenuText("futures/")
        mt.add_cmd("search")
        mt.add_raw("\n")
        mt.add_cmd("historical")
        mt.add_cmd("curve")
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
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yfinance_view.display_search(
                ns_parser.category, ns_parser.exchange, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_historical(self, other_args: List[str]):
        """Process historical command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="historical",
            description="""Display futures historical. [Source: YahooFinance]""",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            type=str,
            default="",
            help="Future ticker to display timeseries separated by comma when multiple, e.g.: BLK,ES",
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start",
            type=valid_date,
            help="Initial date. Default: 3 years ago",
            default=(datetime.now() - timedelta(days=3 * 365)),
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
        )
        if ns_parser:
            yfinance_view.display_historical(
                ns_parser.ticker.split(","),
                ns_parser.start.strftime("%Y-%m-%d"),
                ns_parser.raw,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_curve(self, other_args: List[str]):
        """Process curve command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="curve",
            description="""Display futures curve. [Source: YahooFinance]""",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            type=str,
            choices=self.all_tickers,
            default="",
            help="Future curve to be selected",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            yfinance_view.display_curve(
                ns_parser.ticker,
                ns_parser.raw,
                ns_parser.export,
            )
