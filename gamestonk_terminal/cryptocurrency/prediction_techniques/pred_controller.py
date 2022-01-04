"""Crypto Prediction Controller"""
__docformat__ = "numpy"

import argparse
import difflib
from typing import List, Union

import pandas as pd
import numpy as np
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
    arima_model,
    arima_view,
    ets_model,
    ets_view,
    knn_view,
    mc_model,
    neural_networks_view,
    regression_view,
    pred_helper,
    mc_view,
)
from gamestonk_terminal.cryptocurrency import cryptocurrency_helpers as c_help


class PredictionTechniquesController:
    """Prediction Techniques Controller class"""

    # Command choices
    CHOICES = [
        "cls",
        "home",
        "h",
        "?",
        "help",
        "q",
        "quit",
        "..",
        "exit",
        "r",
        "reset",
    ]

    CHOICES_COMMANDS = [
        "pick",
        "load",
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
    CHOICES += CHOICES_COMMANDS
    sampling_map = {"H": "Hour", "D": "Day"}

    def __init__(
        self,
        coin: str,
        data: pd.DataFrame,
        queue: List[str] = None,
    ):
        """Constructor"""
        self.pred_parser = argparse.ArgumentParser(add_help=False, prog="pred")
        self.pred_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        data["Returns"] = data["Close"].pct_change()
        data["LogRet"] = np.log(data["Close"]) - np.log(data["Close"].shift(1))
        data = data.dropna()

        self.data = data
        self.coin = coin
        self.resolution = "1D"
        self.target = "Close"

        self.completer: Union[None, NestedCompleter] = None
        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["load"]["-r"] = {c: {} for c in c_help.INTERVALS}
            choices["pick"] = {c: {} for c in self.data.columns}
            choices["ets"]["-t"] = {c: {} for c in ets_model.TRENDS}
            choices["ets"]["-s"] = {c: {} for c in ets_model.SEASONS}
            choices["arima"]["-i"] = {c: {} for c in arima_model.ICS}
            choices["mc"]["--dist"] = {c: {} for c in mc_model.DISTRIBUTIONS}
            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""

        help_string = f"""
Prediction Techniques Menu:

    load        load new ticker
    pick        pick new target variable

Coin Loaded: {self.coin}
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

        Parameters
        -------
        an_input : str
            string with input arguments

        Returns
        -------
        List[str]
            List of commands in the queue to execute
        """

        # Empty command
        if not an_input:
            print("")
            return self.queue

        # Navigation slash is being used
        if "/" in an_input:
            actions = an_input.split("/")

            # Absolute path is specified
            if not actions[0]:
                an_input = "home"
            # Relative path so execute first instruction
            else:
                an_input = actions[0]

            # Add all instructions to the queue
            for cmd in actions[1:][::-1]:
                if cmd:
                    self.queue.insert(0, cmd)

        (known_args, other_args) = self.pred_parser.parse_known_args(an_input.split())

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

        return self.queue

    def call_cls(self, _):
        """Process cls command"""
        system_clear()

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_help(self, _):
        """Process help command"""
        self.print_help()

    def call_quit(self, _):
        """Process quit menu command"""
        print("")
        self.queue.insert(0, "quit")

    def call_exit(self, _):
        """Process exit terminal command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        self.queue.insert(0, "pred")
        if self.coin:
            self.queue.insert(0, f"load {self.coin}")
        self.queue.insert(0, "crypto")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
    def call_load(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="load",
            description="Load a new crypto dataframe",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="Coin to get data for",
            type=str,
            default=self.coin,
            dest="coin",
        )
        parser.add_argument(
            "-v",
            "--vs",
            help="Currency to compare coin to.",
            dest="currency",
            default="USD",
            type=str,
        )
        parser.add_argument(
            "-d",
            "--days",
            dest="days",
            type=check_positive,
            default=365,
            help="Number of days to get data for",
        )
        parser.add_argument(
            "-r",
            "--resolution",
            default="1D",
            type=str,
            dest="resolution",
            help="How often to resample data.",
            choices=c_help.INTERVALS,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        # TODO: improve loading from this submenu.  Currently would recommend using this menu after using main load
        if ns_parser:
            self.coin = ns_parser.coin
            self.data = c_help.load_cg_coin_data(
                ns_parser.coin, ns_parser.currency, ns_parser.days, ns_parser.resolution
            )
            res = ns_parser.resolution if ns_parser.days < 90 else "1D"
            self.resolution = res
            print(
                f"{ns_parser.days} Days of {self.coin} vs {ns_parser.currency} loaded with {res} resolution.\n"
            )

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
            choices=list(self.data.columns),
            help="Select variable to analyze",
        )
        if other_args and "-t" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            if ns_parser.s_end_date:
                if ns_parser.s_end_date < self.data.index[0]:
                    print(
                        "Backtesting not allowed, since End Date is older than Start Date of historical data\n"
                    )

                if ns_parser.s_end_date < get_next_stock_market_days(
                    last_stock_day=self.data.index[0],
                    n_next_days=5 + ns_parser.n_days,
                )[-1]:
                    print(
                        "Backtesting not allowed, since End Date is too close to Start Date to train model\n"
                    )

            ets_view.display_exponential_smoothing(
                ticker=self.coin,
                values=self.data[self.target],
                n_predict=ns_parser.n_days,
                trend=ns_parser.trend,
                seasonal=ns_parser.seasonal,
                seasonal_periods=ns_parser.seasonal_periods,
                s_end_date=ns_parser.s_end_date,
                export=ns_parser.export,
                time_res=self.resolution,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            knn_view.display_k_nearest_neighbors(
                ticker=self.coin,
                data=self.data[self.target],
                n_neighbors=ns_parser.n_neighbors,
                n_input_days=ns_parser.n_inputs,
                n_predict_days=ns_parser.n_days,
                test_size=ns_parser.valid_split,
                end_date=ns_parser.s_end_date,
                no_shuffle=ns_parser.no_shuffle,
                time_res=self.resolution,
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
        if ns_parser:
            # BACKTESTING CHECK
            if ns_parser.s_end_date:
                if ns_parser.s_end_date < self.data.index[0]:
                    print(
                        "Backtesting not allowed, since End Date is older than Start Date of historical data\n"
                    )

                if ns_parser.s_end_date < get_next_stock_market_days(
                    last_stock_day=self.data.index[0],
                    n_next_days=5 + ns_parser.n_days,
                )[-1]:
                    print(
                        "Backtesting not allowed, since End Date is too close to Start Date to train model\n"
                    )

            regression_view.display_regression(
                dataset=self.coin,
                values=self.data[self.target],
                poly_order=ns_parser.n_polynomial,
                n_input=ns_parser.n_inputs,
                n_predict=ns_parser.n_days,
                n_jumps=ns_parser.n_jumps,
                s_end_date=ns_parser.s_end_date,
                export=ns_parser.export,
                time_res=self.resolution,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            # BACKTESTING CHECK
            if ns_parser.s_end_date:
                if ns_parser.s_end_date < self.data.index[0]:
                    print(
                        "Backtesting not allowed, since End Date is older than Start Date of historical data\n"
                    )

                if ns_parser.s_end_date < get_next_stock_market_days(
                    last_stock_day=self.data.index[0],
                    n_next_days=5 + ns_parser.n_days,
                )[-1]:
                    print(
                        "Backtesting not allowed, since End Date is too close to Start Date to train model\n"
                    )

            arima_view.display_arima(
                dataset=self.coin,
                values=self.data[self.target],
                arima_order=ns_parser.s_order,
                n_predict=ns_parser.n_days,
                seasonal=ns_parser.b_seasonal,
                ic=ns_parser.s_ic,
                results=ns_parser.b_results,
                s_end_date=ns_parser.s_end_date,
                export=ns_parser.export,
                time_res=self.resolution,
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
            if ns_parser:
                neural_networks_view.display_mlp(
                    dataset=self.coin,
                    data=self.data[self.target],
                    n_input_days=ns_parser.n_inputs,
                    n_predict_days=ns_parser.n_days,
                    learning_rate=ns_parser.lr,
                    epochs=ns_parser.n_epochs,
                    batch_size=ns_parser.n_batch_size,
                    test_size=ns_parser.valid_split,
                    n_loops=ns_parser.n_loops,
                    no_shuffle=ns_parser.no_shuffle,
                    time_res=self.resolution,
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
            if ns_parser:
                neural_networks_view.display_rnn(
                    dataset=self.coin,
                    data=self.data[self.target],
                    n_input_days=ns_parser.n_inputs,
                    n_predict_days=ns_parser.n_days,
                    learning_rate=ns_parser.lr,
                    epochs=ns_parser.n_epochs,
                    batch_size=ns_parser.n_batch_size,
                    test_size=ns_parser.valid_split,
                    n_loops=ns_parser.n_loops,
                    no_shuffle=ns_parser.no_shuffle,
                    time_res=self.resolution,
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
            if ns_parser:
                neural_networks_view.display_lstm(
                    dataset=self.coin,
                    data=self.data[self.target],
                    n_input_days=ns_parser.n_inputs,
                    n_predict_days=ns_parser.n_days,
                    learning_rate=ns_parser.lr,
                    epochs=ns_parser.n_epochs,
                    batch_size=ns_parser.n_batch_size,
                    test_size=ns_parser.valid_split,
                    n_loops=ns_parser.n_loops,
                    no_shuffle=ns_parser.no_shuffle,
                    time_res=self.resolution,
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
            if ns_parser:
                neural_networks_view.display_conv1d(
                    dataset=self.coin,
                    data=self.data[self.target],
                    n_input_days=ns_parser.n_inputs,
                    n_predict_days=ns_parser.n_days,
                    learning_rate=ns_parser.lr,
                    epochs=ns_parser.n_epochs,
                    batch_size=ns_parser.n_batch_size,
                    test_size=ns_parser.valid_split,
                    n_loops=ns_parser.n_loops,
                    no_shuffle=ns_parser.no_shuffle,
                    time_res=self.resolution,
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
            choices=mc_model.DISTRIBUTIONS,
            default="lognormal",
            dest="dist",
            help="Whether to model returns or log returns",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if self.target != "Close":
            print("MC Prediction designed for AdjClose prices\n")

        if ns_parser:
            mc_view.display_mc_forecast(
                data=self.data[self.target],
                n_future=ns_parser.n_days,
                n_sims=ns_parser.n_sims,
                use_log=ns_parser.dist == "lognormal",
                export=ns_parser.export,
                time_res=self.resolution,
            )


def menu(coin: str, data: pd.DataFrame, queue: List[str] = None):
    """Prediction Techniques Menu"""

    pred_controller = PredictionTechniquesController(coin, data, queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if pred_controller.queue and len(pred_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if pred_controller.queue[0] in ("q", "..", "quit"):
                if len(pred_controller.queue) > 1:
                    return pred_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = pred_controller.queue[0]
            pred_controller.queue = pred_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in pred_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /crypto/pred/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                pred_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and pred_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /crypto/pred/ $ ",
                        completer=pred_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /crypto/pred/ $ ")

        try:
            # Process the input command
            pred_controller.queue = pred_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/options menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                pred_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                    if candidate_input == an_input:
                        an_input = ""
                        pred_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                pred_controller.queue.insert(0, an_input)
            else:
                print("\n")
