""" Due Diligence Controller """
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
from gamestonk_terminal.prediction_techniques import (
    arima_view,
    ets_view,
    knn_view,
    neural_networks_view,
    regression_view,
)


class PredictionTechniquesController:
    """Prediction Techniques Controller class"""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "ets",
        "knn",
        "linear",
        "quadratic",
        "cubic",
        "regression",
        "arima",
        "mlp",
        "rnn",
        "lstm",
        "conv1d",
    ]

    def __init__(
        self,
        ticker: str,
        start: datetime,
        interval: str,
        stock: pd.DataFrame,
    ):
        """Constructor"""
        self.stock = stock
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.pred_parser = argparse.ArgumentParser(add_help=False, prog="pred")
        self.pred_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/prediction_techniques"
        )
        s_intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]

        if self.start:
            print(
                f"\n{s_intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
            )
        else:
            print(f"\n{s_intraday} Stock: {self.ticker}")

        print("\nPrediction Techniques:")
        print("   cls         clear screen")
        print("   ?/help      show this menu again")
        print("   q           quit this menu, and shows back to main menu")
        print("   quit        quit to abandon program")
        print("")
        print("   ets         exponential smoothing (e.g. Holt-Winters)")
        print("   knn         k-Nearest Neighbors")
        print("   linear      linear regression (polynomial 1)")
        print("   quadratic   quadratic regression (polynomial 2)")
        print("   cubic       cubic regression (polynomial 3)")
        print("   regression  regression (other polynomial)")
        print("   arima       autoregressive integrated moving average")
        print("   mlp         MultiLayer Perceptron")
        print("   rnn         Recurrent Neural Network")
        print("   lstm        Long-Short Term Memory")
        print("   conv1d      1D Convolutional Neural Network")
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

        (known_args, other_args) = self.pred_parser.parse_known_args(an_input.split())

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

    def call_ets(self, other_args: List[str]):
        """Process ets command"""
        ets_view.exponential_smoothing(other_args, self.ticker, self.stock)

    def call_knn(self, other_args: List[str]):
        """Process knn command"""
        knn_view.k_nearest_neighbors(other_args, self.ticker, self.stock)

    def call_linear(self, other_args: List[str]):
        """Process linear command"""
        regression_view.regression(
            other_args, self.ticker, self.stock, regression_view.LINEAR
        )

    def call_quadratic(self, other_args: List[str]):
        """Process quadratic command"""
        regression_view.regression(
            other_args, self.ticker, self.stock, regression_view.QUADRATIC
        )

    def call_cubic(self, other_args: List[str]):
        """Process cubic command"""
        regression_view.regression(
            other_args, self.ticker, self.stock, regression_view.CUBIC
        )

    def call_regression(self, other_args: List[str]):
        """Process regression command"""
        regression_view.regression(
            other_args, self.ticker, self.stock, regression_view.USER_INPUT
        )

    def call_arima(self, other_args: List[str]):
        """Process arima command"""
        arima_view.arima(other_args, self.ticker, self.stock)

    def call_mlp(self, other_args: List[str]):
        """Process mlp command"""
        neural_networks_view.mlp(other_args, self.ticker, self.stock)

    def call_rnn(self, other_args: List[str]):
        """Process rnn command"""
        neural_networks_view.rnn(other_args, self.ticker, self.stock)

    def call_lstm(self, other_args: List[str]):
        """Process lstm command"""
        neural_networks_view.lstm(other_args, self.ticker, self.stock)

    def call_conv1d(self, other_args: List[str]):
        """Process conv1d command"""
        neural_networks_view.conv1d(other_args, self.ticker, self.stock)


def menu(ticker: str, start: datetime, interval: str, stock: pd.DataFrame):
    """Prediction Techniques Menu"""

    pred_controller = PredictionTechniquesController(ticker, start, interval, stock)
    pred_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in pred_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (pred)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (pred)> ")

        try:
            plt.close("all")

            process_input = pred_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
