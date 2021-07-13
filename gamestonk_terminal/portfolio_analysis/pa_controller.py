__docformat__ = "numpy"

import argparse
import os
import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session

from gamestonk_terminal.portfolio_analysis import portfolio_parser


class PortfolioController:
    """Portfolio Controller"""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "load",
        "group",
    ]

    def __init__(self):
        self.pa_parser = argparse.ArgumentParser(add_help=False, prog="pa")
        self.pa_parser.add_argument("cmd", choices=self.CHOICES)
        self.portfolio_name = ""
        self.portfolio = pd.DataFrame()

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/portfolio_analysis"
        )
        print("\nPortfolio Analysis:")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("   load          load portfolio from csv file")
        print("")
        if self.portfolio_name:
            print(f"Portfolio: {self.portfolio_name}")
            print("")
            print("   group         view holdings by a user input group")
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

        (known_args, other_args) = self.pa_parser.parse_known_args(an_input.split())

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

    def call_load(self, other_args):
        """Process csv command"""
        self.portfolio_name, self.portfolio = portfolio_parser.load_csv_portfolio(
            other_args
        )

        if self.portfolio_name:
            print(f"Successfully loaded: {self.portfolio_name}\n")

    def call_group(self, other_args):
        """Process group command"""
        if self.portfolio_name:
            portfolio_parser.breakdown_by_group(self.portfolio, other_args)
        else:
            print("Please load a portfolio")


def menu():
    """Portfolio Analysis Menu"""
    pa_controller = PortfolioController()
    pa_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in pa_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (pa)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (pa)> ")

        try:
            process_input = pa_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
