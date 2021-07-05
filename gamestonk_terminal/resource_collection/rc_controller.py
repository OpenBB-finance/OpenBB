"""Resource Collection Controller Module"""
__docformat__ = "numpy"

import argparse
import os
import webbrowser
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session


class ResourceCollectionController:
    """Resources Controller class"""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "hfletters",
        "arxiv",
        "finra",
        "edgar",
        "fred",
        "learn",
    ]

    def __init__(self):
        """Constructor"""
        self.rc_parser = argparse.ArgumentParser(add_help=False, prog="rc")
        self.rc_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    @staticmethod
    def print_help():
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/resource_collection"
        )
        print("\nResources:")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("   hfletters     hedge fund letters or reports")
        print("   arxiv         open-access archive for academic articles")
        print("   finra         self-regulatory organization")
        print("   edgar         online public database from SEC")
        print("   fred          economic research data")
        print("   learn         trading analysis, tips and resources")
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

        (known_args, other_args) = self.rc_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        if other_args:
            print(f"The following args were unexpected: {other_args}")

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

    def call_hfletters(self, _):
        """Process hfletters command"""
        webbrowser.open("https://miltonfmr.com/hedge-fund-letters/")
        print("")

    def call_arxiv(self, _):
        """Process arxiv command"""
        webbrowser.open("https://arxiv.org")
        print("")

    def call_finra(self, _):
        """Process finra command"""
        webbrowser.open("https://www.finra.org/#/")
        print("")

    def call_edgar(self, _):
        """Process edgar command"""
        webbrowser.open("https://www.sec.gov/edgar.shtml")
        print("")

    def call_fred(self, _):
        """Process fred command"""
        webbrowser.open("https://fred.stlouisfed.org")
        print("")

    def call_learn(self, _):
        """Process learn command"""
        webbrowser.open("https://moongangcapital.com/free-stock-market-resources/")
        print("")


def menu():
    """Resource Collection Menu"""

    rc_controller = ResourceCollectionController()
    rc_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in rc_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (rc)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (rc)> ")

        try:
            process_input = rc_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
