""" Fundamental Analysis Controller """
__docformat__ = "numpy"

import argparse
import os
from typing import List
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.fundamental_analysis.alpha_vantage import av_controller
from gamestonk_terminal.fundamental_analysis import business_insider_view
from gamestonk_terminal.fundamental_analysis.financial_modeling_prep import (
    fmp_controller,
    fmp_view,
)
from gamestonk_terminal.fundamental_analysis import finviz_view
from gamestonk_terminal.fundamental_analysis import market_watch_view
from gamestonk_terminal.fundamental_analysis import yahoo_finance_view
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair, parse_known_args_and_warn
from gamestonk_terminal.menu import session

# pylint: disable=inconsistent-return-statements


class FundamentalAnalysisController:
    """Fundamental Analysis Controller"""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "score",
        "screener",
        "income",
        "balance",
        "cash",
        "mgmt",
        "info",
        "shrs",
        "sust",
        "cal",
        "av",
        "fmp",
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

        self.fa_parser = argparse.ArgumentParser(add_help=False, prog="fa")
        self.fa_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/fundamental_analysis"
        )
        intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]

        if self.start:
            print(
                f"\n{intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
            )
        else:
            print(f"\n{intraday} Stock: {self.ticker}")

        print("\nFundamental Analysis:")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("   screener      screen info about the company [Finviz]")
        print("   mgmt          management team of the company [Business Insider]")
        print(
            "   score         investing score from Warren Buffett, Joseph Piotroski and Benjamin Graham [FMP]"
        )
        print("")
        print("Market Watch API")
        print("   income        income statement of the company")
        print("   balance       balance sheet of the company")
        print("   cash          cash flow statement of the company")
        print("")
        print("Yahoo Finance API")
        print("   info          information scope of the company")
        print("   shrs          shareholders of the company")
        print("   sust          sustainability values of the company")
        print("   cal           calendar earnings and estimates of the company")
        print("")
        print("Other Sources:")
        print(">  av            Alpha Vantage MENU")
        print(">  fmp           Financial Modeling Prep MENU")
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

        (known_args, other_args) = self.fa_parser.parse_known_args(an_input.split())

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

    def call_mgmt(self, other_args: List[str]):
        """Process mgmt command"""
        business_insider_view.management(other_args, self.ticker)

    def call_screener(self, other_args: List[str]):
        """Process screener command"""
        finviz_view.screener(other_args, self.ticker)

    def call_score(self, other_args: List[str]):
        """Process score command"""
        fmp_view.valinvest_score(other_args, self.ticker)

    def call_income(self, other_args: List[str]):
        """Process income command"""
        market_watch_view.income(other_args, self.ticker)

    def call_balance(self, other_args: List[str]):
        """Process balance command"""
        market_watch_view.balance(other_args, self.ticker)

    def call_cash(self, other_args: List[str]):
        """Process cash command"""
        market_watch_view.cash(other_args, self.ticker)

    def call_info(self, other_args: List[str]):
        """Process info command"""
        yahoo_finance_view.info(other_args, self.ticker)

    def call_shrs(self, other_args: List[str]):
        """Process shrs command"""
        yahoo_finance_view.shareholders(other_args, self.ticker)

    def call_sust(self, other_args: List[str]):
        """Process sust command"""
        yahoo_finance_view.sustainability(other_args, self.ticker)

    def call_cal(self, other_args: List[str]):
        """Process cal command"""
        yahoo_finance_view.calendar_earnings(other_args, self.ticker)

    def call_av(self, _):
        """Process av command"""
        ret = av_controller.menu(self.ticker, self.start, self.interval)

        if ret is False:
            self.print_help()
        else:
            return True

    def call_fmp(self, _):
        """Process fmp command"""
        ret = fmp_controller.menu(self.ticker, self.start, self.interval)

        if ret is False:
            self.print_help()
        else:
            return True


def key_metrics_explained(other_args: List[str]):
    """Key metrics explained

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="info",
        description="""
            Provides information about main key metrics. Namely: EBITDA,
            EPS, P/E, PEG, FCF, P/B, ROE, DPR, P/S, Dividend Yield Ratio, D/E, and Beta.
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        filepath = "fundamental_analysis/key_metrics_explained.txt"
        with open(filepath) as fp:
            line = fp.readline()
            while line:
                print(f"{line.strip()}")
                line = fp.readline()
            print("")

    except Exception as e:
        print(e, "ERROR!\n")


def menu(ticker: str, start: str, interval: str):
    """Fundamental Analysis menu

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    start : str
        Start date of the stock data
    interval : str
        Stock data interval
    """
    fa_controller = FundamentalAnalysisController(ticker, start, interval)
    fa_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in fa_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (fa)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (fa)> ")

        try:
            process_input = fa_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
