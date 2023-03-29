"""Trading Hours Controller."""
__docformat__ = "numpy"

import argparse
import logging
import os
from datetime import date
from typing import List, Optional

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_timezone_or_invalid
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console
from openbb_terminal.stocks.tradinghours import bursa_view
from openbb_terminal.stocks.tradinghours.bursa_model import get_open
from openbb_terminal.stocks.tradinghours.pandas_market_cal_view import (
    display_exchange_holidays,
    get_all_holiday_exchange_short_names,
)
from openbb_terminal.stocks.tradinghours.tradinghours_helper import (
    get_exchanges_short_names,
    get_fd_equities_list,
)

logger = logging.getLogger(__name__)

# pylint: disable=R0902


class TradingHoursController(BaseController):

    """Trading Hours Controller class."""

    CHOICES_COMMANDS = ["symbol", "open", "closed", "all", "exchange", "holidays"]
    PATH = "/stocks/th/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")
    CHOICES_GENERATION = True

    def __init__(self, ticker: str = "", queue: Optional[List[str]] = None):
        """Construct Data."""
        super().__init__(queue)

        self.equities = get_fd_equities_list()
        self.equity_tickers = sorted(list(self.equities.keys()))
        short_names_df = get_exchanges_short_names()
        short_names_index = short_names_df.index.values
        short_names = short_names_df["short_name"].values
        all_short_names = list(short_names) + list(short_names_index)
        self.all_exchange_short_names = sorted(list(all_short_names))
        self.all_holiday_exchange_short_names = sorted(
            list(get_all_holiday_exchange_short_names()["short_name"].values)
        )

        self.symbol = None
        self.symbol_name = None
        self.symbol_market_open = False
        self.exchange = None

        if ticker:
            if ticker in self.equities.index:
                self.symbol = ticker
                self.symbol_name = self.equities.loc[ticker]["name"]
                self.exchange = self.equities.loc[ticker]["exchange"]
                open_ex = get_open()
                if self.exchange in open_ex.index:
                    self.symbol_market_open = True
                else:
                    self.symbol_market_open = False
            else:
                console.print(f"The ticker {ticker} was not found in the database.")

        self.source = "YahooFinance"
        self.data = pd.DataFrame()
        self.timezone = get_user_timezone_or_invalid()

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        exchange_opened = (
            ("OPENED" if self.symbol_market_open else "CLOSED")
            if self.symbol is not None
            else ""
        )

        mt = MenuText("stocks/th/")
        mt.add_cmd("open")
        mt.add_cmd("closed")
        mt.add_cmd("all")
        mt.add_cmd("exchange")
        mt.add_cmd("holidays")
        mt.add_raw("\n")
        mt.add_cmd("symbol")
        mt.add_raw("\n")
        mt.add_param("_symbol_name", self.symbol_name or "")
        mt.add_param("_symbol", self.symbol_name or "")
        mt.add_param("_exchange", exchange_opened)

        console.print(text=mt.menu_text, menu="Stocks - Trading Hours")

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

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.symbol = ns_parser.symbol
            if ns_parser.symbol in self.equities.index:
                self.symbol_name = self.equities.loc[self.symbol]["name"]
                self.exchange = self.equities.loc[self.symbol]["exchange"]
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
            else:
                console.print("[red]Symbol not found on database.[/red]\n")

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
            choices=self.all_exchange_short_names,
            dest="exchange",
        )

        if (
            other_args
            and "-n" not in other_args[0]
            and "--name" not in other_args[0]
            and "-h" not in other_args
        ):
            other_args.insert(0, "-n")

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.exchange:
                bursa_view.display_exchange(ns_parser.exchange)
            else:
                logger.error("Select the exchange you want to know about.")
                console.print(
                    "[red]Select the exchange you want to know about.[/red]\n"
                )

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

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            bursa_view.display_open()

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

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            bursa_view.display_closed()

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

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            bursa_view.display_all()

    @log_start_end(log=logger)
    def call_holidays(self, other_args: List[str]):
        """Process 'holidays' command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="exchange",
            description="Select the exchange and year you want see holidays for",
        )
        parser.add_argument(
            "-n",
            "--name",
            help="Exchange short name",
            dest="exchange",
            required=True,
            type=str.upper,
            choices=self.all_holiday_exchange_short_names,
            metavar="LSE",
        )

        parser.add_argument(
            "-y",
            "--year",
            help="Year",
            nargs="?",
            type=int,
            const=date.today().year,
            dest="year",
            metavar="year",
        )

        if (
            other_args
            and "-n" not in other_args[0]
            and "--name" not in other_args[0]
            and "-h" not in other_args
        ):
            other_args.insert(0, "-n")
            other_args.insert(2, "-y")

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.exchange:
                if ns_parser.year:
                    display_exchange_holidays(ns_parser.exchange, ns_parser.year)
                else:
                    display_exchange_holidays(ns_parser.exchange, date.today().year)
        else:
            logger.error("Select the exchange and year you want holiday calendar for.")
            console.print(
                "[red]Select the exchange and year you want holiday calendar for.[/red]\n"
            )
