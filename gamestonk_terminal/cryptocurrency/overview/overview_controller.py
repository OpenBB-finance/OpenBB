"""Cryptocurrency Overview Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622
import argparse
import os
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.overview import (
    pycoingecko_view,
    coinpaprika_view,
)


class Controller:

    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
        "cgglobal",
        "cgdefi",
        "cgnews",
        "cgstables",
        "cgnft",
        "cgnftday",
        "cgexchanges",
        "cgexrates",
        "cgplatforms",
        "cgproducts",
        "cgindexes",
        "cgderivatives",
        "cgcategories",
        "cghold",
        "cgcompanies",
        "cpglobal",
        "cpmarkets",
        "cpexmarkets",
        "cpinfo",
        "cpexchanges",
        "cpplatforms",
        "cpcontracts",
    ]

    def __init__(self):
        """CONSTRUCTOR"""

        self._overview_parser = argparse.ArgumentParser(add_help=False, prog="ov")
        self._overview_parser.add_argument("cmd", choices=self.CHOICES)

    def print_help(self):
        """Print help"""
        help_text = """
Overview:
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program

CoinGecko:
    cgglobal          global crypto market info
    cgnews            last news available on CoinGecko
    cgdefi            global DeFi market info
    cgstables         stablecoins
    cgnft             non fungible token market status
    cgnftday          non fungible token of the day
    cgexchanges       top crypto exchanges
    cgexrates         coin exchange rates
    cgplatforms       crypto financial platforms
    cgproducts        crypto financial products
    cgindexes         crypto indexes
    cgderivatives     crypto derivatives
    cgcategories      crypto categories
    cghold            ethereum, bitcoin holdings overview statistics
    cgcompanies       ethereum, bitcoin holdings by public companies
CoinPaprika:
    cpglobal          global crypto market info
    cpinfo            basic info about all coins available on CoinPaprika
    cpmarkets         market related info about all coins available on CoinPaprika
    cpexchanges       list all exchanges
    cpexmarkets       all available markets on given exchange
    cpplatforms       list blockchain platforms eg. ethereum, solana, kusama, terra
    cpcontracts       all smart contracts for given platform
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

        (known_args, other_args) = self._overview_parser.parse_known_args(
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

    def call_cghold(self, other_args):
        """Process hold command"""
        pycoingecko_view.holdings_overview(other_args)

    def call_cgcompanies(self, other_args):
        """Process companies command"""
        pycoingecko_view.holdings_companies_list(other_args)

    def call_cgnews(self, other_args):
        """Process news command"""
        pycoingecko_view.news(other_args=other_args)

    def call_cgcategories(self, other_args):
        """Process top_categories command"""
        pycoingecko_view.categories(other_args=other_args)

    def call_cgstables(self, other_args):
        """Process stables command"""
        pycoingecko_view.stablecoins(other_args=other_args)

    def call_cgnft(self, other_args):
        """Process nft command"""
        pycoingecko_view.nft_market_status(other_args=other_args)

    def call_cgnftday(self, other_args):
        """Process nft_today command"""
        pycoingecko_view.nft_of_the_day(other_args=other_args)

    def call_cgproducts(self, other_args):
        """Process products command"""
        pycoingecko_view.products(other_args=other_args)

    def call_cgplatforms(self, other_args):
        """Process platforms command"""
        pycoingecko_view.platforms(other_args=other_args)

    def call_cgexchanges(self, other_args):
        """Process exchanges command"""
        pycoingecko_view.exchanges(other_args=other_args)

    def call_cgexrates(self, other_args):
        """Process exchange_rates command"""
        pycoingecko_view.exchange_rates(other_args=other_args)

    def call_cgindexes(self, other_args):
        """Process indexes command"""
        pycoingecko_view.indexes(other_args=other_args)

    def call_cgderivatives(self, other_args):
        """Process derivatives command"""
        pycoingecko_view.derivatives(other_args=other_args)

    def call_cgglobal(self, other_args):
        """Process global command"""
        pycoingecko_view.global_market_info(other_args=other_args)

    def call_cgdefi(self, other_args):
        """Process defi command"""
        pycoingecko_view.global_defi_info(other_args=other_args)

    def call_cpglobal(self, other_args):
        """Process global command"""
        coinpaprika_view.global_market(other_args=other_args)

    def call_cpmarkets(self, other_args):
        """Process markets command"""
        coinpaprika_view.all_coins_market_info(other_args=other_args)

    def call_cpexmarkets(self, other_args):
        """Process ex_markets command"""
        coinpaprika_view.exchange_markets(other_args=other_args)

    def call_cpinfo(self, other_args):
        """Process info command"""
        coinpaprika_view.all_coins_info(other_args=other_args)

    def call_cpexchanges(self, other_args):
        """Process coins_market command"""
        coinpaprika_view.all_exchanges(other_args=other_args)

    def call_cpplatforms(self, other_args):
        """Process platforms command"""
        coinpaprika_view.all_platforms(other_args=other_args)

    def call_cpcontracts(self, other_args):
        """Process contracts command"""
        coinpaprika_view.contracts(other_args=other_args)


def menu():
    overview_controller = Controller()
    overview_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in overview_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (crypto)>(ov)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(ov)> ")

        try:
            process_input = overview_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
