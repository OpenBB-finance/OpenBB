"""Residuals Controller Module"""
__docformat__ = "numpy"

import argparse
import os
from typing import List
from datetime import datetime
import pandas as pd
from matplotlib import pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.residuals_analysis import residuals_api
from gamestonk_terminal.residuals_analysis import residuals_model
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session


class ResidualsController:
    """Residuals Controller class"""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "pick",
        "fit",
        "res",
        "acf",
        "qqplot",
        "hist",
        "normality",
        "goodness",
        "arch",
        "unitroot",
        "independence",
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
        self.stock = stock["Adj Close"]

        self.model_name: str = "None"
        self.model: pd.Series = None
        self.residuals: List[float] = list()

        self.ra_parser = argparse.ArgumentParser(add_help=False, prog="ra")
        self.ra_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/residuals_analysis"
        )
        s_intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]

        if self.start:
            print(
                f"\n{s_intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
            )
        else:
            print(f"\n{s_intraday} Stock: {self.ticker}")

        print(f"\nModel fit: {self.model_name}")

        print("\nResiduals Analysis:")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("   pick          pick one of the model fitting.")
        print("                 Supports: naive, arima")
        print("")
        if self.model_name != "None":
            print("   fit           show model fit against stock")
            print("   res           show residuals")
            print("   hist          histogram and density plot")
            print("   qqplot        residuals against standard normal curve")
            print("   acf           (partial) auto-correlation function")
            print("   normality     normality test (Kurtosis,Skewness,...)")
            print("   goodness      goodness of fit test (Kolmogorov-Smirnov)")
            print("   arch          autoregressive conditional heteroscedasticity")
            print("   unitroot      unit root test / stationarity (ADF, KPSS)")
            print(
                "   independence  tests independent and identically distributed (BDS)"
            )
            print("")
        return

    def pick_model(self, other_args: List[str]):
        """Pick model to fit to stock data"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="pick",
            description="""Pick model to fit to stock data.""",
        )
        parser.add_argument(
            "-h",
            "--help",
            action="store_true",
            dest="help",
            help="show this help message",
        )
        parser.add_argument(
            "-m",
            "--model",
            dest="model",
            type=str,
            choices=["naive", "arima"],
            help="Model to fit",
        )

        try:
            # For the case where a user uses: 'pick naive'
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-m")

            (ns_parser, _) = parser.parse_known_args(other_args)

            if ns_parser.help:
                parser.print_help()
                print("")
                return

            if not ns_parser:
                return

            if ns_parser.model == "naive":
                self.model_name, self.model, self.residuals = residuals_model.naive(
                    other_args[2:], self.stock
                )

            elif ns_parser.model == "arima":
                self.model_name, self.model, self.residuals = residuals_model.arima(
                    other_args[2:], self.stock
                )

            self.print_help()

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

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.ra_parser.parse_known_args(an_input.split())

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

    def call_pick(self, other_args: List[str]):
        """Process pick command"""
        self.pick_model(other_args)

    def call_fit(self, other_args: List[str]):
        """Process fit command"""
        residuals_api.fit(
            other_args, self.ticker, self.stock, self.model_name, self.model
        )

    def call_res(self, other_args: List[str]):
        """Process res command"""
        residuals_api.res(
            other_args, self.ticker, self.stock, self.model_name, self.residuals
        )

    def call_hist(self, other_args: List[str]):
        """Process hist command"""
        residuals_api.hist(other_args, self.ticker, self.model_name, self.residuals)

    def call_qqplot(self, other_args: List[str]):
        """Process qqplot command"""
        residuals_api.plot_qqplot(
            other_args, self.ticker, self.model_name, self.residuals
        )

    def call_acf(self, other_args: List[str]):
        """Process acf command"""
        residuals_api.acf(other_args, self.ticker, self.model_name, self.residuals)

    def call_normality(self, other_args: List[str]):
        """Process normality command"""
        residuals_api.normality(other_args, self.residuals)

    def call_goodness(self, other_args: List[str]):
        """Process goodness command"""
        residuals_api.goodness(other_args, self.residuals)

    def call_arch(self, other_args: List[str]):
        """Process arch command"""
        residuals_api.arch(other_args, self.residuals)

    def call_unitroot(self, other_args: List[str]):
        """Process unit root command"""
        residuals_api.unitroot(other_args, self.residuals)

    def call_independence(self, other_args: List[str]):
        """Process independence command"""
        residuals_api.independence(other_args, self.residuals)


def menu(ticker: str, start: datetime, interval: str, stock: pd.DataFrame):
    """Residuals Menu"""

    ra_controller = ResidualsController(ticker, start, interval, stock)
    ra_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in ra_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (ra)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (ra)> ")

        try:
            plt.close("all")

            process_input = ra_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
