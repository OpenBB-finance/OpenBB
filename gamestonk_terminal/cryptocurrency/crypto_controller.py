"""Cryptocurrency Controller"""
__docformat__ = "numpy"
# pylint: disable=R0904, C0302, R1710
import argparse
import os
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.coinmarketcap import coinmarketcap_controller
from gamestonk_terminal.cryptocurrency.binance import binance_controller
from gamestonk_terminal.cryptocurrency.coingecko import pycoingecko_controller
from gamestonk_terminal.cryptocurrency import finbrain_crypto_view
from gamestonk_terminal.cryptocurrency.coinpaprika import coinpaprika_controller


class CryptoController:

    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
        "cg",
        "bin",
        "cmc",
        "finbrain",
        "cp",
    ]

    def __init__(self):
        """CONSTRUCTOR"""

        self.crypto_parser = argparse.ArgumentParser(add_help=False, prog="crypto")
        self.crypto_parser.add_argument("cmd", choices=self.CHOICES)

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/cryptocurrency"
        )
        print("\nCryptocurrency:")
        print("   cls             clear screen")
        print("   ?/help          show this menu again")
        print("   q               quit this menu, and shows back to main menu")
        print("   quit            quit to abandon program")
        print("")
        print("   finbrain        Crypto sentiment from 15+ major news headlines")
        print("")
        print(">  cg              CoinGecko overview (market statistics) and coin menu")
        print(">  cmc             Coinmarketcap menu")
        print(">  bin             Binance menu with order book, candles, ta.. ")
        print(">  cp              CoinPaprika menu")
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

        (known_args, other_args) = self.crypto_parser.parse_known_args(an_input.split())

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

    def call_cg(self, _):
        if pycoingecko_controller.menu():
            return True
        print("")

    def call_bin(self, _):
        """Process bin command"""
        if binance_controller.menu():
            return True
        print("")

    def call_cmc(self, _):
        """Process top command"""
        if coinmarketcap_controller.menu():
            return True
        print("")

    def call_finbrain(self, other_args):
        """Process sentiment command"""
        finbrain_crypto_view.crypto_sentiment_analysis(other_args=other_args)

    def call_cp(self, _):
        """Process cp command"""
        if coinpaprika_controller.menu():
            return True
        print("")


def menu():
    crypto_controller = CryptoController()
    crypto_controller.print_help()
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
