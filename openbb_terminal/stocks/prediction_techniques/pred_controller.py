""" Prediction Controller """
__docformat__ = "numpy"

import argparse
import logging
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.common.prediction_techniques import (
    arima_model,
    arima_view,
    ets_model,
    ets_view,
    knn_view,
    mc_model,
    mc_view,
    neural_networks_view,
    pred_helper,
    regression_view,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_FIGURES_ALLOWED,
    check_positive,
    get_next_stock_market_days,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.stocks import stocks_helper

logger = logging.getLogger(__name__)


class PredictionTechniquesController(BaseController):
    """Prediction Techniques Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "pick",
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

    PATH = "/stocks/pred/"

    def __init__(
        self,
        ticker: str,
        start: datetime,
        interval: str,
        stock: pd.DataFrame,
        queue: List[str] = None,
    ):
        """Constructor"""
        super().__init__(queue)

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

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["load"]["-r"] = {c: {} for c in stocks_helper.INTERVALS}
            choices["pick"] = {c: {} for c in stock.columns}
            choices["ets"]["-t"] = {c: {} for c in ets_model.TRENDS}
            choices["ets"]["-s"] = {c: {} for c in ets_model.SEASONS}
            choices["arima"]["-i"] = {c: {} for c in arima_model.ICS}
            choices["mc"]["--dist"] = {c: {} for c in mc_model.DISTRIBUTIONS}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        s_intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]
        if self.start:
            stock_info = (
                f"{s_intraday} {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
            )
        else:
            stock_info = f"{s_intraday} {self.ticker}"

        mt = MenuText("stocks/pred/")
        mt.add_cmd("load")
        mt.add_cmd("pick")
        mt.add_raw("\n")
        mt.add_param("_ticker", stock_info)
        mt.add_param("_target", self.target)
        mt.add_raw("\n")
        mt.add_info("_models_")
        mt.add_cmd("ets")
        mt.add_cmd("knn")
        mt.add_cmd("regression")
        mt.add_cmd("arima")
        mt.add_cmd("mlp")
        mt.add_cmd("rnn")
        mt.add_cmd("lstm")
        mt.add_cmd("conv1d")
        mt.add_cmd("mc")
        console.print(text=mt.menu_text, menu="Stocks - Prediction Techniques")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            return ["stocks", f"load {self.ticker}", "pred"]
        return []

    @log_start_end(log=logger)
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

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            self.target = ns_parser.target
            console.print("")

    @log_start_end(log=logger)
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
            choices=ets_model.TRENDS,
            default="N",
            help="Trend component: N: None, A: Additive, Ad: Additive Damped.",
        )
        parser.add_argument(
            "-s",
            "--seasonal",
            action="store",
            dest="seasonal",
            choices=ets_model.SEASONS,
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:

            if ns_parser.s_end_date:

                if ns_parser.s_end_date < self.stock.index[0]:
                    console.print(
                        "Backtesting not allowed, since End Date is older than Start Date of historical data\n"
                    )

                if (
                    ns_parser.s_end_date
                    < get_next_stock_market_days(
                        last_stock_day=self.stock.index[0],
                        n_next_days=5 + ns_parser.n_days,
                    )[-1]
                ):
                    console.print(
                        "Backtesting not allowed, since End Date is too close to Start Date to train model\n"
                    )

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

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
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

    @log_start_end(log=logger)
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            # BACKTESTING CHECK
            if ns_parser.s_end_date:
                if ns_parser.s_end_date < self.stock.index[0]:
                    console.print(
                        "Backtesting not allowed, since End Date is older than Start Date of historical data\n"
                    )

                if (
                    ns_parser.s_end_date
                    < get_next_stock_market_days(
                        last_stock_day=self.stock.index[0],
                        n_next_days=5 + ns_parser.n_days,
                    )[-1]
                ):
                    console.print(
                        "Backtesting not allowed, since End Date is too close to Start Date to train model\n"
                    )

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

    @log_start_end(log=logger)
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
            choices=arima_model.ICS,
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            # BACKTESTING CHECK
            if ns_parser.s_end_date:

                if ns_parser.s_end_date < self.stock.index[0]:
                    console.print(
                        "Backtesting not allowed, since End Date is older than Start Date of historical data\n"
                    )

                if (
                    ns_parser.s_end_date
                    < get_next_stock_market_days(
                        last_stock_day=self.stock.index[0],
                        n_next_days=5 + ns_parser.n_days,
                    )[-1]
                ):
                    console.print(
                        "Backtesting not allowed, since End Date is too close to Start Date to train model\n"
                    )

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

    @log_start_end(log=logger)
    def call_mlp(self, other_args: List[str]):
        """Process mlp command"""
        try:
            ns_parser = pred_helper.parse_args(
                prog="mlp",
                description="""Multi-Layered-Perceptron. """,
                other_args=other_args,
            )
            if ns_parser:
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
            logger.exception(str(e))
            console.print(e, "\n")

        finally:
            pred_helper.restore_env()

    @log_start_end(log=logger)
    def call_rnn(self, other_args: List[str]):
        """Process rnn command"""
        try:
            ns_parser = pred_helper.parse_args(
                prog="rnn",
                description="""Recurrent Neural Network. """,
                other_args=other_args,
            )
            if ns_parser:
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
            logger.exception(str(e))
            console.print(e, "\n")

        finally:
            pred_helper.restore_env()

    @log_start_end(log=logger)
    def call_lstm(self, other_args: List[str]):
        """Process lstm command"""
        try:
            ns_parser = pred_helper.parse_args(
                prog="lstm",
                description="""Long-Short Term Memory. """,
                other_args=other_args,
            )
            if ns_parser:
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
            logger.exception(str(e))
            console.print(e, "\n")

        finally:
            pred_helper.restore_env()

    @log_start_end(log=logger)
    def call_conv1d(self, other_args: List[str]):
        """Process conv1d command"""
        try:
            ns_parser = pred_helper.parse_args(
                prog="conv1d",
                description="""1D CNN.""",
                other_args=other_args,
            )
            if ns_parser:
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
            logger.exception(str(e))
            console.print(e, "\n")

        finally:
            pred_helper.restore_env()

    @log_start_end(log=logger)
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
            type=check_positive,
        )
        parser.add_argument(
            "--dist",
            choices=mc_model.DISTRIBUTIONS,
            default="lognormal",
            dest="dist",
            help="Whether to model returns or log returns",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            if self.target != "AdjClose":
                console.print("MC Prediction designed for AdjClose prices\n")

            mc_view.display_mc_forecast(
                data=self.stock[self.target],
                n_future=ns_parser.n_days,
                n_sims=ns_parser.n_sims,
                use_log=ns_parser.dist == "lognormal",
                export=ns_parser.export,
            )
