"""Extra Controller Module"""
__docformat__ = "numpy"

import os
import argparse
import requests
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import get_flair

# pylint: disable=R1732


class ExtraController:
    """Extra Controller class"""

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
        self.extra_parser = argparse.ArgumentParser(add_help=False, prog="extra")
        self.extra_parser.add_argument(
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

        (known_args, other_args) = self.extra_parser.parse_known_args(an_input.split())

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

    def call_gwei(self, _):
        """Process gwei command"""
        r = requests.get("https://www.gasnow.org/api/v3/gas/price").json()["data"]
        fast = int(r["fast"] / 1_000_000_000)
        fastest = int(r["rapid"] / 1_000_000_000)
        average = int(r["standard"] / 1_000_000_000)
        low = int(r["slow"] / 1_000_000_000)
        print(
            f"""
        Current ETH gas prices (gwei):
            Fastest  (~15 sec):     {fastest} gwei
            Fast     (~1 min):      {fast} gwei
            Standard (~3 min):      {average} gwei
            Slow     (>10 min):     {low} gwei
        """
        )


def print_help():
    """Print help"""
    print(
        "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/cryptocurrency/extra"
    )
    print("\nExtra:")
    print("   cls           clear screen")
    print("   ?/help        show this menu again")
    print("   q             quit this menu, and shows back to main menu")
    print("   quit          quit to abandon program")
    print("")
    print("   gwei          check current eth gas fees")
    print("")


def menu():
    """Extra Menu"""
    extra_controller = ExtraController()
    extra_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in extra_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (crypto)>(extra)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(extra)> ")

        try:
            process_input = extra_controller.switch(an_input)
        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if process_input is False:
            return False

        if process_input is True:
            return True
