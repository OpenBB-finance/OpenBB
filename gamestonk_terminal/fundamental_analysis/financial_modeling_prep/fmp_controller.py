""" Financial Modeling Prep Controller """
__docformat__ = "numpy"

import argparse
import os
from typing import List
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.fundamental_analysis.financial_modeling_prep import fmp_view
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
)
from gamestonk_terminal.menu import session


class FinancialModelingPrepController:
    """Financial Modeling Prep Controller"""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "profile",
        "quote",
        "enterprise",
        "dcf",
        "income",
        "balance",
        "cash",
        "metrics",
        "ratios",
        "growth",
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
        self.fmp_parser = argparse.ArgumentParser(add_help=False, prog="fmp")
        self.fmp_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/"
            "tree/main/gamestonk_terminal/fundamental_analysis/financial_modeling_prep"
        )
        intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]

        if self.start:
            print(
                f"\n{intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
            )
        else:
            print(f"\n{intraday} Stock: {self.ticker}")

        print("\nFinancial Modeling Prep API")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("   profile       profile of the company")
        print("   quote         quote of the company")
        print("   enterprise    enterprise value of the company over time")
        print("   dcf           discounted cash flow of the company over time")
        print("   income        income statements of the company")
        print("   balance       balance sheet of the company")
        print("   cash          cash flow statement of the company")
        print("   metrics       key metrics of the company")
        print("   ratios        financial ratios of the company")
        print("   growth        financial statement growth of the company")
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

        (known_args, other_args) = self.fmp_parser.parse_known_args(an_input.split())

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

    def call_profile(self, other_args: List[str]):
        """Process profile command"""
        fmp_view.profile(other_args, self.ticker)

    def call_quote(self, other_args: List[str]):
        """Process quote command"""
        fmp_view.quote(other_args, self.ticker)

    def call_enterprise(self, other_args: List[str]):
        """Process income command"""
        fmp_view.enterprise(other_args, self.ticker)

    def call_dcf(self, other_args: List[str]):
        """Process dcf command"""
        fmp_view.discounted_cash_flow(other_args, self.ticker)

    def call_income(self, other_args: List[str]):
        """Process income command"""
        fmp_view.income_statement(other_args, self.ticker)

    def call_balance(self, other_args: List[str]):
        """Process balance command"""
        fmp_view.balance_sheet(other_args, self.ticker)

    def call_cash(self, other_args: List[str]):
        """Process cash command"""
        fmp_view.cash_flow(other_args, self.ticker)

    def call_metrics(self, other_args: List[str]):
        """Process metrics command"""
        fmp_view.key_metrics(other_args, self.ticker)

    def call_ratios(self, other_args: List[str]):
        """Process cash command"""
        fmp_view.financial_ratios(other_args, self.ticker)

    def call_growth(self, other_args: List[str]):
        """Process cash command"""
        fmp_view.financial_statement_growth(other_args, self.ticker)


def menu(ticker: str, start: str, interval: str):
    """Financial Modeling Prep menu

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    start : str
        Start date of the stock data
    interval : str
        Stock data interval
    """

    fmp_controller = FinancialModelingPrepController(ticker, start, interval)
    fmp_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in fmp_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (fa)>(fmp)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (fa)>(fmp)> ")

        try:
            process_input = fmp_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
