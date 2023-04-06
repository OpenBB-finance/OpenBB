"""Backtesting Controller Module"""
__docformat__ = "numpy"

import argparse
import logging
from typing import List, Optional

import matplotlib as mpl
import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_non_negative_float,
    check_positive,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import StockBaseController
from openbb_terminal.rich_config import MenuText, console

# This code below aims to fix an issue with the fnn module, used by bt module
# which forces matplotlib backend to be 'agg' which doesn't allow to plot
# Save current matplotlib backend
default_backend = mpl.get_backend()
# Restore backend matplotlib used

# pylint: disable=wrong-import-position
from openbb_terminal.stocks.backtesting import bt_view  # noqa: E402

logger = logging.getLogger(__name__)

mpl.use(default_backend)


def no_data_message():
    """Print message when no ticker is loaded"""
    console.print("[red]No data loaded. Use 'load' command to load a symbol[/red]")


class BacktestingController(StockBaseController):
    """Backtesting Controller class"""

    CHOICES_COMMANDS = ["load", "ema", "emacross", "rsi", "whatif"]
    PATH = "/stocks/bt/"
    CHOICES_GENERATION = True

    def __init__(
        self, ticker: str, stock: pd.DataFrame, queue: Optional[List[str]] = None
    ):
        """Constructor"""
        super().__init__(queue)

        self.ticker = ticker
        self.stock = stock
        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("stocks/bt/")
        mt.add_raw("")
        mt.add_param("_ticker", self.ticker.upper() or "No Ticker Loaded")
        mt.add_raw("\n")
        mt.add_cmd("load")
        mt.add_raw("\n")
        mt.add_cmd("whatif", self.ticker)
        mt.add_raw("\n")
        mt.add_cmd("ema", self.ticker)
        mt.add_cmd("emacross", self.ticker)
        mt.add_cmd("rsi", self.ticker)
        console.print(text=mt.menu_text, menu="Stocks - Backtesting")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            return ["stocks", f"load {self.ticker}", "bt"]
        return []

    @log_start_end(log=logger)
    def call_whatif(self, other_args: List[str]):
        """Call whatif"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="whatif",
            description="Displays what if scenario of having bought X shares at date Y",
        )
        parser.add_argument(
            "-d",
            "--date",
            default=None,
            dest="date_shares_acquired",
            type=valid_date,
            help="Date at which the shares were acquired",
        )
        parser.add_argument(
            "-n",
            "--number",
            default=1.0,
            type=check_non_negative_float,
            help="Number of shares acquired",
            dest="num_shares_acquired",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-d")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.stock.empty:
                no_data_message()
                return
            bt_view.display_whatif_scenario(
                symbol=self.ticker,
                num_shares_acquired=ns_parser.num_shares_acquired,
                date_shares_acquired=ns_parser.date_shares_acquired,
            )

    @log_start_end(log=logger)
    def call_ema(self, other_args: List[str]):
        """Call EMA strategy"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ema",
            description="Strategy where stock is bought when Price > EMA(l)",
        )
        parser.add_argument(
            "-l",
            default=20,
            dest="length",
            type=check_positive,
            help="EMA period to consider",
        )
        parser.add_argument(
            "--spy",
            action="store_true",
            default=False,
            help="Flag to add spy hold comparison",
            dest="spy",
        )
        parser.add_argument(
            "--no_bench",
            action="store_true",
            default=False,
            help="Flag to not show buy and hold comparison",
            dest="no_bench",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.stock.empty:
                no_data_message()
                return
            bt_view.display_simple_ema(
                symbol=self.ticker,
                data=self.stock,
                ema_length=ns_parser.length,
                spy_bt=ns_parser.spy,
                no_bench=ns_parser.no_bench,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_emacross(self, other_args: List[str]):
        """Call EMA Cross strategy"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="emacross",
            description="Cross between a long and a short Exponential Moving Average.",
        )
        parser.add_argument(
            "-l",
            "--long",
            default=50,
            dest="long",
            type=check_positive,
            help="Long EMA period",
        )
        parser.add_argument(
            "-s",
            "--short",
            default=20,
            dest="short",
            type=check_positive,
            help="Short EMA period",
        )
        parser.add_argument(
            "--spy",
            action="store_true",
            default=False,
            help="Flag to add spy hold comparison",
            dest="spy",
        )
        parser.add_argument(
            "--no_bench",
            action="store_true",
            default=False,
            help="Flag to not show buy and hold comparison",
            dest="no_bench",
        )
        parser.add_argument(
            "--no_short",
            action="store_false",
            default=True,
            dest="shortable",
            help="Flag that disables the short sell",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.stock.empty:
                no_data_message()
                return
            if ns_parser.long < ns_parser.short:
                console.print("Short EMA period is longer than Long EMA period\n")

            bt_view.display_emacross(
                symbol=self.ticker,
                data=self.stock,
                short_ema=ns_parser.short,
                long_ema=ns_parser.long,
                spy_bt=ns_parser.spy,
                no_bench=ns_parser.no_bench,
                shortable=ns_parser.shortable,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_rsi(self, other_args: List[str]):
        """Call RSI Strategy"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rsi",
            description="""Strategy that buys when the stock is less than a threshold
            and shorts when it exceeds a threshold.""",
        )
        parser.add_argument(
            "-p",
            "--periods",
            dest="periods",
            help="Number of periods for RSI calculation",
            type=check_positive,
            default=14,
        )
        parser.add_argument(
            "-u",
            "--high",
            default=70,
            dest="high",
            type=check_positive,
            help="High (upper) RSI Level",
        )
        parser.add_argument(
            "-l",
            "--low",
            default=30,
            dest="low",
            type=check_positive,
            help="Low RSI Level",
        )
        parser.add_argument(
            "--spy",
            action="store_true",
            default=False,
            help="Flag to add spy hold comparison",
            dest="spy",
        )
        parser.add_argument(
            "--no_bench",
            action="store_true",
            default=False,
            help="Flag to not show buy and hold comparison",
            dest="no_bench",
        )
        parser.add_argument(
            "--no_short",
            action="store_false",
            default=True,
            dest="shortable",
            help="Flag that disables the short sell",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.stock.empty:
                no_data_message()
                return
            if ns_parser.high < ns_parser.low:
                console.print("Low RSI value is higher than Low RSI value\n")

            bt_view.display_rsi_strategy(
                symbol=self.ticker,
                data=self.stock,
                periods=ns_parser.periods,
                low_rsi=ns_parser.low,
                high_rsi=ns_parser.high,
                spy_bt=ns_parser.spy,
                no_bench=ns_parser.no_bench,
                shortable=ns_parser.shortable,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
