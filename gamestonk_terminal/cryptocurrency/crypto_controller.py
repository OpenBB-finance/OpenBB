"""Cryptocurrency Controller"""
__docformat__ = "numpy"

import argparse
import pandas as pd
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency import (
    binance_model,
    pycoingecko_view,
    coinmarketcap_view as cmc_view,
)


class CryptoController:

    CHOICES = [
        "help",
        "q",
        "quit",
        "load",
        "view",
        "top",
        "trend",
        "book",
        "trades",
        "candle",
        "balance",
        "add",
    ]

    def __init__(self):
        """CONSTRUCTOR"""

        self.crypto_parser = argparse.ArgumentParser(add_help=False, prog="crypto")
        self.crypto_parser.add_argument("cmd", choices=self.CHOICES)
        self.current_coin = None
        self.current_currency = None
        self.current_df = pd.DataFrame()

    @staticmethod
    def print_help(self):
        """Print help"""
        print("\nCryptocurrency:")
        print("   help          show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print(f"\nCurrent Coin: {self.current_coin}")
        print("")
        print("Coingecko:")
        print("   load          load cryptocurrency data")
        print("   view          load and view cryptocurrency data")
        print("   trend         show top 7 trending coins")
        print("")
        print("CoinMarketCap:")
        print("   top           view top coins from coinmarketcap")
        print("")
        print("Binance:")
        print("   add           add coin as current")
        print("   book          show order book")
        print("   candle        get klines/candles and plot")
        print("   balance       show coin balance")
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
        self.print_help(self)

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_load(self, other_args):
        """Load command - get df from gecko"""
        self.current_coin, self.current_df = pycoingecko_view.load(other_args)

    def call_view(self, other_args):
        """View command - plot loaded coin"""
        if self.current_coin:
            pycoingecko_view.view(self.current_coin, self.current_df, other_args)

        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_trend(self, _):
        """Trend command - show top 7 gecko coins"""
        pycoingecko_view.trend()

    def call_top(self, other_args):
        """Top command - get top n coins from coinmarketcap"""
        cmc_view.get_cmc_top_n(other_args)

    def call_book(self, other_args):
        """Book command - get order book from binance"""
        binance_model.order_book(self.current_coin + self.current_currency, other_args)

    def call_candle(self, other_args):
        """Candle command - show candle chart from binance"""
        binance_model.candles(self.current_coin + self.current_currency, other_args)

    def call_balance(self, other_args):
        """Balance command - check current holdings of coin in binance"""
        binance_model.balance(self.current_coin, other_args)

    def call_add(self, other_args):
        """Add command - set current coin for binance operations"""
        self.current_coin, self.current_currency = binance_model.add_binance_coin(
            other_args
        )
        print(f"{self.current_coin} loaded vs {self.current_currency}")
        print("")


def menu():
    crypto_controller = CryptoController()
    crypto_controller.print_help(crypto_controller)
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
