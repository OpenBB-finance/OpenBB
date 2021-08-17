"""Cryptocurrency Discovery Controller"""
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
from gamestonk_terminal.cryptocurrency.cryptocurrency_helpers import all_coins


class DiscoveryController:

    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
        "coins",
        "cpsearch",
        "cmctop",
        "cgtrending",
        "cgvoted",
        "cgvisited",
        "cgvolume",
        "cgrecently",
        "cgsentiment",
        "cggainers",
        "cglosers",
        "cgyfarms",
        "cgdefi",
        "cgdex",
        "cgnft",
    ]

    def __init__(self):
        """CONSTRUCTOR"""

        self._discovery_parser = argparse.ArgumentParser(add_help=False, prog="disc")
        self._discovery_parser.add_argument("cmd", choices=self.CHOICES)

    def print_help(self):
        """Print help"""
        help_text = """
Discovery:
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program
    coins       search for coins on CoinGecko, Binance, CoinPaprika

CoinGecko:
    cgtrending        trending coins on CoinGecko
    cgvoted           most voted coins on CoinGecko
    cgvisited         most visited coins on CoinGecko
    cgvolume          coins with highest volume on CoinGecko
    cgrecently        recently added on CoinGecko
    cgsentiment       coins with most positive sentiment
    cggainers         top gainers - coins which price gained the most in given period
    cglosers          top losers - coins which price dropped the most in given period
    cgyfarms          top yield farms
    cgdefi            top defi protocols
    cgdex             top decentralized exchanges
    cgnft             top non fungible tokens
CoinPaprika:
    cpsearch          search on CoinPaprika
CoinMarketCap:
    cmctop            top coins from CoinMarketCap

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
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program."""
        return True

    def call_coins(self, other_args):
        """Process coins command"""
        all_coins(other_args=other_args)

    def call_cggainers(self, other_args):
        """Process gainers command"""
        pycoingecko_view.gainers(other_args)

    def call_cglosers(self, other_args):
        """Process losers command"""
        pycoingecko_view.losers(other_args)

    def call_cgtrending(self, other_args):
        """Process trending command"""
        pycoingecko_view.discover(category="trending", other_args=other_args)

    def call_cgvoted(self, other_args):
        """Process most_voted command"""
        pycoingecko_view.discover(category="most_voted", other_args=other_args)

    def call_cgrecently(self, other_args):
        """Process recently command"""
        pycoingecko_view.recently_added(other_args=other_args)

    def call_cgvisited(self, other_args):
        """Process most_visited command"""
        pycoingecko_view.discover(category="most_visited", other_args=other_args)

    def call_cgsentiment(self, other_args):
        """Process sentiment command"""
        pycoingecko_view.discover(category="positive_sentiment", other_args=other_args)

    def call_cgyfarms(self, other_args):
        """Process yfarms command"""
        pycoingecko_view.yfarms(other_args=other_args)

    def call_cgvolume(self, other_args):
        """Process top_volume command"""
        pycoingecko_view.top_volume_coins(other_args=other_args)

    def call_cgdefi(self, other_args):
        """Process top_defi command"""
        pycoingecko_view.top_defi_coins(other_args=other_args)

    def call_cgdex(self, other_args):
        """Process top_dex command"""
        pycoingecko_view.top_dex(other_args=other_args)

    def call_cgnft(self, other_args):
        """Process top_nft command"""
        pycoingecko_view.top_nft(other_args=other_args)

    def call_cmctop(self, other_args):
        """Process top command"""
        coinmarketcap_view.get_cmc_top_n(other_args)

    def call_cpsearch(self, other_args):
        """Process search command"""
        coinpaprika_view.search(other_args=other_args)


def menu():
    disc_controller = DiscoveryController()
    disc_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in disc_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (crypto)>(disc)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(disc)> ")

        try:
            process_input = disc_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
