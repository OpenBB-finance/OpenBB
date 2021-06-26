"""Cryptocurrency Controller"""
__docformat__ = "numpy"
# pylint: disable=R0904, C0302
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.coingecko import pycoingecko_view
from gamestonk_terminal.cryptocurrency import ta_crypto_controller


class GeckoCoinController:

    CHOICES = [
        "help",
        "q",
        "quit",
        "load",
        "clear",
        "chart",
        "ta",
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

    def print_help(self):
        """Print help"""
        print("\nCryptocurrency:")
        print("   help            show this menu again")
        print("   q               quit this menu, and shows back to main menu")
        print("   quit            quit to abandon program")
        print("")
        print("Coingecko Coin Menu:")
        print("   load            load cryptocurrency data")
        print("   clear           remove loaded coin")
        print("   chart           show price chart for loaded coin")
        print("   ta              technical analysis menu for loaded coin")
        print("   info            show basic information about loaded coin")
        print("   market          show market stats about loaded coin")
        print("   ath             show all time high related stats for loaded coin")
        print("   atl             show all time low related stats for loaded coin")
        print(
            "   web             show found websites for loaded coin e.g forum, homepage"
        )
        print(
            "   social          show social portals urls for loaded coin, e.g reddit, twitter"
        )
        print(
            "   score           show different kind of scores for loaded coin, e.g developer score, sentiment score"
        )
        print("   dev             show github, bitbucket coin development statistics")
        print("   bc              show url to blockchain explorers for loaded coin")
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
        """Process load command"""
        self.current_coin = pycoingecko_view.load(other_args)

    def call_chart(self, other_args):
        """Process chart command"""
        if self.current_coin:
            pycoingecko_view.view(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_info(self, other_args):
        """Process info command"""
        if self.current_coin:
            pycoingecko_view.base_info(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_market(self, other_args):
        """Process market command"""
        if self.current_coin:
            pycoingecko_view.market_data(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_web(self, other_args):
        """Process web command"""
        if self.current_coin:
            pycoingecko_view.web(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_social(self, other_args):
        """Process social command"""
        if self.current_coin:
            pycoingecko_view.social(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_dev(self, other_args):
        """Process dev command"""
        if self.current_coin:
            pycoingecko_view.dev(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_ath(self, other_args):
        """Process ath command"""
        if self.current_coin:
            pycoingecko_view.ath(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_atl(self, other_args):
        """Process atl command"""
        if self.current_coin:
            pycoingecko_view.atl(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_score(self, other_args):
        """Process score command"""
        if self.current_coin:
            pycoingecko_view.score(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_bc(self, other_args):
        """Process bc command"""
        if self.current_coin:
            pycoingecko_view.blockchain_explorers(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_clear(self, _):
        """Process clear command"""
        if self.current_coin:
            print(
                f"Current coin {self.current_coin.coin_symbol} was removed. You can load new coin with load -c <coin>"
            )
            self.current_coin = None
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    # pylint: disable=inconsistent-return-statements
    def call_ta(self, other_args):
        """Process ta command"""
        if self.current_coin:
            self.current_df = pycoingecko_view.ta(self.current_coin, other_args)
            if self.current_df is not None:
                try:
                    self.current_df = self.current_df[["price"]].rename(
                        columns={"price": "4. close"}
                    )
                    self.current_df.index.name = "date"

                    return ta_crypto_controller.menu(
                        self.current_df,
                        self.current_coin.coin_symbol,
                        self.current_df.index[0],
                        "",
                    )
                except (ValueError, KeyError) as e:
                    print(e)
            else:
                return
        else:
            print("Please load a coin through either load - coin", "\n")
            return


def menu():
    gecko_controller = GeckoCoinController()
    gecko_controller.print_help()
    plt.close("all")

    while True:
        # Get input command from user
        if gecko_controller.current_coin:
            print(f"loaded coin: ({gecko_controller.current_coin.coin_symbol})")

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
