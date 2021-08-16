""" Due Diligence Controller """
__docformat__ = "numpy"

import argparse
import os
from typing import List
from pandas.core.frame import DataFrame
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.stocks.due_diligence import business_insider_view as bi_view
from gamestonk_terminal.stocks.due_diligence import (
    financial_modeling_prep_view as fmp_view,
)
from gamestonk_terminal.stocks.due_diligence import finviz_view as fvz_view
from gamestonk_terminal.stocks.due_diligence import market_watch_view as mw_view
from gamestonk_terminal.stocks.due_diligence import reddit_view as r_view
from gamestonk_terminal.stocks.due_diligence import finnhub_view
from gamestonk_terminal.stocks.due_diligence import csimarket_view
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session


class DueDiligenceController:
    """Due Diligence Controller"""

    # Command choices
    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
        "red",
        "sec",
        "rating",
        "pt",
        "rot",
        "est",
        "ins",
        "insider",
        "news",
        "analyst",
        "warnings",
        "supplier",
        "customer",
    ]

    def __init__(self, ticker: str, start: str, interval: str, stock: DataFrame):
        """Constructor

        Parameters
        ----------
        stock : DataFrame
            Due diligence stock dataframe
        ticker : str
            Due diligence ticker symbol
        start : str
            Start date of the stock data
        interval : str
            Stock data interval
        """
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.stock = stock

        self.dd_parser = argparse.ArgumentParser(add_help=False, prog="dd")
        self.dd_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/stocks/due_diligence"
        )
        intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]

        if self.start:
            print(
                f"\n{intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
            )
        else:
            print(f"\n{intraday} Stock: {self.ticker}")

        print("\nDue Diligence:")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("   news          latest news of the company [News API]")
        print("   red           gets due diligence from another user's post [Reddit]")
        print("   analyst       analyst prices and ratings of the company [Finviz]")
        print(
            "   rating        rating of the company from strong sell to strong buy [FMP]"
        )
        print("   pt            price targets over time [Business Insider]")
        print(
            "   rot           rating over timefrom strong sell to strong buy [Finnhub]"
        )
        print(
            "   est           quarter and year analysts earnings estimates [Business Insider]"
        )
        print("   ins           insider activity over time [Business Insider]")
        print("   insider       insider trading of the company [Finviz]")
        print("   sec           SEC filings [Market Watch]")
        print(
            "   warnings      company warnings according to Sean Seah book [Market Watch]"
        )
        print("   supplier      list of suppliers [csimarket]")
        print("   customer      list of customers [csimarket]")
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

        (known_args, other_args) = self.dd_parser.parse_known_args(an_input.split())

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

    def call_red(self, other_args: List[str]):
        """Process red command"""
        r_view.due_diligence(other_args, self.ticker)

    def call_insider(self, other_args: List[str]):
        """Process insider command"""
        fvz_view.insider(other_args, self.ticker)

    def call_analyst(self, other_args: List[str]):
        """Process analyst command"""
        fvz_view.analyst(other_args, self.ticker)

    def call_pt(self, other_args: List[str]):
        """Process pt command"""
        bi_view.price_target_from_analysts(
            other_args, self.stock, self.ticker, self.start, self.interval
        )

    def call_rot(self, other_args: List[str]):
        """Process rot command"""
        finnhub_view.rating_over_time(other_args, self.ticker)

    def call_est(self, other_args: List[str]):
        """Process est command"""
        bi_view.estimates(other_args, self.ticker)

    def call_ins(self, other_args: List[str]):
        """Process ins command"""
        bi_view.insider_activity(
            other_args, self.stock, self.ticker, self.start, self.interval
        )

    def call_rating(self, other_args: List[str]):
        """Process rating command"""
        fmp_view.rating(other_args, self.ticker)

    def call_warnings(self, other_args: List[str]):
        """Process rating command"""
        mw_view.sean_seah_warnings(other_args, self.ticker)

    def call_sec(self, other_args: List[str]):
        """Process sec command"""
        mw_view.sec_fillings(other_args, self.ticker)

    def call_supplier(self, other_args: List[str]):
        """Process supplier command"""
        csimarket_view.suppliers(self.ticker, other_args)

    def call_customer(self, other_args: List[str]):
        """Process customer command"""
        csimarket_view.customers(self.ticker, other_args)


def menu(ticker: str, start: str, interval: str, stock: DataFrame):
    """Due Diligence Menu

    Parameters
    ----------
    stock : DataFrame
        Due diligence stock dataframe
    ticker : str
        Due diligence ticker symbol
    start : str
        Start date of the stock data
    interval : str
        Stock data interval
    """

    dd_controller = DueDiligenceController(ticker, start, interval, stock)
    dd_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in dd_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (stocks)>(dd)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)>(dd)> ")

        try:
            process_input = dd_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
