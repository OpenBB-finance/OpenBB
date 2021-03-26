__docformat__ = "numpy"

import argparse
import pandas as pd
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency import coin_api


class CryptoController:

    CHOICES = ["help", "q", "quit", "load", "view", "clear"]

    def __init__(self):

        self.crypto_parser = argparse.ArgumentParser(add_help=False, prog="crypto")
        self.crypto_parser.add_argument("cmd", choices=self.CHOICES)
        self.current_coin = None
        self.current_df = pd.DataFrame()

    @staticmethod
    def print_help(current_coin):
        """ Print help """
        print("\nCryptocurrency:")
        print("   help          show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print(f"\nCurrent Coin : {current_coin}")
        print("")
        print("   load          load cryptocurrency data")
        print("   view          load and view cryptocurrency data")
        print("   clear          load cryptocurrency data")
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
        (known_args, other_args) = self.crypto_parser.parse_known_args(an_input.split())

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command"""
        self.print_help(self.current_coin)

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_load(self, other_args):
        self.current_coin, self.current_df = coin_api.load(other_args)

    def call_view(self, _):
        if self.current_coin:
            coin_api.view(self.current_coin, self.current_df)

        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_clear(self, _):
        self.current_coin = None
        self.current_df = pd.DataFrame()


def menu():
    crypto_controller = CryptoController()
    crypto_controller.print_help(crypto_controller.current_coin)
    plt.close("all")
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in crypto_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (crypto)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)> ")

        try:
            process_input = crypto_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
