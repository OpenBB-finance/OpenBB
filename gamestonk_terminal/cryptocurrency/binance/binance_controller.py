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
from gamestonk_terminal.cryptocurrency.binance import binance_model
from gamestonk_terminal.technical_analysis import ta_controller


class BinanceController:

    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
        "book",
        "candle",
        "balance",
        "load",
        "ta",
        "clear",
    ]

    def __init__(self):
        """CONSTRUCTOR"""

        self._binance_parser = argparse.ArgumentParser(add_help=False, prog="bin")
        self._binance_parser.add_argument("cmd", choices=self.CHOICES)
        self.current_coin = None
        self.current_currency = None
        self.current_df = pd.DataFrame()
        self.source = ""

    def print_help(self):
        """Print help"""
        print("\nBinance:")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print(f"Loaded coin: {self.current_coin}")
        print("")
        print("   load          load coin/currency to use and load candle data")
        print("   clear         clear loaded coin")
        print("   book          show order book")
        print("   candle        show candles")
        print("   balance       show coin balance")
        print("   ta            open technical analysis menu")
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

        (known_args, other_args) = self._binance_parser.parse_known_args(
            an_input.split()
        )

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

    def call_book(self, other_args):
        """Process book command"""
        binance_model.order_book(other_args, self.current_coin, self.current_currency)

    def call_candle(self, _):
        """Process candle command"""
        if self.current_coin is None and self.current_df.empty:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")
        else:
            binance_model.show_candles(
                self.current_df, self.current_coin, self.current_currency
            )

    def call_balance(self, _):
        """Process balance command"""
        binance_model.balance(self.current_coin)

    def call_load(self, other_args):
        """Process select command"""
        (
            self.current_coin,
            self.current_currency,
            self.current_df,
        ) = binance_model.select_binance_coin(other_args)
        self.source = "BIN"
        print("")

    def call_clear(self, _):
        """Process clear command"""
        if self.current_coin:
            print(
                f"Current coin {self.current_coin} was removed. You can load new coin with load -c <coin>"
            )
            print("")
            self.current_coin = None
            self.current_currency = None
            self.current_df = pd.DataFrame()
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    # pylint: disable=inconsistent-return-statements
    def call_ta(self, _):
        """Process ta command"""
        if not self.current_coin:
            print("Please load a coin through either load -c ", "\n")

        elif self.current_df.empty:
            print("Price dataframe is empty")

        else:

            try:
                quit = ta_controller.menu(
                    stock=self.current_df,
                    ticker=self.current_coin,
                    start=self.current_df.index[0],
                    interval="",
                    context="(crypto)>(bin)",
                )
                print("")
                if quit is not None:
                    if quit is True:
                        return quit

            except (ValueError, KeyError) as e:
                print(e)


def menu():
    binance_controller = BinanceController()
    binance_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in binance_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (crypto)>(bin)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(bin)> ")

        try:
            process_input = binance_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
