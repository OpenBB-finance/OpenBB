"""Comparison Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
import os
import random
from typing import List
from datetime import datetime
import requests
import pandas as pd
from matplotlib import pyplot as plt
from finvizfinance.screener.overview import Overview
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import get_flair, parse_known_args_and_warn
from gamestonk_terminal.comparison_analysis import yahoo_finance_view
from gamestonk_terminal.comparison_analysis import market_watch_view
from gamestonk_terminal.comparison_analysis import finbrain_view
from gamestonk_terminal.comparison_analysis import finviz_compare_view
from gamestonk_terminal.portfolio_optimization import po_controller
from gamestonk_terminal.menu import session


class ComparisonAnalysisController:
    """Comparison Analysis Controller class"""

    # Command choices
    CHOICES = [
        "?",
        "cls",
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
        "overview",
        "valuation",
        "financial",
        "ownership",
        "performance",
        "technical",
        "po",
    ]

    def __init__(
        self,
        ticker: str,
        start: datetime,
        interval: str,
        stock: pd.DataFrame,
    ):
        """Constructor

        Parameters
        ----------
        ticker : str
            Stock ticker
        start : datetime
            Start time
        interval : str
            Time interval
        stock : pd.DataFrame
            Stock data
        """
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.stock = stock

        self.similar: List[str] = []
        self.user = ""

        self.ca_parser = argparse.ArgumentParser(add_help=False, prog="ca")
        self.ca_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/comparison_analysis"
        )

        s_intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]

        if self.start:
            print(
                f"\n{s_intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
            )
        else:
            print(f"\n{s_intraday} Stock: {self.ticker}")

        if self.similar:
            print(f"[{self.user}] Similar Companies: {', '.join(self.similar)}")

        print("\nComparison Analysis Mode:")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("   get           get similar companies")
        print("   select        select similar companies")
        print("")
        print("   historical    historical price data comparison")
        print("   hcorr         historical price correlation")
        print("   income        income financials comparison")
        print("   balance       balance financials comparison")
        print("   cashflow      cashflow comparison")
        print("   sentiment     sentiment analysis comparison")
        print("   scorr         sentiment correlation")
        print("")
        print("   overview      brief overview comparison")
        print("   valuation     brief valuation comparison")
        print("   financial     brief financial comparison")
        print("   ownership     brief ownership comparison")
        print("   performance   brief performance comparison")
        print("   technical     brief technical comparison")
        print("")

        if self.similar:
            print(">  po          portfolio optimization for selected tickers")
            print("")
        return

    def get_similar_companies(self, other_args: List[str]):
        """Get similar companies. [Source: Polygon API]

        Parameters
        ----------
        other_args : List[str]
            argparse other args
        """
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="get",
            description="""Get similar companies to compare with.""",
        )
        parser.add_argument(
            "-s",
            "--source",
            action="store",
            default="finviz",
            dest="source",
            choices=["polygon", "finnhub", "finviz"],
            help="source that provides similar companies",
        )

        # If source is finviz the user may want to get
        # similar companies based on Industry and Sector only, and not
        # on the fact that they are based on the same country
        if "finviz" in other_args or not other_args:
            parser.add_argument(
                "--nocountry",
                action="store_true",
                default=False,
                dest="b_no_country",
                help="Similar stocks from finviz using only Industry and Sector.",
            )

        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-s")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            if ns_parser.source == "polygon":
                result = requests.get(
                    f"https://api.polygon.io/v1/meta/symbols/{self.ticker.upper()}/company?&apiKey={cfg.API_POLYGON_KEY}"
                )

                if result.status_code == 200:
                    self.similar = result.json()["similar"]
                    self.user = "Polygon"
                else:
                    print(result.json()["error"])

            elif ns_parser.source == "finnhub":
                result = requests.get(
                    f"https://finnhub.io/api/v1/stock/peers?symbol={self.ticker}&token={cfg.API_FINNHUB_KEY}"
                )

                if result.status_code == 200:
                    d_peers = result.json()

                    if d_peers:
                        self.similar = d_peers
                        self.user = "Finnhub"
                    else:
                        print("Similar companies not found.")

            else:
                if ns_parser.b_no_country:
                    compare_list = ["Sector", "Industry"]
                else:
                    compare_list = ["Sector", "Industry", "Country"]

                self.similar = (
                    Overview()
                    .compare(self.ticker, compare_list, verbose=0)["Ticker"]
                    .to_list()
                )
                self.user = "Finviz"

            if self.ticker.upper() in self.similar:
                self.similar.remove(self.ticker.upper())

            if len(self.similar) > 10:
                random.shuffle(self.similar)
                self.similar = sorted(self.similar[:10])
                print(
                    "The limit of stocks to compare with are 10. Hence, 10 random similar stocks will be displayed.\n",
                )

            if self.similar:
                print(f"[{self.user}] Similar Companies: {', '.join(self.similar)}")
            print("")

        except Exception as e:
            print(e, "\n")

    def select_similar_companies(self, other_args: List[str]):
        """Select similar companies, e.g. NIO,XPEV,LI

        Parameters
        ----------
        other_args : List[str]
            argparse other args
        """
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
            self.user = "User"
            print("")

        except Exception as e:
            print(e, "\n")

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

        (known_args, other_args) = self.ca_parser.parse_known_args(an_input.split())

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

    def call_get(self, other_args: List[str]):
        """Process get command"""
        self.get_similar_companies(other_args)

    def call_select(self, other_args: List[str]):
        """Process select command"""
        self.select_similar_companies(other_args)

    def call_historical(self, other_args: List[str]):
        """Process historical command"""
        yahoo_finance_view.historical(
            other_args, self.stock, self.ticker, self.start, self.interval, self.similar
        )

    def call_hcorr(self, other_args: List[str]):
        """Process historical correlation command"""
        yahoo_finance_view.correlation(
            other_args, self.stock, self.ticker, self.start, self.interval, self.similar
        )

    def call_income(self, other_args: List[str]):
        """Process income command"""
        market_watch_view.compare_income(other_args, self.ticker, self.similar)

    def call_balance(self, other_args: List[str]):
        """Process balance command"""
        market_watch_view.compare_balance(other_args, self.ticker, self.similar)

    def call_cashflow(self, other_args: List[str]):
        """Process cashflow command"""
        market_watch_view.compare_cashflow(other_args, self.ticker, self.similar)

    def call_sentiment(self, other_args: List[str]):
        """Process sentiment command"""
        finbrain_view.sentiment_compare(other_args, self.ticker, self.similar)

    def call_scorr(self, other_args: List[str]):
        """Process sentiment correlation command"""
        finbrain_view.sentiment_correlation(other_args, self.ticker, self.similar)

    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        finviz_compare_view.screener(other_args, "overview", self.ticker, self.similar)

    def call_valuation(self, other_args: List[str]):
        """Process valuation command"""
        finviz_compare_view.screener(other_args, "valuation", self.ticker, self.similar)

    def call_financial(self, other_args: List[str]):
        """Process financial command"""
        finviz_compare_view.screener(other_args, "financial", self.ticker, self.similar)

    def call_ownership(self, other_args: List[str]):
        """Process ownership command"""
        finviz_compare_view.screener(other_args, "ownership", self.ticker, self.similar)

    def call_performance(self, other_args: List[str]):
        """Process performance command"""
        finviz_compare_view.screener(
            other_args, "performance", self.ticker, self.similar
        )

    def call_technical(self, other_args: List[str]):
        """Process technical command"""
        finviz_compare_view.screener(other_args, "technical", self.ticker, self.similar)

    def call_po(self, _):
        """Call the portfolio optimization menu with selected tickers"""
        return po_controller.menu([self.ticker] + self.similar)


def menu(ticker: str, start: datetime, interval: str, stock: pd.DataFrame):
    """Comparison Analysis Menu

    Parameters
    ----------
    ticker : str
        Stock ticker
    start : datetime
        Time start
    interval : str
        Time interval
    stock : pd.DataFrame
        Stock data
    """

    ca_controller = ComparisonAnalysisController(ticker, start, interval, stock)
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
