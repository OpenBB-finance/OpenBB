""" Due Diligence Controller """
__docformat__ = "numpy"

import argparse
import os
from typing import List
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    check_positive,
    valid_date,
    get_next_stock_market_days,
    EXPORT_ONLY_FIGURES_ALLOWED,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.common.prediction_techniques import (
    arima_view,
    ets_view,
    knn_view,
    neural_networks_view,
    regression_view,
)
from gamestonk_terminal.stocks.stocks_helper import load


class PredictionTechniquesController:
    """Prediction Techniques Controller class"""

    # Command choices
    CHOICES = ["cls", "?", "help", "q", "quit", "load", "pick"]

    CHOICES_MODELS = [
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
    CHOICES += CHOICES_MODELS

    def __init__(
        self,
        ticker: str,
        start: datetime,
        interval: str,
        stock: pd.DataFrame,
    ):
        """Constructor"""
        stock["Returns"] = stock["Adj Close"].pct_change()
        stock["LogRet"] = np.log(stock["Adj Close"]) - np.log(
            stock["Adj Close"].shift(1)
        )
        stock = stock.rename(columns={"Adj Close": "AdjClose"})
        stock = stock.dropna()

        self.stock = stock
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.target = "AdjClose"
        self.pred_parser = argparse.ArgumentParser(add_help=False, prog="pred")
        self.pred_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        s_intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]
        if self.start:
            stock_info = f"{s_intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
        else:
            stock_info = "{s_intraday} Stock: {self.ticker}"

        help_string = f""">>> PREDICTION <<<

What would you like to do?
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon program
    load        load new ticker
    pick        pick new target variable

{stock_info}
Target Column: {self.target}

Models:
    ets         exponential smoothing (e.g. Holt-Winters)
    knn         k-Nearest Neighbors
    linear      linear regression (polynomial 1)
    quadratic   quadratic regression (polynomial 2)
    cubic       cubic regression (polynomial 3)
    regression  regression (other polynomial)
    arima       autoregressive integrated moving average
    mlp         MultiLayer Perceptron
    rnn         Recurrent Neural Network
    lstm        Long-Short Term Memory
    conv1d      1D Convolutional Neural Network
        """
        print(help_string)

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

    def call_load(self, other_args: List[str]):
        """Process load command"""
        self.ticker, self.start, self.interval, stock = load(
            other_args, self.ticker, self.start, self.interval, self.stock
        )
        if "." in self.ticker:
            self.ticker = self.ticker.split(".")[0]

        if "-h" not in other_args:
            stock["Returns"] = stock["Adj Close"].pct_change()
            stock["LogRet"] = np.log(stock["Adj Close"]) - np.log(
                stock["Adj Close"].shift(1)
            )
            stock = stock.rename(columns={"Adj Close": "AdjClose"})
            stock = stock.dropna()
            self.stock = stock

    def call_pick(self, other_args: List[str]):
        """Process pick command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="pick",
            description="""
                Change target variable
            """,
        )
        parser.add_argument(
            "-t",
            "--target",
            dest="target",
            choices=list(self.stock.columns),
            help="Select variable to analyze",
        )
        try:
            if other_args:
                if "-t" not in other_args and "-h" not in other_args:
                    other_args.insert(0, "-t")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            self.target = ns_parser.target
            print("")

        except Exception as e:
            print(e, "\n")

    def call_ets(self, other_args: List[str]):
        """Process ets command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ets",
            description="""
                Exponential Smoothing, see https://otexts.com/fpp2/taxonomy.html

                Trend='N',  Seasonal='N': Simple Exponential Smoothing
                Trend='N',  Seasonal='A': Exponential Smoothing
                Trend='N',  Seasonal='M': Exponential Smoothing
                Trend='A',  Seasonal='N': Holt’s linear method
                Trend='A',  Seasonal='A': Additive Holt-Winters’ method
                Trend='A',  Seasonal='M': Multiplicative Holt-Winters’ method
                Trend='Ad', Seasonal='N': Additive damped trend method
                Trend='Ad', Seasonal='A': Exponential Smoothing
                Trend='Ad', Seasonal='M': Holt-Winters’ damped method
                Trend component: N: None, A: Additive, Ad: Additive Damped
                Seasonality component: N: None, A: Additive, M: Multiplicative
            """,
        )
        parser.add_argument(
            "-d",
            "--days",
            action="store",
            dest="n_days",
            type=check_positive,
            default=5,
            help="prediction days.",
        )
        parser.add_argument(
            "-t",
            "--trend",
            action="store",
            dest="trend",
            choices=["N", "A", "Ad"],
            default="N",
            help="Trend component: N: None, A: Additive, Ad: Additive Damped.",
        )
        parser.add_argument(
            "-s",
            "--seasonal",
            action="store",
            dest="seasonal",
            choices=["N", "A", "M"],
            default="N",
            help="Seasonality component: N: None, A: Additive, M: Multiplicative.",
        )
        parser.add_argument(
            "-p",
            "--periods",
            action="store",
            dest="seasonal_periods",
            type=check_positive,
            default=5,
            help="Seasonal periods.",
        )
        parser.add_argument(
            "-e",
            "--end",
            action="store",
            type=valid_date,
            dest="s_end_date",
            default=None,
            help="The end date (format YYYY-MM-DD) to select - Backtesting",
        )

        try:
            ns_parser = parse_known_args_and_warn(
                parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
            )
            if not ns_parser:
                return

            if ns_parser.s_end_date:

                if ns_parser.s_end_date < self.stock.index[0]:
                    print(
                        "Backtesting not allowed, since End Date is older than Start Date of historical data\n"
                    )
                    return

                if ns_parser.s_end_date < get_next_stock_market_days(
                    last_stock_day=self.stock.index[0],
                    n_next_days=5 + ns_parser.n_days,
                )[-1]:
                    print(
                        "Backtesting not allowed, since End Date is too close to Start Date to train model\n"
                    )
                    return

            ets_view.display_exponential_smoothing(
                ticker=self.ticker,
                values=self.stock[self.target],
                n_predict=ns_parser.n_days,
                trend=ns_parser.trend,
                seasonal=ns_parser.seasonal,
                seasonal_periods=ns_parser.seasonal_periods,
                s_end_date=ns_parser.s_end_date,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

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
                f"{get_flair()} (stocks)>(pred)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)>(pred)> ")

        try:
            plt.close("all")

            process_input = pred_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
