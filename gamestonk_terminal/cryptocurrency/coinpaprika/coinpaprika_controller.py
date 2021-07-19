"""CoinPaprika Controller"""
__docformat__ = "numpy"

# pylint: disable=inconsistent-return-statements, too-many-public-methods, too-many-lines, redefined-builtin

import argparse
import os
import pandas as pd
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.coinpaprika import coinpaprika_view
from gamestonk_terminal.technical_analysis import ta_controller


class PaprikaController:

    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
        "clear",
        "global",
        "search",
        "coins",
        "info",
        "markets",
        "exchanges",
        "ex_markets",
        "platforms",
        "contracts",
        "events",
        "twitter",
        "ex",
        "mkt",
        "chart",
        "ta",
        "ps",
        "basic",
        "load",
        "find",
    ]

    def __init__(self):
        """CONSTRUCTOR"""

        self._paprika_parser = argparse.ArgumentParser(add_help=False, prog="cp")
        self._paprika_parser.add_argument("cmd", choices=self.CHOICES)
        self.current_coin = None
        self.current_currency = None
        self.current_df = pd.DataFrame()

    def print_help(self):
        """Print help"""
        print("\nCoinPaprika:")
        print("   cls             clear screen")
        print("   ?/help          show this menu again")
        print("   q               quit this menu, and shows back to main menu")
        print("   quit            quit to abandon program")
        print("")
        print("Coin")
        print("   find            alternate way to search for coins")
        print("   load            load cryptocurrency data")
        print("   clear           remove loaded coin")
        print("")
        print(f"Loaded coin: {self.current_coin}")
        print("")
        print("   chart           price chart for loaded coin")
        print(">  ta              technical analysis menu for loaded coin")
        print("   basic           basic information about loaded coin")
        print("   ps              price and supply related metrics for loaded coin")
        print("   mkt             all markets for loaded coin")
        print("   ex              all exchanges where loaded coin is listed")
        print("   twitter         tweets for loaded coin")
        print("   events          events related to loaded coin")
        print("")
        print("Overview:")
        print("   global          global crypto market info")
        print("   coins           coins available on CoinPaprika")
        print("   info            basic info about all coins available on CoinPaprika")
        print(
            "   markets         market related info about all coins available on CoinPaprika"
        )
        print("   search          search for coins, exchanges, people on CoinPaprika")
        print("   exchanges       list all exchanges")
        print("   ex_markets      all available markets on given exchange")
        print(
            "   platforms       list blockchain platforms eg. ethereum, solana, kusama, terra"
        )
        print("   contracts       all smart contracts for given platform")

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

        (known_args, other_args) = self._paprika_parser.parse_known_args(
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

    def call_search(self, other_args):
        """Process search command"""
        coinpaprika_view.search(other_args=other_args)

    def call_load(self, other_args):
        """Process load command"""
        self.current_coin = coinpaprika_view.load(other_args)

    def call_chart(self, other_args):
        """Process chart command"""
        if self.current_coin:
            coinpaprika_view.chart(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_ps(self, other_args):
        """Process ps command"""
        if self.current_coin:
            coinpaprika_view.price_supply(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_basic(self, other_args):
        """Process ps command"""
        if self.current_coin:
            coinpaprika_view.basic(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_mkt(self, other_args):
        """Process market command"""
        if self.current_coin:
            coinpaprika_view.markets(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_ex(self, other_args):
        """Process ex command"""
        if self.current_coin:
            coinpaprika_view.exchanges(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_events(self, other_args):
        """Process events command"""
        if self.current_coin:
            coinpaprika_view.events(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_twitter(self, other_args):
        """Process twitter command"""
        if self.current_coin:
            coinpaprika_view.twitter(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_clear(self, _):
        """Process clear command"""
        if self.current_coin:
            print(
                f"Current coin {self.current_coin} was removed. You can load new coin with load -c <coin>"
            )
            print("")
            self.current_coin = None
            self.current_df = pd.DataFrame()
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    # pylint: disable=inconsistent-return-statements
    def call_ta(self, other_args):
        """Process ta command"""
        if self.current_coin:
            self.current_df, self.current_currency = coinpaprika_view.ta(
                self.current_coin, other_args
            )
            if self.current_df is not None:
                try:
                    quit = ta_controller.menu(
                        stock=self.current_df,
                        ticker=self.current_coin,
                        start=self.current_df.index[0],
                        interval="",
                        context="(crypto)>(cp)",
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
            print("Please load a coin through either load - coin", "\n")
            return

    def call_global(self, other_args):
        """Process global command"""
        coinpaprika_view.global_market(other_args=other_args)

    def call_coins(self, other_args):
        """Process coins command"""
        coinpaprika_view.coins(other_args=other_args)

    def call_markets(self, other_args):
        """Process markets command"""
        coinpaprika_view.all_coins_market_info(other_args=other_args)

    def call_ex_markets(self, other_args):
        """Process ex_markets command"""
        coinpaprika_view.exchange_markets(other_args=other_args)

    def call_info(self, other_args):
        """Process info command"""
        coinpaprika_view.all_coins_info(other_args=other_args)

    def call_exchanges(self, other_args):
        """Process coins_market command"""
        coinpaprika_view.all_exchanges(other_args=other_args)

    def call_platforms(self, other_args):
        """Process platforms command"""
        coinpaprika_view.all_platforms(other_args=other_args)

    def call_contracts(self, other_args):
        """Process contracts command"""
        coinpaprika_view.contracts(other_args=other_args)

    def call_find(self, other_args):
        """Process find command"""
        coinpaprika_view.find(other_args=other_args)


def menu():
    paprika_controller = PaprikaController()
    paprika_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in paprika_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (crypto)>(cp)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(cp)> ")

        try:
            process_input = paprika_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
