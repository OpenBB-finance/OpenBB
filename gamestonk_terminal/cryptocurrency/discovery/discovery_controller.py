"""Cryptocurrency Overview Controller"""
__docformat__ = "numpy"
# pylint: disable=R0904, C0302, W0622
import argparse
import os
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.discovery import (
    pycoingecko_view,
    coinpaprika_view,
    coinmarketcap_view,
)


class Controller:

    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
        "cp_search",
        "cp_coins",
        "cmc_top",
        "cg_trending",
        "cg_most_voted",
        "cg_most_visited",
        "cg_top_volume",
        "cg_recently",
        "cg_sentiment",
        "cg_gainers",
        "cg_losers",
        "cg_yfarms",
        "cg_top_defi",
        "cg_top_dex",
        "cg_top_nft",
        "cg_coins",
    ]

    def __init__(self):
        """CONSTRUCTOR"""

        self._discovery_parser = argparse.ArgumentParser(add_help=False, prog="disc")
        self._discovery_parser.add_argument("cmd", choices=self.CHOICES)

    def print_help(self):
        """Print help"""
        print("\nDiscovery:")
        print("   cls             clear screen")
        print("   ?/help          show this menu again")
        print("   q               quit this menu, and shows back to main menu")
        print("   quit            quit to abandon program")
        print("")

        print("CoinGecko:")
        print("   cg_coins           coins available on CoinGecko")
        print("   cg_trending        trending coins on CoinGecko")
        print("   cg_most_voted      most voted coins on CoinGecko")
        print("   cg_most_visited    most visited coins on CoinGecko")
        print("   cg_top_volume      coins with highest volume on CoinGecko")
        print("   cg_recently        recently added on CoinGecko")
        print("   cg_sentiment       coins with most positive sentiment")
        print(
            "   cg_gainers         top gainers - coins which price gained the most in given period "
        )
        print(
            "   cg_losers          top losers - coins which price dropped the most in given period "
        )
        print("   cg_yfarms          top yield farms")
        print("   cg_top_defi        top defi protocols")
        print("   cg_top_dex         top decentralized exchanges")
        print("   cg_top_nft         top non fungible tokens")
        print("")
        print("CoinPaprika:")
        print("   cp_coins           coins available on CoinPaprika")
        print("   cp_search          global crypto market info")
        print("")
        print("CoinMarket Cap:")
        print("   cmc_top            top coins from coinmarketcap")

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

        (known_args, other_args) = self._discovery_parser.parse_known_args(
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

    def call_cg_coins(self, other_args):
        """Process coins command"""
        pycoingecko_view.coin_list(other_args=other_args)

    def call_cg_gainers(self, other_args):
        """Process hold_comp command"""
        pycoingecko_view.gainers(other_args)

    def call_cg_losers(self, other_args):
        """Process hold_comp command"""
        pycoingecko_view.losers(other_args)

    def call_cg_trending(self, other_args):
        """Process trending command"""
        pycoingecko_view.discover(category="trending", other_args=other_args)

    def call_cg_most_voted(self, other_args):
        """Process most_voted command"""
        pycoingecko_view.discover(category="most_voted", other_args=other_args)

    def call_cg_recently(self, other_args):
        """Process recently command"""
        pycoingecko_view.recently_added(other_args=other_args)

    def call_cg_most_visited(self, other_args):
        """Process most_voted command"""
        pycoingecko_view.discover(category="most_visited", other_args=other_args)

    def call_cg_sentiment(self, other_args):
        """Process sentiment command"""
        pycoingecko_view.discover(category="positive_sentiment", other_args=other_args)

    def call_cg_yfarms(self, other_args):
        """Process yield_farms command"""
        pycoingecko_view.yfarms(other_args=other_args)

    def call_cg_top_volume(self, other_args):
        """Process top_volume command"""
        pycoingecko_view.top_volume_coins(other_args=other_args)

    def call_cg_top_defi(self, other_args):
        """Process top_volume command"""
        pycoingecko_view.top_defi_coins(other_args=other_args)

    def call_cg_top_dex(self, other_args):
        """Process top_volume command"""
        pycoingecko_view.top_dex(other_args=other_args)

    def call_cg_top_nft(self, other_args):
        """Process top_volume command"""
        pycoingecko_view.top_dex(other_args=other_args)

    def call_cmc_top(self, other_args):
        """Process top command"""
        coinmarketcap_view.get_cmc_top_n(other_args)

    def call_cp_coins(self, other_args):
        """Process coins command"""
        coinpaprika_view.coins(other_args=other_args)

    def call_cp_search(self, other_args):
        """Process coins command"""
        coinpaprika_view.search(other_args=other_args)


def menu():
    controller = Controller()
    controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (crypto)>(disc)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(disc)> ")

        try:
            process_input = controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
