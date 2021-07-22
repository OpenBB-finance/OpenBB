"""Tradier options controller"""
__docformat__ = "numpy"

import argparse
from typing import List
import os
from prompt_toolkit.completion import NestedCompleter

import pandas as pd

from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.options.tradier import tradier_model, tradier_view
from gamestonk_terminal.options import op_helpers


class TradierController:
    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
        "load",
        "exp",
        "chains",
        "oi",
        "vol",
        "voi",
    ]

    def __init__(self, ticker):
        self.ticker = ticker
        if ticker:
            self.expiry_dates = tradier_model.option_expirations(ticker)
        else:
            self.expiry_dates = []
        self.selected_date = None
        self.options = pd.DataFrame()
        self.tr_parser = argparse.ArgumentParser(add_help=False, prog="tr")
        self.tr_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

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

        (known_args, other_args) = self.tr_parser.parse_known_args(an_input.split())

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

    def call_q(self, _):
        """Process Q command - quit the menu."""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program."""
        return True

    def call_help(self, _):
        """Process Help command."""
        self.print_help()

    def call_load(self, other_args: List[str]):
        """Process load command"""
        self.ticker = op_helpers.load(other_args)
        self.expiry_dates = tradier_model.option_expirations(self.ticker)
        print("")
        print(f"Current Ticker: {self.ticker or None}")
        print(f"Current Expiration: {self.selected_date or None}")
        print("")

    def call_exp(self, other_args: List[str]):
        """Process exp command"""
        if self.ticker:
            self.selected_date = op_helpers.select_option_date(
                self.expiry_dates, other_args
            )
        else:
            print("Please select a ticker using load {ticker}", "\n")
        if self.selected_date:
            self.options = tradier_model.get_option_chains(
                self.ticker, self.selected_date
            )
            print("")
            print(f"Current Ticker: {self.ticker or None}")
            print(f"Current Expiration: {self.selected_date or None}")
            print("")

    def call_chains(self, other_args: List[str]):
        """Process chains command"""
        tradier_view.display_chains(
            self.options, self.ticker, self.selected_date, other_args
        )

    # pylint: disable=unnecessary-pass

    def call_oi(self, other_args: List[str]):
        """Process oi command"""
        pass

    def call_vol(self, other_args: List[str]):
        """Process oi command"""
        pass

    def call_voi(self, other_args: List[str]):
        pass

    def print_help(self):
        """Print help."""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/options/yfinance"
        )
        print("\nOptions:")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("   load          load a new ticker")
        print("   exp           see and set expiration date")
        print("")
        print(f"Current Ticker: {self.ticker or None}")
        print(f"Current Expiration: {self.selected_date or None}")
        if not self.options.empty:
            print("")
            print("   chains        display option chains with greeks")
            print("   oi            plot open interest")
            print("   vol           plot volume")
            print("   voi           plot volume and open interest")
        print("")


def menu(ticker):

    tr_controller = TradierController(ticker)
    tr_controller.print_help()
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in TradierController.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (op)>(tr)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (op)>(tr)> ")

        try:
            process_input = tr_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
