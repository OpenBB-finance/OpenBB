"""Government Controller Module"""
__docformat__ = "numpy"

import argparse
from typing import List
from matplotlib import pyplot as plt
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.government import quiverquant_view


class GovController:
    """Gov Controller class"""

    # Command choices
    CHOICES = [
        "help",
        "q",
        "quit",
        "last_congress",
        "buy_congress",
        "sell_congress",
        "congress",
    ]

    def __init__(
        self,
        ticker: str,
    ):
        """Constructor"""
        self.ticker = ticker
        self.gov_parser = argparse.ArgumentParser(add_help=False, prog="gov")
        self.gov_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    @staticmethod
    def print_help(self):
        """Print help"""

        print("\nExploratory Data Analysis:")
        print("   help             show this comparison analysis menu again")
        print("   q                quit this menu, and shows back to main menu")
        print("   quit             quit to abandon program")
        print("")
        print("Explore:")
        print("   last_congress    last congress trading")
        print("   buy_congress     top buy congress tickers")
        print("   sell_congress    top sell congress tickers")
        print("")
        if self.ticker:
            print(f"Ticker: {self.ticker}")
            print("   congress         congress trades on the ticker")
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
        (known_args, other_args) = self.gov_parser.parse_known_args(an_input.split())

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command"""
        self.print_help(self)

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_last_congress(self, other_args: List[str]):
        """Process last_congress command"""
        quiverquant_view.last_congress(other_args)

    def call_buy_congress(self, other_args: List[str]):
        """Process buy_congress command"""
        quiverquant_view.buy_congress(other_args)

    def call_sell_congress(self, other_args: List[str]):
        """Process sell_congress command"""
        quiverquant_view.sell_congress(other_args)

    def call_congress(self, other_args: List[str]):
        """Process congress command"""
        quiverquant_view.congress(other_args, self.ticker)


def menu(ticker: str):
    """Government Menu"""

    gov_controller = GovController(ticker)
    gov_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in gov_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (gov)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (gov)> ")

        try:
            plt.close("all")

            process_input = gov_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
