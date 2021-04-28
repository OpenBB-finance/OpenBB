import argparse
from typing import List
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.prediction_techniques import (
    arima,
    ets,
    knn,
    neural_networks,
    regression,
    sma,
)


class PredictionTechniquesController:
    """Prediction Techniques Controller class"""

    # Command choices
    CHOICES = [
        "help",
        "q",
        "quit",
        "sma",
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
    ]

    if gtff.ENABLE_FBPROPHET:
        CHOICES.append("prophet")

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
        self.pred_parser = argparse.ArgumentParser(add_help=False, prog="pred")
        self.pred_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""

        s_intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]

        if self.start:
            print(
                f"\n{s_intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
            )
        else:
            print(f"\n{s_intraday} Stock: {self.ticker}")

        print("\nPrediction Techniques:")
        print("   help        show this prediction techniques menu again")
        print("   q           quit this menu, and shows back to main menu")
        print("   quit        quit to abandon program")
        print("")
        print("   sma         simple moving average")
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
        if gtff.ENABLE_FBPROPHET:
            print("   prophet     Facebook's prophet prediction")
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
        (known_args, other_args) = self.pred_parser.parse_known_args(an_input.split())

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

    def call_sma(self, other_args: List[str]):
        """Process sma command"""
        sma.simple_moving_average(other_args, self.ticker, self.stock)

    def call_ets(self, other_args: List[str]):
        """Process ets command"""
        ets.exponential_smoothing(other_args, self.ticker, self.stock)

    def call_knn(self, other_args: List[str]):
        """Process knn command"""
        knn.k_nearest_neighbors(other_args, self.ticker, self.stock)

    def call_linear(self, other_args: List[str]):
        """Process linear command"""
        regression.regression(other_args, self.ticker, self.stock, regression.LINEAR)

    def call_quadratic(self, other_args: List[str]):
        """Process quadratic command"""
        regression.regression(other_args, self.ticker, self.stock, regression.QUADRATIC)

    def call_cubic(self, other_args: List[str]):
        """Process cubic command"""
        regression.regression(other_args, self.ticker, self.stock, regression.CUBIC)

    def call_regression(self, other_args: List[str]):
        """Process regression command"""
        regression.regression(
            other_args, self.ticker, self.stock, regression.USER_INPUT
        )

    def call_arima(self, other_args: List[str]):
        """Process arima command"""
        arima.arima(other_args, self.ticker, self.stock)

    def call_mlp(self, other_args: List[str]):
        """Process mlp command"""
        neural_networks.mlp(other_args, self.ticker, self.stock)

    def call_rnn(self, other_args: List[str]):
        """Process rnn command"""
        neural_networks.rnn(other_args, self.ticker, self.stock)

    def call_lstm(self, other_args: List[str]):
        """Process lstm command"""
        neural_networks.lstm(other_args, self.ticker, self.stock)

    if gtff.ENABLE_FBPROPHET:

        def call_prophet(self, other_args: List[str]):
            """Process prophet command"""
            # pylint: disable=import-outside-toplevel
            from gamestonk_terminal.prediction_techniques import fbprophet

            fbprophet.fbprophet(other_args, self.ticker, self.stock)


def menu(stock: pd.DataFrame, ticker: str, start: datetime, interval: str):
    """Comparison Analysis Menu"""

    pred_controller = PredictionTechniquesController(stock, ticker, start, interval)
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
