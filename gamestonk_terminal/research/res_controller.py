"""Research Controller Module"""
__docformat__ = "numpy"

import argparse
import os
import webbrowser
from datetime import datetime
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session


class ResearchController:
    """Research Controller class"""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "macroaxis",
        "yahoo",
        "finviz",
        "marketwatch",
        "fool",
        "businessinsider",
        "fmp",
        "fidelity",
        "tradingview",
        "marketchameleon",
        "stockrow",
        "barchart",
        "grufity",
        "fintel",
        "zacks",
        "macrotrends",
        "newsfilter",
        "stockanalysis",
    ]

    def __init__(self, ticker: str, start: datetime, interval: str):
        """Constructor"""
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.res_parser = argparse.ArgumentParser(add_help=False, prog="res")
        self.res_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/research"
        )
        s_intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]

        if self.start:
            print(
                f"\n{s_intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
            )
        else:
            print(f"\n{s_intraday} Stock: {self.ticker}")

        print("\nResearch:")
        print("   cls               clear screen")
        print("   ?/help            show this menu again")
        print("   q                 quit this menu, and shows back to main menu")
        print("   quit              quit to abandon program")
        print("")
        print("   macroaxis         www.macroaxis.com")
        print("   yahoo             www.finance.yahoo.com")
        print("   finviz            www.finviz.com")
        print("   marketwatch       www.marketwatch.com")
        print("   fool              www.fool.com")
        print("   businessinsider   www.markets.businessinsider.com")
        print("   fmp               www.financialmodelingprep.com")
        print("   fidelity          www.eresearch.fidelity.com")
        print("   tradingview       www.tradingview.com")
        print("   marketchameleon   www.marketchameleon.com")
        print("   stockrow          www.stockrow.com")
        print("   barchart          www.barchart.com")
        print("   grufity           www.grufity.com")
        print("   fintel            www.fintel.com")
        print("   zacks             www.zacks.com")
        print("   macrotrends       www.macrotrends.net")
        print("   newsfilter        www.newsfilter.io")
        print("   stockanalysis     www.stockanalysis.com")

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

        (known_args, other_args) = self.res_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        if other_args:
            print(f"The following args were unexpected: {other_args}")

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(None)

    def call_help(self, _):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_macroaxis(self, _):
        """Process macroaxis command"""
        webbrowser.open(f"https://www.macroaxis.com/invest/market/{self.ticker}")

    def call_yahoo(self, _):
        """Process yahoo command"""
        webbrowser.open(f"https://finance.yahoo.com/quote/{self.ticker}")

    def call_finviz(self, _):
        """Process finviz command"""
        webbrowser.open(f"https://finviz.com/quote.ashx?t={self.ticker}")

    def call_marketwatch(self, _):
        """Process marketwatch command"""
        webbrowser.open(f"https://www.marketwatch.com/investing/stock/{self.ticker}")

    def call_fool(self, _):
        """Process fool command"""
        webbrowser.open(f"https://www.fool.com/quote/{self.ticker}")

    def call_businessinsider(self, _):
        """Process businessinsider command"""
        webbrowser.open(
            f"https://markets.businessinsider.com/stocks/{self.ticker}-stock/"
        )

    def call_fmp(self, _):
        """Process fmp command"""
        webbrowser.open(
            f"https://financialmodelingprep.com/financial-summary/{self.ticker}"
        )

    def call_fidelity(self, _):
        """Process fidelity command"""
        webbrowser.open(
            f"https://eresearch.fidelity.com/eresearch/goto/evaluate/snapshot.jhtml?symbols={self.ticker}"
        )

    def call_tradingview(self, _):
        """Process tradingview command"""
        webbrowser.open(f"https://www.tradingview.com/symbols/{self.ticker}")

    def call_marketchameleon(self, _):
        """Process marketchameleon command"""
        webbrowser.open(f"https://marketchameleon.com/Overview/{self.ticker}")

    def call_stockrow(self, _):
        """Process stockrow command"""
        webbrowser.open(f"https://stockrow.com/{self.ticker}")

    def call_barchart(self, _):
        """Process barchart command"""
        webbrowser.open(
            f"https://www.barchart.com/stocks/quotes/{self.ticker}/overview"
        )

    def call_grufity(self, _):
        """Process grufity command"""
        webbrowser.open(f"https://grufity.com/stock/{self.ticker}")

    def call_fintel(self, _):
        """Process fintel command"""
        webbrowser.open(f"https://fintel.io/s/us/{self.ticker}")

    def call_zacks(self, _):
        """Process zacks command"""
        webbrowser.open(f"https://www.zacks.com/stock/quote/{self.ticker}")

    def call_macrotrends(self, _):
        """Process macrotrends command"""
        webbrowser.open(
            f"https://www.macrotrends.net/stocks/charts/{self.ticker}/{self.ticker}/market-cap"
        )

    def call_newsfilter(self, _):
        """Process newsfilter command"""
        webbrowser.open(f"https://newsfilter.io/search?query={self.ticker}")

    def call_stockanalysis(self, _):
        """Process stockanalysis command"""
        webbrowser.open(f"https://stockanalysis.com/stocks/{self.ticker}/")


def menu(ticker: str, start: datetime, interval: str):
    """Research Menu"""

    res_controller = ResearchController(ticker, start, interval)
    res_controller.call_help(None)
    print("")

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in res_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (res)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (res)> ")

        try:
            process_input = res_controller.switch(an_input)
            print("")

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
