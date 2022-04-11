"""Trading Hours Controller."""
__docformat__ = "numpy"

import argparse
import logging
import os

# from datetime import datetime, timedelta
from typing import List

import pandas as pd
from prompt_toolkit.completion import NestedCompleter

# import financedatabase as fd

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.helper_funcs import (
    get_user_timezone_or_invalid,
    parse_known_args_and_warn,
)
from openbb_terminal.rich_config import console
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.tradinghours.tradinghours_helper import (
    get_fd_equities_list,
)


logger = logging.getLogger(__name__)


class TradingHoursController(BaseController):

    """Trading Hours Controller class."""

    CHOICES_COMMANDS = [
        "symbol",
        "is_traded",
        "open",
        "closed",
        "all",
    ]
    PATH = "/tradinghours/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")

    def __init__(self, queue: List[str] = None):
        """Construct Data."""
        super().__init__(queue)

        self.equities = get_fd_equities_list()
        self.equity_tickers = sorted(list(self.equities.keys()))

        self.symbol = "AAPL"
        self.symbol_name = self.equities[self.symbol]["long_name"]
        self.source = "yf"
        self.data = pd.DataFrame()
        self.timezone = get_user_timezone_or_invalid()

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["symbol"] = {c: None for c in self.equity_tickers}
            choices["symbol"]["-n"] = {c: None for c in self.equity_tickers}
            choices["symbol"]["--name"] = {c: None for c in self.equity_tickers}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        help_text = f"""[cmds]
    symbol      select the symbol

Name:     {None or self.symbol_name}
[param]Symbol:   [/param]{None or self.symbol}

[cmds]
is_traded     show when [param]symbol: [/param]{None or self.symbol} is traded
open          show open markets
closed        show closed markets
all           show all markets[/cmds]
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
            type=str,
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
            self.symbol_name = self.equities[self.symbol]["long_name"]
            console.print(
                f"\nSelected symbol\nSymbol:   {self.symbol}\n"
                f"Name:     {self.symbol_name}\n\n"
            )
