"""Options Controller Module."""
__docformat__ = "numpy"

import argparse
import os
from typing import List
import matplotlib.pyplot as plt

from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.options import (
    barchart_view,
    syncretism_view,
    calculator_model,
    op_helpers,
)
from gamestonk_terminal.options.yfinance import yfinance_controller
from gamestonk_terminal.options.tradier import tradier_controller

from gamestonk_terminal.menu import session

# pylint: disable=no-member


class OptionsController:
    """Options Controller class."""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "disp",
        "scr",
        "calc",
        "yf",
        "tr",
        "info",
        "load",
    ]

    def __init__(self, ticker: str):
        """Construct data."""
        if ticker:
            self.ticker = ticker
        else:
            self.ticker = ""

        self.op_parser = argparse.ArgumentParser(add_help=False, prog="op")
        self.op_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    @staticmethod
    def print_help(ticker):
        """Print help."""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/options"
        )
        print("\nOptions:")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("   disp          display all preset screeners filters")
        print("   scr           output screener options")
        print("")
        print("   calc          basic call/put PnL calculator")
        print("")
        print(">  yf            yahoo finance options menu")
        print(">  tr            tradier options menu")
        print("")
        print(f"Current Ticker: {ticker}")
        print("   load          load new ticker")
        print("   info          display option information (volatility, IV rank etc)")
        print("")

    def switch(self, an_input: str):
        """Process and dispatch input.

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

        (known_args, other_args) = self.op_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help(self.ticker)
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command."""
        self.print_help(self.ticker)

    def call_q(self, _):
        """Process Q command - quit the menu."""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program."""
        return True

    def call_calc(self, other_args: List[str]):
        calculator_model.pnl_calculator(other_args)

    def call_info(self, other_args: List[str]):
        barchart_view.print_options_data(self.ticker, other_args)

    def call_disp(self, other_args: List[str]):
        syncretism_view.view_available_presets(other_args)

    def call_scr(self, other_args: List[str]):
        syncretism_view.screener_output(other_args)

    def call_load(self, other_args: List[str]):
        self.ticker = op_helpers.load(other_args)
        print(f"{self.ticker} loaded \n")

    # pylint: disable=inconsistent-return-statements
    def call_yf(self, _):
        """Process cp command"""
        if yfinance_controller.menu(self.ticker):
            return True

    def call_tr(self, _):
        """Process cp command"""
        if tradier_controller.menu(self.ticker):
            return True


def menu(ticker: str):
    """Options Menu."""

    try:
        op_controller = OptionsController(ticker)
        op_controller.call_help(None)
    except IndexError:
        print("No options found for " + ticker)
        print("")
        process_input = False
        return process_input

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in op_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (op)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (op)> ")

        try:
            plt.close("all")

            process_input = op_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
