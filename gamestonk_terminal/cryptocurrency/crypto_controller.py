"""Cryptocurrency Controller"""
__docformat__ = "numpy"
# pylint: disable=R0904, C0302, R1710, W0622

import argparse
import os
import matplotlib.pyplot as plt
import pandas as pd
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.technical_analysis import ta_controller
from gamestonk_terminal.cryptocurrency.overview import overview_controller
from gamestonk_terminal.cryptocurrency.due_diligence import (
    dd_controller,
    coinpaprika_view,
    binance_view,
    pycoingecko_view,
)
from gamestonk_terminal.cryptocurrency.discovery import (
    discovery_controller,
)
from gamestonk_terminal.cryptocurrency.due_diligence import (
    finbrain_crypto_view,
)

from gamestonk_terminal.cryptocurrency.cryptocurrency_helpers import load, find
from gamestonk_terminal.cryptocurrency.report import report_controller


class CryptoController:
    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
    ]

    CHOICES_COMMAND = [
        "finbrain",
        "chart",
        "load",
        "find",
    ]

    CHOICES_MENUS = [
        "ta",
        "dd",
        "ov",
        "disc",
        "report",
    ]

    SOURCES = {
        "bin": "Binance",
        "cg": "CoinGecko",
        "cp": "CoinPaprika",
    }

    DD_VIEWS_MAPPING = {
        "cg": pycoingecko_view,
        "cp": coinpaprika_view,
        "bin": binance_view,
    }

    CHOICES += CHOICES_COMMAND
    CHOICES += CHOICES_MENUS

    def __init__(self):
        """CONSTRUCTOR"""

        self.crypto_parser = argparse.ArgumentParser(add_help=False, prog="crypto")
        self.crypto_parser.add_argument("cmd", choices=self.CHOICES)

        self.current_coin = ""
        self.current_df = pd.DataFrame()
        self.current_currency = ""
        self.source = ""

    def print_help(self):
        """Print help"""
        help_text = """https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/cryptocurrency

>> CRYPTO <<

What do you want to do?
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program
"""
        help_text += (
            f"\nCoin: {self.current_coin}" if self.current_coin != "" else "\nCoin: ?"
        )
        help_text += (
            f"\nSource: {self.SOURCES.get(self.source, '?')}\n"
            if self.source != ""
            else "\nSource: ?\n"
        )
        help_text += """
    load        load a specific cryptocurrency for analysis
    chart       view a candle chart for a specific cryptocurrency
    find        alternate way to search for coins
    finbrain    crypto sentiment from 15+ major news headlines

>   disc        discover trending cryptocurrencies,  e.g.: top gainers, losers, top sentiment
>   ov          overview of the cryptocurrencies,    e.g.: market cap, DeFi, latest news, top exchanges, stables
>   dd          due-diligence for loaded coin,       e.g.: coin information, social media, market stats
>   ta          technical analysis for loaded coin.  e.g.: ema, macd, rsi, adx, bbands, obv
>   report      generate automatic report
"""
        print(help_text)

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

    def call_load(self, other_args):
        """Process load command"""
        try:
            self.current_coin, self.source = load(
                coin=self.current_coin, other_args=other_args
            )
        except TypeError:
            print("Couldn't load data\n")

    def call_chart(self, other_args):
        """Process chart command"""
        if self.current_coin:
            getattr(self.DD_VIEWS_MAPPING[self.source], "chart")(
                self.current_coin, other_args
            )
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_ta(self, other_args):
        """Process ta command"""
        if self.current_coin:
            self.current_df, self.current_currency = getattr(
                self.DD_VIEWS_MAPPING[self.source], "load_ta_data"
            )(self.current_coin, other_args)
            if self.current_currency != "" and not self.current_df.empty:
                try:
                    quit = ta_controller.menu(
                        stock=self.current_df,
                        ticker=self.current_coin,
                        start=self.current_df.index[0],
                        interval="",
                    )
                    print("")
                    if quit is not None:
                        if quit is True:
                            return quit

                except (ValueError, KeyError) as e:
                    print(e)
            else:
                return

        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_disc(self, _):
        """Process disc command"""
        disc = discovery_controller.menu()
        if disc is False:
            self.print_help()
        else:
            return True

    def call_ov(self, _):
        """Process ov command"""
        ov = overview_controller.menu()
        if ov is False:
            self.print_help()
        else:
            return True

    def call_finbrain(self, other_args):
        """Process finbrain command"""
        finbrain_crypto_view.crypto_sentiment_analysis(other_args=other_args)

    def call_dd(self, _):
        """Process dd command"""
        if self.current_coin:
            dd = dd_controller.menu(self.current_coin, self.source)
            if dd is False:
                self.print_help()
            else:
                return True
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_report(self, _):
        """Process report command"""
        ret = report_controller.menu()

        if ret is False:
            self.print_help()
        else:
            return True

    def call_find(self, other_args):
        """Process find command"""
        find(other_args=other_args)


def menu():
    crypto_controller = CryptoController()
    crypto_controller.call_help(None)
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
