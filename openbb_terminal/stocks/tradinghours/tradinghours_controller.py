"""Trading Hours Controller."""
__docformat__ = "numpy"

import argparse
import logging
import os

from typing import List

import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.helper_funcs import (
    get_user_timezone_or_invalid,
    parse_known_args_and_warn,
)
from openbb_terminal.rich_config import console
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.stocks.tradinghours import bursa_view
from openbb_terminal.stocks.tradinghours.bursa_model import get_open
from openbb_terminal.stocks.tradinghours.tradinghours_helper import (
    get_exchanges_short_names,
    get_fd_equities_list,
)


logger = logging.getLogger(__name__)


class TradingHoursController(BaseController):

    """Trading Hours Controller class."""

    CHOICES_COMMANDS = ["symbol", "open", "closed", "all", "exchange"]
    PATH = "/stocks/th/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")

    def __init__(self, queue: List[str] = None):
        """Construct Data."""
        super().__init__(queue)

        self.equities = get_fd_equities_list()
        self.equity_tickers = sorted(list(self.equities.keys()))
        short_names_df = get_exchanges_short_names()
        short_names_index = short_names_df.index.values
        short_names = short_names_df["short_name"].values
        all_short_names = list(short_names) + list(short_names_index)
        self.all_exchange_short_names = sorted(list(all_short_names))

        self.exchange = None
        self.symbol = None
        self.symbol_name = None
        self.symbol_market_open = False
        self.source = "yf"
        self.data = pd.DataFrame()
        self.timezone = get_user_timezone_or_invalid()

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["exchange"] = {c: None for c in self.all_exchange_short_names}
            choices["exchange"]["-n"] = {c: None for c in self.all_exchange_short_names}
            choices["exchange"]["--name"] = {
                c: None for c in self.all_exchange_short_names
            }
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        if self.symbol is not None:
            if self.symbol_market_open:
                exchange_opened = "OPENED"
            else:
                exchange_opened = "CLOSED"
        else:
            exchange_opened = ""

        help_text = f"""[cmds]
    symbol       select the symbol[/cmds]

[param]Symbol name:[/param] {self.symbol_name or ""}
[param]Symbol:[/param] {self.symbol or ""}
[param]Exchange open:[/param] {exchange_opened}
[cmds]
    open         show open markets
    closed       show closed markets
    all          show all markets
    exchange     show one exchange[/cmds]
"""
        console.print(text=help_text, menu="Trading Hours")

    @log_start_end(log=logger)
    def call_symbol(self, other_args: List[str]):
        """Process 'symbol' command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="symbol",
            description="Select the symbol you wish to trade",
        )
        parser.add_argument(
            "-n",
            "--name",
            help="Symbol",
            type=str.upper,
            dest="symbol",
        )

        if (
            other_args
            and "-n" not in other_args[0]
            and "--name" not in other_args[0]
            and "-h" not in other_args
        ):
            other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.symbol = ns_parser.symbol
            self.symbol_name = self.equities[self.symbol]["short_name"]  #
            self.exchange = self.equities[self.symbol]["exchange"]
            open_ex = get_open()
            if self.exchange in open_ex.index:
                self.symbol_market_open = True
            else:
                self.symbol_market_open = False
            # add currency
            console.print(
                f"\nSelected symbol\nSymbol:        {self.symbol}\n"
                f"Name:          {self.symbol_name}\n"
                f"Market open:   {self.symbol_market_open}\n"
            )

    @log_start_end(log=logger)
    def call_exchange(self, other_args: List[str]):
        """Process 'exchange' command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="exchange",
            description="Select the exchange you want see open hours for",
        )
        parser.add_argument(
            "-n",
            "--name",
            help="Exchange short name",
            type=str.upper,
            dest="exchange",
        )

        if (
            other_args
            and "-n" not in other_args[0]
            and "--name" not in other_args[0]
            and "-h" not in other_args
        ):
            other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser and ns_parser.exchange:
            bursa_view.display_exchange(ns_parser.exchange)
        else:
            logger.error("Select the exchange you want to know about.")
            console.print("[red]Select the exchange you want to know about.[/red]\n")

    @log_start_end(log=logger)
    def call_open(self, other_args: List[str]):
        """Process 'symbol' command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="exchange",
            description="Show currently open exchanges",
        )

        if other_args and "-h" not in other_args:
            other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            bursa_view.display_open()
        else:
            logger.error("No open exchanges right now.")
            console.print("[red]No open exchanges right now.[/red]\n")

    @log_start_end(log=logger)
    def call_closed(self, other_args: List[str]):
        """Process 'symbol' command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="exchange",
            description="Show currently closed exchanges",
        )

        if other_args and "-h" not in other_args:
            other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            bursa_view.display_closed()
        else:
            logger.error("No closed exchanges right now.")
            console.print("[red]No closed exchanges right now.[/red]\n")

    @log_start_end(log=logger)
    def call_all(self, other_args: List[str]):
        """Process 'symbol' command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="exchange",
            description="Show all exchanges",
        )

        if other_args and "-h" not in other_args:
            other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            bursa_view.display_all()
        else:
            logger.error("No exchanges right now.")
            console.print("[red]No exchanges right now.[/red]\n")
