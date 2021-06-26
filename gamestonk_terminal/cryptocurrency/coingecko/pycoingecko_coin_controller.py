"""Cryptocurrency Controller"""
__docformat__ = "numpy"
# pylint: disable=R0904, C0302
import argparse
import pandas as pd
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.coingecko import pycoingecko_view


class GeckoCoinController:

    CHOICES = [
        "help",
        "q",
        "quit",
        "load",
        "chart",
        "info",
        "market",
        "ath",
        "atl",
        "score",
        "web",
        "social",
        "bc",
        "dev",
    ]

    def __init__(self):
        """CONSTRUCTOR"""

        self._gecko_parser = argparse.ArgumentParser(add_help=False, prog="gecko")
        self._gecko_parser.add_argument("cmd", choices=self.CHOICES)
        self.current_coin = None
        self.current_currency = None
        self.current_df = pd.DataFrame()
        self.source = ""

    def print_help(self):
        """Print help"""
        print("\nCryptocurrency:")
        print("   help            show this menu again")
        print("   q               quit this menu, and shows back to main menu")
        print("   quit            quit to abandon program")
        print("")
        print("Coingecko Coin Menu:")
        print("   load            load cryptocurrency data")
        print("   chart           load and view cryptocurrency data")
        print("   info          load and view cryptocurrency data")
        print("   market          load and view cryptocurrency data")
        print("   ath           load and view cryptocurrency data")
        print("   atl          load and view cryptocurrency data")
        print("   web           load and view cryptocurrency data")
        print("   social           load and view cryptocurrency data")
        print("   score            load and view cryptocurrency data")
        print("   dev           load and view cryptocurrency data")
        print("   bc           load and view cryptocurrency data")
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
        (known_args, other_args) = self._gecko_parser.parse_known_args(an_input.split())

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

    def call_load(self, other_args):
        self.current_coin = pycoingecko_view.load(other_args)
        self.source = "CG"

    def call_chart(self, other_args):
        if self.current_coin:
            pycoingecko_view.view(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_info(self, other_args):
        if self.current_coin:
            pycoingecko_view.base_info(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_market(self, other_args):
        if self.current_coin:
            pycoingecko_view.market_data(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_web(self, other_args):
        if self.current_coin:
            pycoingecko_view.web(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_social(self, other_args):
        if self.current_coin:
            pycoingecko_view.social(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_dev(self, other_args):
        if self.current_coin:
            pycoingecko_view.dev(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_ath(self, other_args):
        if self.current_coin:
            pycoingecko_view.ath(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_atl(self, other_args):
        if self.current_coin:
            pycoingecko_view.atl(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_score(self, other_args):
        if self.current_coin:
            pycoingecko_view.score(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_bc(self, other_args):
        if self.current_coin:
            pycoingecko_view.blockchain_explorers(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")


def menu():
    gecko_controller = GeckoCoinController()
    gecko_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in gecko_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (crypto)>(gecko)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(gecko)> ")

        try:
            process_input = gecko_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue


menu()
