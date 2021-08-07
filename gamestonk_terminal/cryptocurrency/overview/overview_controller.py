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
        "cg_global",
        "cg_coins",
        "cg_defi",
        "cg_news",
        "cg_stables",
        "cg_nft",
        "cg_exchanges",
        "cg_exrates",
        "cg_platforms",
        "cg_products",
        "cg_indexes",
        "cg_derivatives",
        "cg_categories",
        "cg_hold",
        "cg_companies",
        "cp_global",
        "cp_markets",
        "cp_exmarkets",
        "cp_info",
        "cp_exchanges",
        "cp_platforms",
        "cp_contracts",
    ]

    def __init__(self):
        """CONSTRUCTOR"""

        self._overview_parser = argparse.ArgumentParser(add_help=False, prog="ov")
        self._overview_parser.add_argument("cmd", choices=self.CHOICES)

    def print_help(self):
        """Print help"""
        print("\nOverview:")
        print("   cls             clear screen")
        print("   ?/help          show this menu again")
        print("   q               quit this menu, and shows back to main menu")
        print("   quit            quit to abandon program")
        print("")

        print("")
        print("CoinGecko:")
        print("   cg_global          global crypto market info")
        print("   cg_news            last news available on CoinGecko")
        print("   cg_defi            global DeFi market info")
        print("   cg_stables         stablecoins")
        print("   cg_nft             non fungible token market status")
        print("   cg_exchanges       top crypto exchanges")
        print("   cg_exrates         coin exchange rates")
        print("   cg_platforms       crypto financial platforms")
        print("   cg_products        crypto financial products")
        print("   cg_indexes         crypto indexes")
        print("   cg_derivatives     crypto derivatives")
        print("   cg_categories      crypto categories")
        print("   cg_hold            ethereum, bitcoin holdings overview statistics")
        print("   cg_companies       ethereum, bitcoin holdings by public companies")
        print("")
        print("CoinPaprika:")
        print("   cp_global          global crypto market info")
        print(
            "   cp_info            basic info about all coins available on CoinPaprika"
        )
        print(
            "   cp_markets         market related info about all coins available on CoinPaprika"
        )
        print("   cp_exchanges       list all exchanges")
        print("   cp_exmarkets       all available markets on given exchange")
        print(
            "   cp_platforms       list blockchain platforms eg. ethereum, solana, kusama, terra"
        )
        print("   cp_contracts       all smart contracts for given platform")

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
        print("Moving back to (crypto) menu")
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program."""
        return True

    def call_cg_hold(self, other_args):
        """Process hold command"""
        pycoingecko_view.holdings_overview(other_args)

    def call_cg_companies(self, other_args):
        """Process companies command"""
        pycoingecko_view.holdings_companies_list(other_args)

    def call_cg_news(self, other_args):
        """Process news command"""
        pycoingecko_view.news(other_args=other_args)

    def call_cg_categories(self, other_args):
        """Process top_categories command"""
        pycoingecko_view.categories(other_args=other_args)

    def call_cg_stables(self, other_args):
        """Process stables command"""
        pycoingecko_view.stablecoins(other_args=other_args)

    def call_cg_nft(self, other_args):
        """Process top_volume command"""
        pycoingecko_view.nft_market_status(other_args=other_args)

    def call_cg_products(self, other_args):
        """Process products command"""
        pycoingecko_view.products(other_args=other_args)

    def call_cg_platforms(self, other_args):
        """Process platforms command"""
        pycoingecko_view.platforms(other_args=other_args)

    def call_cg_exchanges(self, other_args):
        """Process exchanges command"""
        pycoingecko_view.exchanges(other_args=other_args)

    def call_cg_exrates(self, other_args):
        """Process exchange_rates command"""
        pycoingecko_view.exchange_rates(other_args=other_args)

    def call_cg_indexes(self, other_args):
        """Process indexes command"""
        pycoingecko_view.indexes(other_args=other_args)

    def call_cg_derivatives(self, other_args):
        """Process derivatives command"""
        pycoingecko_view.derivatives(other_args=other_args)

    def call_cg_global(self, other_args):
        """Process global command"""
        pycoingecko_view.global_market_info(other_args=other_args)

    def call_cg_defi(self, other_args):
        """Process defi command"""
        pycoingecko_view.global_defi_info(other_args=other_args)

    def call_cp_global(self, other_args):
        """Process global command"""
        coinpaprika_view.global_market(other_args=other_args)

    def call_cp_markets(self, other_args):
        """Process markets command"""
        coinpaprika_view.all_coins_market_info(other_args=other_args)

    def call_cp_exmarkets(self, other_args):
        """Process ex_markets command"""
        coinpaprika_view.exchange_markets(other_args=other_args)

    def call_cp_info(self, other_args):
        """Process info command"""
        coinpaprika_view.all_coins_info(other_args=other_args)

    def call_cp_exchanges(self, other_args):
        """Process coins_market command"""
        coinpaprika_view.all_exchanges(other_args=other_args)

    def call_cp_platforms(self, other_args):
        """Process platforms command"""
        coinpaprika_view.all_platforms(other_args=other_args)

    def call_cp_contracts(self, other_args):
        """Process contracts command"""
        coinpaprika_view.contracts(other_args=other_args)


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
                f"{get_flair()} (crypto)>(ov)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(ov)> ")

        try:
            process_input = controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
