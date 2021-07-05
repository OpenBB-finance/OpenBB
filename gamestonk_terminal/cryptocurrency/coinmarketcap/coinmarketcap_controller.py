"""Cryptocurrency Controller"""
__docformat__ = "numpy"
# pylint: disable=R0904, C0302, W0622
import argparse
import os
import pandas as pd
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.coinmarketcap import (
    coinmarketcap_view as cmc_view,
)


class CMCController:

    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
        "top",
    ]

    def __init__(self):
        """CONSTRUCTOR"""

        self._cmc_parser = argparse.ArgumentParser(add_help=False, prog="cmc")
        self._cmc_parser.add_argument("cmd", choices=self.CHOICES)
        self.current_coin = None
        self.current_currency = None
        self.current_df = pd.DataFrame()
        self.source = ""

    def print_help(self):
        """Print help"""
        print("\nCoinmarketcap:")
        print("   cls             clear screen")
        print("   ?/help          show this menu again")
        print("   q               quit this menu, and shows back to main menu")
        print("   quit            quit to abandon program")
        print("   top             view top coins from coinmarketcap")
        print("")

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

        (known_args, other_args) = self._cmc_parser.parse_known_args(an_input.split())

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
        """Process Q command - quit the menu."""
        print("Moving back to (crypto) menu")
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program."""
        return True

    def call_top(self, other_args):
        """Process top command"""
        cmc_view.get_cmc_top_n(other_args)


def menu():
    cmc_controller = CMCController()
    cmc_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in cmc_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (crypto)>(cmc)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(cmc)> ")

        try:
            process_input = cmc_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
