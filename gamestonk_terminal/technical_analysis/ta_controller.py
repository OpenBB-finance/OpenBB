"""Technical Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
import os
from typing import List
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.technical_analysis import momentum as ta_momentum
from gamestonk_terminal.technical_analysis import overlap as ta_overlap
from gamestonk_terminal.technical_analysis import trend_indicators as ta_trend
from gamestonk_terminal.technical_analysis import volatility as ta_volatility
from gamestonk_terminal.technical_analysis import volume as ta_volume
from gamestonk_terminal.technical_analysis import finbrain_view
from gamestonk_terminal.technical_analysis import tradingview_view
from gamestonk_terminal.technical_analysis import finviz_view
from gamestonk_terminal.technical_analysis import finnhub_view


class TechnicalAnalysisController:
    """Technical Analysis Controller class"""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "view",
        "summary",
        "recom",
        "pr",
        "ema",
        "sma",
        "vwap",
        "cci",
        "macd",
        "rsi",
        "stoch",
        "adx",
        "aroon",
        "bbands",
        "ad",
        "obv",
    ]

    def __init__(
        self,
        ticker: str,
        start: datetime,
        interval: str,
        stock: pd.DataFrame,
    ):
        """Constructor"""
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.stock = stock

        self.ta_parser = argparse.ArgumentParser(add_help=False, prog="ta")
        self.ta_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/technical_analysis"
        )
        s_intraday = (f"Intraday {self.interval }", "Daily")[self.interval == "1440min"]

        if self.start:
            print(
                f"\n{s_intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
            )
        else:
            print(f"\n{s_intraday} Stock: {self.ticker}")

        print("\nTechnical Analysis:")  # https://github.com/twopirllc/pandas-ta
        print("   cls         clear screen")
        print("   ?/help      show this menu again")
        print("   q           quit this menu, and shows back to main menu")
        print("   quit        quit to abandon program")
        print("")
        print("   view        view historical data and trendlines [Finviz]")
        print("   summary     technical summary report [FinBrain API]")
        print(
            "   recom       recommendation based on Technical Indicators [Tradingview API]"
        )
        print("   pr          pattern recognition [Finnhub]")
        print("")
        print("overlap:")
        print("   ema         exponential moving average")
        print("   sma         simple moving average")
        print("   vwap        volume weighted average price")
        print("momentum:")
        print("   cci         commodity channel index")
        print("   macd        moving average convergence/divergence")
        print("   rsi         relative strength index")
        print("   stoch       stochastic oscillator")
        print("trend:")
        print("   adx         average directional movement index")
        print("   aroon       aroon indicator")
        print("volatility:")
        print("   bbands      bollinger bands")
        print("volume:")
        print("   ad          chaikin accumulation/distribution line values")
        print("   obv         on balance volume")
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

        (known_args, other_args) = self.ta_parser.parse_known_args(an_input.split())

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

    def call_view(self, other_args: List[str]):
        """Process view command"""
        finviz_view.view(other_args, self.ticker)

    def call_summary(self, other_args: List[str]):
        """Process summary command"""
        finbrain_view.technical_summary_report(other_args, self.ticker)

    def call_recom(self, other_args: List[str]):
        """Process recom command"""
        tradingview_view.print_recommendation(other_args, self.ticker)

    def call_pr(self, other_args: List[str]):
        """Process pr command"""
        finnhub_view.pattern_recognition_view(other_args, self.ticker)

    # OVERLAP
    def call_ema(self, other_args: List[str]):
        """Process ema command"""
        ta_overlap.ema(other_args, self.ticker, self.interval, self.stock)

    def call_sma(self, other_args: List[str]):
        """Process sma command"""
        ta_overlap.sma(other_args, self.ticker, self.interval, self.stock)

    def call_vwap(self, other_args: List[str]):
        """Process vwap command"""
        ta_overlap.vwap(other_args, self.ticker, self.interval, self.stock)

    # MOMENTUM
    def call_cci(self, other_args: List[str]):
        """Process cci command"""
        ta_momentum.cci(other_args, self.ticker, self.interval, self.stock)

    def call_macd(self, other_args: List[str]):
        """Process macd command"""
        ta_momentum.macd(other_args, self.ticker, self.interval, self.stock)

    def call_rsi(self, other_args: List[str]):
        """Process rsi command"""
        ta_momentum.rsi(other_args, self.ticker, self.interval, self.stock)

    def call_stoch(self, other_args: List[str]):
        """Process stoch command"""
        ta_momentum.stoch(other_args, self.ticker, self.interval, self.stock)

    # TREND
    def call_adx(self, other_args: List[str]):
        """Process adx command"""
        ta_trend.adx(other_args, self.ticker, self.interval, self.stock)

    def call_aroon(self, other_args: List[str]):
        """Process aroon command"""
        ta_trend.aroon(other_args, self.ticker, self.interval, self.stock)

    # VOLATILITY
    def call_bbands(self, other_args: List[str]):
        """Process bbands command"""
        ta_volatility.bbands(other_args, self.ticker, self.interval, self.stock)

    # VOLUME
    def call_ad(self, other_args: List[str]):
        """Process ad command"""
        ta_volume.ad(other_args, self.ticker, self.interval, self.stock)

    def call_obv(self, other_args: List[str]):
        """Process obv command"""
        ta_volume.obv(other_args, self.ticker, self.interval, self.stock)


def menu(
    ticker: str, start: datetime, interval: str, stock: pd.DataFrame, context: str = ""
):
    """Technical Analysis Menu"""

    ta_controller = TechnicalAnalysisController(ticker, start, interval, stock)
    ta_controller.call_help(None)

    if context:
        context = f"{context}>"

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in ta_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} {context}(ta)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} {context}(ta)> ")

        try:
            plt.close("all")

            process_input = ta_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
