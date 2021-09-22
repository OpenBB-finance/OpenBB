"""Backtesting Controller Module"""
__docformat__ = "numpy"

import argparse
import os
from typing import List

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    check_positive,
    get_flair,
    parse_known_args_and_warn,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.stocks.stocks_helper import load

# This code below aims to fix an issue with the fnn module, used by bt module
# which forces matplotlib backend to be 'agg' which doesn't allow to plot
# Save current matplotlib backend
default_backend = mpl.get_backend()
# pylint: disable=wrong-import-position
from gamestonk_terminal.stocks.backtesting import bt_view  # noqa: E402

# Restore backend matplotlib used
mpl.use(default_backend)


class BacktestingController:
    """Backtesting Class"""

    CHOICES = ["?", "cls", "help", "q", "quit", "load"]
    CHOICES_COMMANDS = ["ema", "ema_cross", "rsi"]
    CHOICES += CHOICES_COMMANDS

    def __init__(self, ticker: str, stock: pd.DataFrame):
        self.ticker = ticker
        self.stock = stock
        self.bt_parser = argparse.ArgumentParser(add_help=False, prog="bt")
        self.bt_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        help_text = f"""
Backtesting:
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon program
    load        load new ticker to analyze

Current Ticker: {self.ticker.upper()}

    ema         buy when price exceeds EMA(l)
    ema_cross   buy when EMA(short) > EMA(long)
    rsi         buy when RSI < low and sell when RSI > high
        """
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.bt_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_load(self, other_args: List[str]):
        """Process load command"""
        self.ticker, _, _, self.stock = load(
            other_args, self.ticker, "", "1440", pd.DataFrame()
        )
        if "." in self.ticker:
            self.ticker = self.ticker.split(".")[0]

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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            bt_view.display_simple_ema(
                ticker=self.ticker,
                df_stock=self.stock,
                ema_length=ns_parser.length,
                spy_bt=ns_parser.spy,
                no_bench=ns_parser.no_bench,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_ema_cross(self, other_args: List[str]):
        """Call EMA Cross strategy"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ema_cross",
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            if ns_parser.long < ns_parser.short:
                print("Short EMA period is longer than Long EMA period\n")
                return

            bt_view.display_ema_cross(
                ticker=self.ticker,
                df_stock=self.stock,
                short_ema=ns_parser.short,
                long_ema=ns_parser.long,
                spy_bt=ns_parser.spy,
                no_bench=ns_parser.no_bench,
                shortable=ns_parser.shortable,
                export=ns_parser.export,
            )
        except Exception as e:
            print(e, "\n")

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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            if ns_parser.high < ns_parser.low:
                print("Low RSI value is higher than Low RSI value\n")
                return

            bt_view.display_rsi_strategy(
                ticker=self.ticker,
                df_stock=self.stock,
                periods=ns_parser.periods,
                low_rsi=ns_parser.low,
                high_rsi=ns_parser.high,
                spy_bt=ns_parser.spy,
                no_bench=ns_parser.no_bench,
                shortable=ns_parser.shortable,
                export=ns_parser.export,
            )
        except Exception as e:
            print(e, "\n")


def menu(ticker: str, stock: pd.DataFrame):
    """Backtesting Menu"""
    plt.close("all")
    bt_controller = BacktestingController(ticker, stock)
    bt_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in bt_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (stocks)>(bt)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)>(bt)> ")

        try:
            plt.close("all")

            process_input = bt_controller.switch(an_input)
            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
