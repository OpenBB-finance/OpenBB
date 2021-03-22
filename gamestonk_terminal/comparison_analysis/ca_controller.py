"""Comparison Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
import requests
from typing import List
from datetime import datetime
import pandas as pd
from matplotlib import pyplot as plt
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import get_flair, parse_known_args_and_warn
from gamestonk_terminal.comparison_analysis import yahoo_finance_api as yf_api
from gamestonk_terminal.comparison_analysis import market_watch_api as mw_api
from gamestonk_terminal.comparison_analysis import finbrain_api as f_api
from gamestonk_terminal.menu import session
from prompt_toolkit.completion import NestedCompleter


class ComparisonAnalysisController:
    """Comparison Analysis Controller class"""

    # Command choices
    CHOICES = [
        "help",
        "q",
        "quit",
        "get",
        "select",
        "historical",
        "hcorr",
        "income",
        "balance",
        "cashflow",
        "sentiment",
        "scorr",
    ]

    def __init__(
        self,
        stock: pd.DataFrame,
        ticker: str,
        start: datetime,
        interval: str,
        similar: List[str],
        user: bool,
    ):
        """Constructor"""
        self.similar = similar
        self.user = user
        self.stock = stock
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.ca_parser = argparse.ArgumentParser(add_help=False, prog="ca")
        self.ca_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    @staticmethod
    def print_help(self):
        """Print help"""

        s_intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]

        if self.start:
            print(
                f"\n{s_intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
            )
        else:
            print(f"\n{s_intraday} Stock: {self.ticker}")

        s_similar_source = ("Polygon API", "User")[self.user]

        if self.similar:
            print(f"[{s_similar_source}] Similar Companies: {', '.join(self.similar)}")
        else:
            print(f"No similar companies [{s_similar_source}]")

        print("\nComparison Analysis Mode:")
        print("   help          show this comparison analysis menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("   get           get similar companies [Polygon API]")
        print("   select        select similar companies")
        print("")
        print("   historical    historical price data comparison")
        print("   hcorr         historical price correlation")
        print("")
        print("   income        income financials comparison")
        print("   balance       balance financials comparison")
        print("   cashflow      cashflow comparison")
        print("")
        print("   sentiment     sentiment analysis comparison")
        print("   scorr         sentiment correlation")
        print("")
        return

    @staticmethod
    def get_similar_companies(self, other_args: List[str]):
        """ Get similar companies. [Source: Polygon API] """
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="get",
            description="""Get similar companies to compare with.""",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            result = requests.get(
                f"https://api.polygon.io/v1/meta/symbols/{self.ticker.upper()}/company?&apiKey={cfg.API_POLYGON_KEY}"
            )

            if result.status_code == 200:
                self.similar = result.json()["similar"]
                print(f"[Polygon API] Similar Companies: {', '.join(self.similar)}")
                self.user = False
            else:
                print(result.json()["error"])

        except Exception as e:
            print(e)

        print("")
        return

    @staticmethod
    def select_similar_companies(self, other_args: List[str]):
        """ Select similar companies, e.g. NIO,XPEV,LI"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="select",
            description="""Select similar companies to compare with.""",
        )
        parser.add_argument(
            "-s",
            "--similar",
            dest="l_similar",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            help="similar companies to compare with.",
        )

        try:
            # For the case where a user uses: 'select NIO,XPEV,LI'
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-s")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            self.similar = ns_parser.l_similar
            self.user = True

        except Exception as e:
            print(e)

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
        (known_args, other_args) = self.ca_parser.parse_known_args(an_input.split())

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

    def call_get(self, other_args: List[str]):
        """Process get command"""
        self.get_similar_companies(self, other_args)

    def call_select(self, other_args: List[str]):
        """Process select command"""
        self.select_similar_companies(self, other_args)

    def call_historical(self, other_args: List[str]):
        """Process historical command"""
        yf_api.historical(
            other_args, self.stock, self.ticker, self.start, self.interval, self.similar
        )

    def call_hcorr(self, other_args: List[str]):
        """Process historical correlation command"""
        yf_api.correlation(
            other_args, self.stock, self.ticker, self.start, self.interval, self.similar
        )

    def call_income(self, other_args: List[str]):
        """Process income command"""
        mw_api.compare_income(other_args, self.ticker, self.similar)

    def call_balance(self, other_args: List[str]):
        """Process balance command"""
        mw_api.compare_balance(other_args, self.ticker, self.similar)

    def call_cashflow(self, other_args: List[str]):
        """Process cashflow command"""
        mw_api.compare_cashflow(other_args, self.ticker, self.similar)

    def call_sentiment(self, other_args: List[str]):
        """Process sentiment command"""
        f_api.sentiment_compare(other_args, self.ticker, self.similar)

    def call_scorr(self, other_args: List[str]):
        """Process sentiment correlation command"""
        f_api.sentiment_correlation(other_args, self.ticker, self.similar)


def menu(stock: pd.DataFrame, ticker: str, start: datetime, interval: str):
    """Comparison Analysis Menu"""

    ca_controller = ComparisonAnalysisController(
        stock, ticker, start, interval, [], False
    )
    ca_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in ca_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (ca)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (ca)> ")

        try:
            plt.close("all")

            process_input = ca_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
