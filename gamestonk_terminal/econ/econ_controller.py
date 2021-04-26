""" Econ Controller """
__docformat__ = "numpy"

import argparse
from typing import List
from matplotlib import pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.econ import fred_view, vix_view


class EconController:
    """Econ Controller"""

    # Command choices
    CHOICES = [
        "help",
        "q",
        "quit",
        "gdp",
        "unemp",
        "t1",
        "t5",
        "t10",
        "t30",
        "mort30",
        "fedrate",
        "moodAAA",
        "usdcad",
        "cust",
        "view",
    ]

    def __init__(self):
        """Constructor"""
        self.disc_parser = argparse.ArgumentParser(add_help=False, prog="econ")
        self.disc_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    @staticmethod
    def print_help():
        """Print help"""

        print("\nEconomic Data:")
        print("   help          show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print(" ")
        print("VIX:\n")
        print("   view          plot VIX")
        print("FRED:\n")
        print("   gdp           GDP")
        print("   unemp         Unemployment Rate")
        print("   t1            1-Year Treasury Constant Maturity Rate")
        print("   t5            5-Year Treasury Constant Maturity Rate")
        print("   t10           10-Year Treasury Constant Maturity Rate")
        print("   t30           30-Year Treasury Constant Maturity Rate")
        print("   mort30        30-Year Fixed Rate Mortgage Average")
        print("   fedrate       Effective Federal Funds Rate")
        print("   moodAAA       Moody's Seasoned AAA Corporate Bond Yield")
        print("   usdcad        Canada / U.S. Foreign Exchange Rate (CAD per 1 USD)")
        print("   cust          User Specified FRED Data - Please Specify --id")
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
        (known_args, other_args) = self.disc_parser.parse_known_args(an_input.split())

        fred_data_list = [
            "gdp",
            "unemp",
            "t1",
            "t5",
            "t10",
            "t30",
            "mort30",
            "fedrate",
            "moodAAA",
            "usdcad",
        ]
        vix_command_list = ["view"]
        if known_args.cmd in fred_data_list:
            return getattr(self, "call_fred_api")(other_args, known_args.cmd)

        if known_args.cmd in vix_command_list:
            return getattr(self, "call_VIX")(other_args, known_args.cmd)

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

    def call_fred_api(self, other_args: List[str], cmd: str):
        """Process Fred Data call"""
        fred_view.get_fred_data(other_args, cmd)

    def call_VIX(self, other_args: List[str], cmd: str):
        """Process a VIX Call."""
        if cmd == "view":
            vix_view.view_vix(other_args)
        else:
            print("The command selected doesn't exist\n")

    def call_cust(self, other_args: List[str]):
        """Process cust call"""
        fred_view.custom_data(other_args)


def menu():
    """Econ Menu"""

    econ_controller = EconController()

    plt.close("all")

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
