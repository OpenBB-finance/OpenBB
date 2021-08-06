"""Behavioural Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
import os
from typing import List
from datetime import datetime
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.common.behavioural_analysis import (
    google_view,
)


class BehaviouralAnalysisController:
    """Behavioural Analysis Controller class"""

    # Command choices
    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
    ]

    CHOICES_COMMANDS = [
        "infer",
        "sentiment",
        "mentions",
        "regions",
        "queries",
        "rise",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(self, ticker: str, start: datetime):
        """Constructor"""
        self.ticker = ticker
        self.start = start
        self.ba_parser = argparse.ArgumentParser(add_help=False, prog="ba")
        self.ba_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    @staticmethod
    def print_help():
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/behavioural_analysis"
        )
        print("\nBehavioural Analysis:")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("Twitter:")
        print("   infer         infer about stock's sentiment from latest tweets")
        print("   sentiment     in-depth sentiment prediction from tweets over time")
        print("")
        print("Google:")
        print("   mentions      interest over time based on stock's mentions")
        print("   regions       regions that show highest interest in stock")
        print("   queries       top related queries with this stock")
        print("   rise          top rising related queries with stock")
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

        (known_args, other_args) = self.ba_parser.parse_known_args(an_input.split())

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

    def call_mentions(self, other_args: List[str]):
        """Process mentions command"""
        google_view.mentions(other_args, self.ticker, self.start)

    def call_regions(self, other_args: List[str]):
        """Process regions command"""
        google_view.regions(other_args, self.ticker)

    def call_queries(self, other_args: List[str]):
        """Process queries command"""
        google_view.queries(other_args, self.ticker)

    def call_rise(self, other_args: List[str]):
        """Process rise command"""
        google_view.rise(other_args, self.ticker)

    def call_infer(self, other_args: List[str]):
        """Process infer command"""
        if not gtff.ENABLE_PREDICT:
            print("Predict is not enabled in feature_flags.py")
            print("Twitter inference menu is disabled", "\n")
            return

        try:
            # pylint: disable=import-outside-toplevel
            from gamestonk_terminal.common.behavioural_analysis import twitter_view
        except ModuleNotFoundError as e:
            print("Optional packages need to be installed")
            print(e, "\n")
            return
        except Exception as e:
            print(e, "\n")
            return

        twitter_view.inference(other_args, self.ticker)

    def call_sentiment(self, other_args: List[str]):
        """Process sentiment command"""
        if not gtff.ENABLE_PREDICT:
            print("Predict is not enabled in feature_flags.py")
            print("Twitter inference menu is disabled", "\n")
            return

        try:
            # pylint: disable=import-outside-toplevel
            from gamestonk_terminal.common.behavioural_analysis import twitter_view
        except ModuleNotFoundError as e:
            print("Optional packages need to be installed")
            print(e, "\n")
            return
        except Exception as e:
            print(e, "\n")
            return

        twitter_view.sentiment(other_args, self.ticker)


def menu(ticker: str, start: datetime):
    """Behavioural Analysis Menu"""

    ba_controller = BehaviouralAnalysisController(ticker, start)
    ba_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in ba_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (forex)>(ba)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (forex)>(ba)> ")

        try:
            process_input = ba_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
