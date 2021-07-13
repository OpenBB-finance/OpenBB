""" Alpha Vantage Controller """
__docformat__ = "numpy"

import argparse
import os
from typing import List
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.fundamental_analysis.alpha_vantage import av_view
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session


class AlphaVantageController:
    """Alpha Vantage Controller"""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "overview",
        "key",
        "income",
        "balance",
        "cash",
        "earnings",
    ]

    def __init__(self, ticker: str, start: str, interval: str):
        """Constructor

        Parameters
        ----------
        ticker : str
            Fundamental analysis ticker symbol
        start : str
            Stat date of the stock data
        interval : str
            Stock data interval
        """

        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.av_parser = argparse.ArgumentParser(add_help=False, prog="av")
        self.av_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/"
            "tree/main/gamestonk_terminal/fundamental_analysis/alpha_vantage"
        )
        intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]

        if self.start:
            print(
                f"\n{intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
            )
        else:
            print(f"\n{intraday} Stock: {self.ticker}")

        print("\nAlpha Vantage:")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   help          show this alpha vantage menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("   overview      overview of the company")
        print("   key           company key metrics")
        print("   income        income statements of the company")
        print("   balance       balance sheet of the company")
        print("   cash          cash flow of the company")
        print("   earnings      earnings dates and reported EPS")
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

        (known_args, other_args) = self.av_parser.parse_known_args(an_input.split())

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

    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        av_view.overview(other_args, self.ticker)

    def call_key(self, other_args: List[str]):
        """Process overview command"""
        av_view.key(other_args, self.ticker)

    def call_income(self, other_args: List[str]):
        """Process income command"""
        av_view.income_statement(other_args, self.ticker)

    def call_balance(self, other_args: List[str]):
        """Process balance command"""
        av_view.balance_sheet(other_args, self.ticker)

    def call_cash(self, other_args: List[str]):
        """Process cash command"""
        av_view.cash_flow(other_args, self.ticker)

    def call_earnings(self, other_args: List[str]):
        """Process earnings command"""
        av_view.earnings(other_args, self.ticker)


def menu(ticker: str, start: str, interval: str):
    """Alpha Vantage menu

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    start : str
        Start date of the stock data
    interval : str
        Stock data interval
    """

    av_controller = AlphaVantageController(ticker, start, interval)
    av_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in av_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (fa)>(av)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (fa)>(av)> ")

        try:
            process_input = av_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
