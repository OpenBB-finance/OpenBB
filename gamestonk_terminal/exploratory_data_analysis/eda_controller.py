"""Exploratory Data Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime
import pandas as pd
from matplotlib import pyplot as plt
from gamestonk_terminal.exploratory_data_analysis import eda_api
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import get_flair, parse_known_args_and_warn
from gamestonk_terminal.menu import session
from prompt_toolkit.completion import NestedCompleter


class EdaController:
    """EDA Controller class"""

    # Command choices
    CHOICES = [
        "help",
        "q",
        "quit",
        "summary",
        "hist",
        "cdf",
        "bwy",
        "bwm",
        "rolling",
        "decompose",
        "cusum",
    ]

    def __init__(
        self,
        stock: pd.DataFrame,
        ticker: str,
        start: datetime,
        interval: str,
    ):
        """Constructor"""
        self.stock = stock
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.stats_parser = argparse.ArgumentParser(add_help=False, prog="stats")
        self.stats_parser.add_argument(
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

        print("\nExploratory Data Analysis:")
        print("   help          show this comparison analysis menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("   summary       brief summary statistics")
        print("   hist          histogram with density plot")
        print("   cdf           cumulative distribution function")
        print("   bwy           box and whisker yearly plot")
        print("   bwm           box and whisker monthly plot")
        print("   rolling       rolling mean and std deviation")
        print("   decompose     decomposition in cyclic-trend, season, and residuals")
        print("   cusum         detects abrupt changes using cumulative sum algorithm")
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
        (known_args, other_args) = self.stats_parser.parse_known_args(an_input.split())

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

    def call_summary(self, other_args: List[str]):
        """Process summary command"""
        eda_api.summary(other_args, self.stock)

    def call_hist(self, other_args: List[str]):
        """Process hist command"""
        eda_api.hist(other_args, self.ticker, self.stock)

    def call_cdf(self, other_args: List[str]):
        """Process cdf command"""
        eda_api.cdf(other_args, self.ticker, self.stock)

    def call_bwy(self, other_args: List[str]):
        """Process bwy command"""
        eda_api.bwy(other_args, self.ticker, self.stock)

    def call_bwm(self, other_args: List[str]):
        """Process bwm command"""
        eda_api.bwm(other_args, self.ticker, self.stock)

    def call_rolling(self, other_args: List[str]):
        """Process rolling command"""
        eda_api.rolling(other_args, self.ticker, self.stock)

    def call_decompose(self, other_args: List[str]):
        """Process decompose command"""
        eda_api.decompose(other_args, self.ticker, self.stock)

    def call_cusum(self, other_args: List[str]):
        """Process cusum command"""
        eda_api.cusum(other_args, self.ticker, self.stock)


def menu(stock: pd.DataFrame, ticker: str, start: datetime, interval: str):
    """Statistics Menu"""

    eda_controller = EdaController(stock, ticker, start, interval)
    eda_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in eda_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (eda)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (eda)> ")

        try:
            plt.close("all")

            process_input = eda_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
