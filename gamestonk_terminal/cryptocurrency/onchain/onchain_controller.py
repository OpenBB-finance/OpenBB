"""Onchain Controller Module"""
__docformat__ = "numpy"

import os
import argparse
from typing import List
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import get_flair, parse_known_args_and_warn

from gamestonk_terminal.cryptocurrency.onchain import gasnow_view

# pylint: disable=R1732


class OnchainController:
    """Onchain Controller class"""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
    ]

    CHOICES_COMMANDS = [
        "gwei",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(self):
        """Constructor"""
        self.onchain_parser = argparse.ArgumentParser(add_help=False, prog="onchain")
        self.onchain_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def switch(self, an_input: str):
        """Process and dispatch input

        Parameters
        -------
        an_input : str
            string with input arguments

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

        (known_args, other_args) = self.onchain_parser.parse_known_args(
            an_input.split()
        )

        # Help menu again
        if known_args.cmd == "?":
            print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, *_):
        """Process Help command"""
        print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_gwei(self, other_args: List[str]):
        """Process gwei command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="onchain",
            description="""
                Display ETH gas fees
                [Source: https://www.gasnow.org]
            """,
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

            gasnow_view.display_gwei_fees(export=ns_parser.export)

        except Exception as e:
            print(e, "\n")


def print_help():
    """Print help"""
    print(
        "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/cryptocurrency/onchain"
    )
    print("\nOnchain:")
    print("   cls           clear screen")
    print("   ?/help        show this menu again")
    print("   q             quit this menu, and shows back to main menu")
    print("   quit          quit to abandon program")
    print("")
    print("   gwei          check current eth gas fees")
    print("")


def menu():
    """Onchain Menu"""
    onchain_controller = OnchainController()
    onchain_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in onchain_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (crypto)>(onchain)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(onchain)> ")

        try:
            process_input = onchain_controller.switch(an_input)
        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if process_input is False:
            return False

        if process_input is True:
            return True
