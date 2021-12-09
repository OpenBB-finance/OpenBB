""" Prediction Controller """
__docformat__ = "numpy"

import argparse
import difflib
from typing import List
from datetime import datetime, timedelta
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
    try_except,
    system_clear,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.common.prediction_techniques import (
    arima_view,
    ets_view,
    knn_view,
    neural_networks_view,
    regression_view,
    pred_helper,
    mc_view,
)
from gamestonk_terminal.stocks import stocks_helper


class PredictionTechniquesController:
    """Prediction Techniques Controller class"""

    # Command choices
    CHOICES = ["cls", "?", "help", "q", "quit", "load", "pick"]

    CHOICES_MODELS = [
        "ets",
        "knn",
        "regression",
        "arima",
        "mlp",
        "rnn",
        "lstm",
        "conv1d",
        "mc",
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

        help_string = f"""
Prediction Techniques:
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
    regression  polynomial regression
    arima       autoregressive integrated moving average
    mlp         MultiLayer Perceptron
    rnn         Recurrent Neural Network
    lstm        Long-Short Term Memory
    conv1d      1D Convolutional Neural Network
    mc          Monte-Carlo simulations
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
            system_clear()
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
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load stock ticker to perform analysis on. When the data source is 'yf', an Indian ticker can be"
            " loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in"
            " https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html.",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            action="store",
            dest="ticker",
            required="-h" not in other_args,
            help="Stock ticker",
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the stock",
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            default=datetime.now().strftime("%Y-%m-%d"),
            dest="end",
            help="The ending date (format YYYY-MM-DD) of the stock",
        )
        parser.add_argument(
            "-i",
            "--interval",
            action="store",
            dest="interval",
            type=int,
            default=1440,
            choices=[1, 5, 15, 30, 60],
            help="Intraday stock minutes",
        )
        parser.add_argument(
            "--source",
            action="store",
            dest="source",
            choices=["yf", "av", "iex"],
            default="yf",
            help="Source of historical data.",
        )
        parser.add_argument(
            "-p",
            "--prepost",
            action="store_true",
            default=False,
            dest="prepost",
            help="Pre/After market hours. Only works for 'yf' source, and intraday data",
        )

        # For the case where a user uses: 'load BB'
        if other_args and "-t" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_stock_candidate = stocks_helper.load(
            ns_parser.ticker,
            ns_parser.start,
            ns_parser.interval,
            ns_parser.end,
            ns_parser.prepost,
            ns_parser.source,
        )

        if not df_stock_candidate.empty:
            self.stock = df_stock_candidate
            if "." in ns_parser.ticker:
                self.ticker = ns_parser.ticker.upper().split(".")[0]
            else:
                self.ticker = ns_parser.ticker.upper()

            self.start = ns_parser.start
            self.interval = str(ns_parser.interval) + "min"

            self.stock["Returns"] = self.stock["Adj Close"].pct_change()
            self.stock["LogRet"] = np.log(self.stock["Adj Close"]) - np.log(
                self.stock["Adj Close"].shift(1)
            )
            self.stock = self.stock.rename(columns={"Adj Close": "AdjClose"})
            self.stock = self.stock.dropna()

    @try_except
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
        if other_args and "-t" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        self.target = ns_parser.target
        print("")

    @try_except
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

    @try_except
    def call_knn(self, other_args: List[str]):
        """Process knn command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="knn",
            description="""
                K nearest neighbors is a simple algorithm that stores all
                available cases and predict the numerical target based on a similarity measure
                (e.g. distance functions).
            """,
        )
        parser.add_argument(
            "-i",
            "--input",
            action="store",
            dest="n_inputs",
            type=check_positive,
            default=40,
            help="number of days to use as input for prediction.",
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
            "-j",
            "--jumps",
            action="store",
            dest="n_jumps",
            type=check_positive,
            default=1,
            help="number of jumps in training data.",
        )
        parser.add_argument(
            "-n",
            "--neighbors",
            action="store",
            dest="n_neighbors",
            type=check_positive,
            default=20,
            help="number of neighbors to use on the algorithm.",
        )
        parser.add_argument(
            "-e",
            "--end",
            action="store",
            type=valid_date,
            dest="s_end_date",
            default=None,
            help="The end date (format YYYY-MM-DD) to select for testing",
        )
        parser.add_argument(
            "-t",
            "--test_size",
            default=0.2,
            dest="valid_split",
            type=float,
            help="Percentage of data to validate in sample",
        )
        parser.add_argument(
            "--no_shuffle",
            action="store_false",
            dest="no_shuffle",
            default=True,
            help="Specify if shuffling validation inputs.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        knn_view.display_k_nearest_neighbors(
            ticker=self.ticker,
            data=self.stock[self.target],
            n_neighbors=ns_parser.n_neighbors,
            n_input_days=ns_parser.n_inputs,
            n_predict_days=ns_parser.n_days,
            test_size=ns_parser.valid_split,
            end_date=ns_parser.s_end_date,
            no_shuffle=ns_parser.no_shuffle,
        )

    @try_except
    def call_regression(self, other_args: List[str]):
        """Process linear command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="regression",
            description="""
                Regression attempts to model the relationship between
                two variables by fitting a linear/quadratic/cubic/other equation to
                observed data. One variable is considered to be an explanatory variable,
                and the other is considered to be a dependent variable.
            """,
        )

        parser.add_argument(
            "-i",
            "--input",
            action="store",
            dest="n_inputs",
            type=check_positive,
            default=40,
            help="number of days to use for prediction.",
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
            "-j",
            "--jumps",
            action="store",
            dest="n_jumps",
            type=check_positive,
            default=1,
            help="number of jumps in training data.",
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
        parser.add_argument(
            "-p",
            "--polynomial",
            action="store",
            dest="n_polynomial",
            type=check_positive,
            default=1,
            help="polynomial associated with regression.",
        )
        if (
            other_args
            and "-h" not in other_args
            and ("-p" not in other_args or "--polynomial" not in other_args)
        ):
            other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if not ns_parser:
            return
        # BACKTESTING CHECK
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

        regression_view.display_regression(
            dataset=self.ticker,
            values=self.stock[self.target],
            poly_order=ns_parser.n_polynomial,
            n_input=ns_parser.n_inputs,
            n_predict=ns_parser.n_days,
            n_jumps=ns_parser.n_jumps,
            s_end_date=ns_parser.s_end_date,
            export=ns_parser.export,
        )

    @try_except
    def call_arima(self, other_args: List[str]):
        """Process arima command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="arima",
            description="""
                In statistics and econometrics, and in particular in time series analysis, an
                autoregressive integrated moving average (ARIMA) model is a generalization of an
                autoregressive moving average (ARMA) model. Both of these models are fitted to time
                series data either to better understand the data or to predict future points in the
                series (forecasting). ARIMA(p,d,q) where parameters p, d, and q are non-negative
                integers, p is the order (number of time lags) of the autoregressive model, d is the
                degree of differencing (the number of times the data have had past values subtracted),
                and q is the order of the moving-average model.
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
            "-i",
            "--ic",
            action="store",
            dest="s_ic",
            type=str,
            default="aic",
            choices=["aic", "aicc", "bic", "hqic", "oob"],
            help="information criteria.",
        )
        parser.add_argument(
            "-s",
            "--seasonal",
            action="store_true",
            default=False,
            dest="b_seasonal",
            help="Use weekly seasonal data.",
        )
        parser.add_argument(
            "-o",
            "--order",
            action="store",
            dest="s_order",
            default="",
            type=str,
            help="arima model order (p,d,q) in format: p,d,q.",
        )
        parser.add_argument(
            "-r",
            "--results",
            action="store_true",
            dest="b_results",
            default=False,
            help="results about ARIMA summary flag.",
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if not ns_parser:
            return

        # BACKTESTING CHECK
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

        arima_view.display_arima(
            dataset=self.ticker,
            values=self.stock[self.target],
            arima_order=ns_parser.s_order,
            n_predict=ns_parser.n_days,
            seasonal=ns_parser.b_seasonal,
            ic=ns_parser.s_ic,
            results=ns_parser.b_results,
            s_end_date=ns_parser.s_end_date,
            export=ns_parser.export,
        )

    @try_except
    def call_mlp(self, other_args: List[str]):
        """Process mlp command"""
        try:
            ns_parser = pred_helper.parse_args(
                prog="mlp",
                description="""Multi-Layered-Perceptron. """,
                other_args=other_args,
            )
            if not ns_parser:
                return

            neural_networks_view.display_mlp(
                dataset=self.ticker,
                data=self.stock[self.target],
                n_input_days=ns_parser.n_inputs,
                n_predict_days=ns_parser.n_days,
                learning_rate=ns_parser.lr,
                epochs=ns_parser.n_epochs,
                batch_size=ns_parser.n_batch_size,
                test_size=ns_parser.valid_split,
                n_loops=ns_parser.n_loops,
                no_shuffle=ns_parser.no_shuffle,
            )
        except Exception as e:
            print(e, "\n")

        finally:
            pred_helper.restore_env()

    def call_rnn(self, other_args: List[str]):
        """Process rnn command"""
        try:
            ns_parser = pred_helper.parse_args(
                prog="rnn",
                description="""Recurrent Neural Network. """,
                other_args=other_args,
            )
            if not ns_parser:
                return

            neural_networks_view.display_rnn(
                dataset=self.ticker,
                data=self.stock[self.target],
                n_input_days=ns_parser.n_inputs,
                n_predict_days=ns_parser.n_days,
                learning_rate=ns_parser.lr,
                epochs=ns_parser.n_epochs,
                batch_size=ns_parser.n_batch_size,
                test_size=ns_parser.valid_split,
                n_loops=ns_parser.n_loops,
                no_shuffle=ns_parser.no_shuffle,
            )

        except Exception as e:
            print(e, "\n")

        finally:
            pred_helper.restore_env()

    def call_lstm(self, other_args: List[str]):
        """Process lstm command"""
        try:
            ns_parser = pred_helper.parse_args(
                prog="lstm",
                description="""Long-Short Term Memory. """,
                other_args=other_args,
            )
            if not ns_parser:
                return
            neural_networks_view.display_lstm(
                dataset=self.ticker,
                data=self.stock[self.target],
                n_input_days=ns_parser.n_inputs,
                n_predict_days=ns_parser.n_days,
                learning_rate=ns_parser.lr,
                epochs=ns_parser.n_epochs,
                batch_size=ns_parser.n_batch_size,
                test_size=ns_parser.valid_split,
                n_loops=ns_parser.n_loops,
                no_shuffle=ns_parser.no_shuffle,
            )

        except Exception as e:
            print(e, "\n")

        finally:
            pred_helper.restore_env()

    def call_conv1d(self, other_args: List[str]):
        """Process conv1d command"""
        try:
            ns_parser = pred_helper.parse_args(
                prog="conv1d",
                description="""1D CNN.""",
                other_args=other_args,
            )
            if not ns_parser:
                return

            neural_networks_view.display_conv1d(
                dataset=self.ticker,
                data=self.stock[self.target],
                n_input_days=ns_parser.n_inputs,
                n_predict_days=ns_parser.n_days,
                learning_rate=ns_parser.lr,
                epochs=ns_parser.n_epochs,
                batch_size=ns_parser.n_batch_size,
                test_size=ns_parser.valid_split,
                n_loops=ns_parser.n_loops,
                no_shuffle=ns_parser.no_shuffle,
            )

        except Exception as e:
            print(e, "\n")

        finally:
            pred_helper.restore_env()

    @try_except
    def call_mc(self, other_args: List[str]):
        """Process mc command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="mc",
            description="""
                Perform Monte Carlo forecasting
            """,
        )
        parser.add_argument(
            "-d",
            "--days",
            help="Days to predict",
            dest="n_days",
            type=check_positive,
            default=30,
        )
        parser.add_argument(
            "-n",
            "--num",
            help="Number of simulations to perform",
            dest="n_sims",
            default=100,
        )
        parser.add_argument(
            "--dist",
            choices=["normal", "lognormal"],
            default="lognormal",
            dest="dist",
            help="Whether to model returns or log returns",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if not ns_parser:
            return
        if self.target != "AdjClose":
            print("MC Prediction designed for AdjClose prices")
            return

        mc_view.display_mc_forecast(
            data=self.stock[self.target],
            n_future=ns_parser.n_days,
            n_sims=ns_parser.n_sims,
            use_log=ns_parser.dist == "lognormal",
            export=ns_parser.export,
        )


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
            similar_cmd = difflib.get_close_matches(
                an_input, pred_controller.CHOICES, n=1, cutoff=0.7
            )

            if similar_cmd:
                print(f"Did you mean '{similar_cmd[0]}'?\n")
            continue
