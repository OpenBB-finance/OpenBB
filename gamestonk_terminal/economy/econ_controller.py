""" Econ Controller """
__docformat__ = "numpy"

import argparse
import os
from typing import List
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.economy import fred_view
from gamestonk_terminal.economy import finnhub_view
from gamestonk_terminal.economy import cnn_view
from gamestonk_terminal.economy import wsj_view


class EconomyController:
    """Economy Controller"""

    # Command choices
    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
        "events",
        "fred",
        "vixcls",
        "gdp",
        "unrate",
        "dgs1",
        "dgs5",
        "dgs10",
        "dgs30",
        "mortgage30us",
        "fedfunds",
        "aaa",
        "dexcaus",
        "feargreed",
        "overview",
        "indices",
        "futures",
        "us_bonds",
        "gl_bonds",
        "futures",
        "currencies",
    ]

    def __init__(self):
        """Constructor"""
        self.econ_parser = argparse.ArgumentParser(add_help=False, prog="econ")
        self.econ_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    @staticmethod
    def print_help():
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/economy"
        )
        print("\nEconomic Data:")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print(" ")
        print("   feargreed     CNN Fear and Greed Index")
        print("   events        economic impact events [Finnhub]")
        print(
            "   fred          display customized FRED data from https://fred.stlouisfed.org"
        )
        print("   vixcls        Volatility Index")
        print("   gdp           Gross Domestic Product")
        print("   unrate        Unemployment Rate")
        print("   dgs1          1-year Treasury Constant Maturity Rate")
        print("   dgs5          5-year Treasury Constant Maturity Rate")
        print("   dgs10         10-year Treasury Constant Maturity Rate")
        print("   dgs30         30-year Treasury Constant Maturity Rate")
        print("   mortgage30us  30-year Fixed Rate Mortgage Average")
        print("   fedfunds      Effective Federal Funds Rate")
        print("   aaa           Moody's Seasoned AAA Corporate Bond Yield")
        print("   dexcaus       Canada / U.S. Foreign Exchange Rate (CAD per 1 USD)")
        print("")
        print("Wall St. Journal:")
        print("   overview      market data overview")
        print("   indices       us indices overview")
        print("   futures       futures overview")
        print("   us_bonds      us bond overview")
        print("   gl_bonds      global bonds overview")
        print("   currencies    currency overview")
        print("")
        return

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

        (known_args, other_args) = self.econ_parser.parse_known_args(an_input.split())

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

    def call_events(self, other_args: List[str]):
        """Process events command"""
        finnhub_view.economy_calendar_events(other_args)

    def call_fred(self, other_args: List[str]):
        """Process fred command"""
        fred_view.display_fred(other_args, "")

    def call_vixcls(self, other_args: List[str]):
        """Process vixcls command"""
        fred_view.display_fred(other_args, "VIXCLS")

    def call_gdp(self, other_args: List[str]):
        """Process gdp command"""
        fred_view.display_fred(other_args, "GDP")

    def call_unrate(self, other_args: List[str]):
        """Process unrate command"""
        fred_view.display_fred(other_args, "UNRATE")

    def call_dgs1(self, other_args: List[str]):
        """Process dgs1 command"""
        fred_view.display_fred(other_args, "DGS1")

    def call_dgs5(self, other_args: List[str]):
        """Process dgs5 command"""
        fred_view.display_fred(other_args, "DGS5")

    def call_dgs10(self, other_args: List[str]):
        """Process dgs10 command"""
        fred_view.display_fred(other_args, "DGS10")

    def call_dgs30(self, other_args: List[str]):
        """Process dgs30 command"""
        fred_view.display_fred(other_args, "DGS30")

    def call_mortgage30us(self, other_args: List[str]):
        """Process mortgage30us command"""
        fred_view.display_fred(other_args, "MORTGAGE30US")

    def call_fedfunds(self, other_args: List[str]):
        """Process fedfunds command"""
        fred_view.display_fred(other_args, "FEDFUNDS")

    def call_aaa(self, other_args: List[str]):
        """Process aaa command"""
        fred_view.display_fred(other_args, "AAA")

    def call_dexcaus(self, other_args: List[str]):
        """Process dexcaus command"""
        fred_view.display_fred(other_args, "DEXCAUS")

    def call_feargreed(self, other_args: List[str]):
        """Process feargreed command"""
        cnn_view.fear_and_greed_index(other_args)

    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        wsj_view.display_overview(other_args)

    def call_indices(self, other_args: List[str]):
        """Process indices command"""
        wsj_view.display_indices(other_args)

    def call_futures(self, other_args: List[str]):
        """Process futures command"""
        wsj_view.display_futures(other_args)

    def call_us_bonds(self, other_args: List[str]):
        """Process us_bonds command"""
        wsj_view.display_usbonds(other_args)

    def call_gl_bonds(self, other_args: List[str]):
        """Process gl_bonds command"""
        wsj_view.display_glbonds(other_args)

    def call_currencies(self, other_args: List[str]):
        """Process curremcies command"""
        wsj_view.display_currencies(other_args)


def menu():
    """Econ Menu"""

    econ_controller = EconomyController()
    econ_controller.print_help()

    # Loop forever and ever
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in econ_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (econ)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (econ)> ")
        try:
            process_input = econ_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
