"""Yfinance options controller"""
__docformat__ = "numpy"

import argparse
from typing import List
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session

from gamestonk_terminal.options import op_helpers
from gamestonk_terminal.options.yfinance import yfinance_model

class YFinanceController:
    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
        "load"
    ]

    def __init__(self, ticker):
        self.ticker = ticker
        if ticker:
            self.expiry_dates = yfinance_model.option_expirations(ticker)
        else:
            self.expiry_dates = []
        self.yf_parser = argparse.ArgumentParser(add_help=False, prog="yf")
        self.yf_parser.add_argument(
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

        (known_args, other_args) = self.yf_parser.parse_known_args(an_input.split())

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

    def call_q(self, _):
        """Process Q command - quit the menu."""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program."""
        return True

    def call_help(self, _):
        """Process Help command."""
        self.print_help(self.ticker)

    def call_load(self, other_args:List[str]):
        """Process load command"""
        self.ticker = op_helpers.load(other_args)
        self.expiry_dates = yfinance_model.option_expirations(self.ticker)
        self.print_help()

    def print_help(self):
        print("help")
        print(f"Ticker: {self.ticker or None}")
        print(self.expiry_dates)

def menu(ticker):

    yf_controller = YFinanceController(ticker)
    yf_controller.print_help()
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in YFinanceController.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (op)>(yf)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (op)>(yf)> ")

        try:
            process_input = yf_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
