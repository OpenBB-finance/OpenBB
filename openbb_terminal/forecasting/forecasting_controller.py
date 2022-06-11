"""Forecasting Controller Module"""
__docformat__ = "numpy"

# pylint: disable=too-many-lines, too-many-branches, inconsistent-return-statements

import argparse
import logging
from itertools import chain
import os
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    check_positive,
    check_positive_float,
    parse_known_args_and_warn,
    NO_EXPORT,
    EXPORT_ONLY_FIGURES_ALLOWED,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    export_data,
)
from openbb_terminal.helper_funcs import (
    print_rich_table,
    check_list_values,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.forecasting import (
    forecasting_model,
    forecasting_view,
    expo_model,
    expo_view,
    theta_model,
    theta_view,
    rnn_view,
    NBEATS_view,
)

logger = logging.getLogger(__name__)

# pylint: disable=R0902


class ForecastingController(BaseController):
    """Forecasting class"""

    CHOICES_COMMANDS: List[str] = ["load", "show", "expo", "theta", "rnn", "nbeats"]
    # CHOICES_MENUS: List[str] = ["qa", "pred"]
    pandas_plot_choices = [
        "line",
        "scatter",
        "bar",
        "barh",
        "hist",
        "box",
        "kde",
        "area",
        "pie",
        "hexbin",
    ]
    PATH = "/forecasting/"

    loaded_dataset_cols = "\n"
    list_dataset_cols: List = list()

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)
        self.files: List[str] = list()
        self.datasets: Dict[str, pd.DataFrame] = dict()
        self.regression: Dict[Any[Dict, Any], Any] = dict()

        self.DATA_TYPES: List[str] = ["int", "float", "str", "bool", "category", "date"]

        self.signs: Dict[Any, Any] = {
            "div": "/",
            "mul": "*",
            "add": "+",
            "sub": "-",
            "mod": "%",
            "pow": "**",
        }
        self.file_types = ["csv", "xlsx"]
        self.DATA_FILES = {
            filepath.name: filepath
            for file_type in self.file_types
            for filepath in chain(
                Path(obbff.EXPORT_FOLDER_PATH).rglob(f"*.{file_type}"),
                Path("custom_imports").rglob(f"*.{file_type}"),
            )
            if filepath.is_file()
        }

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["load"] = {c: None for c in self.DATA_FILES.keys()}
            choices["show"] = {c: None for c in self.files}

            self.choices = choices

            # To link to the support HTML
            choices["support"] = self.SUPPORT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def update_runtime_choices(self):
        if session and obbff.USE_PROMPT_TOOLKIT:

            # Autocomplete for the user to use a particular dataset
            for feature in [
                "show",
            ]:  # "expo"]:
                self.choices[feature] = {c: None for c in self.files}

            self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("forecasting/")
        mt.add_param(
            "_data_loc",
            f"\n\t{obbff.EXPORT_FOLDER_PATH}\n\t{Path('custom_imports').resolve()}",
        )
        mt.add_raw("\n")
        mt.add_cmd("load")
        mt.add_raw("\n")
        mt.add_param("_loaded", self.loaded_dataset_cols)
        mt.add_info("_exploration_")
        mt.add_cmd("show", "", self.files)
        mt.add_info("_tsforecasting_")
        mt.add_cmd("expo", "", self.files)
        mt.add_cmd("theta", "", self.files)
        mt.add_cmd("rnn", "", self.files)
        mt.add_cmd("nbeats", "", self.files)

        console.print(text=mt.menu_text, menu="Forecasting")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.files:
            load_files = [f"load {file}" for file in self.files]
            return ["forecasting"] + load_files
        return []

    @log_start_end(log=logger)
    def call_load(self, other_args: List[str]):
        """Process load"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load custom dataset (from previous export, custom imports).",
        )
        parser.add_argument(
            "-f",
            "--file",
            help="File to load data in (can be custom import, may have been exported before.)",
            type=str,
        )
        parser.add_argument(
            "-a",
            "--alias",
            help="Alias name to give to the dataset",
            type=str,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if ns_parser.file:
                file = ns_parser.file
                if ns_parser.alias:
                    alias = ns_parser.alias
                else:
                    if "." in ns_parser.file:
                        alias = ".".join(ns_parser.file.split(".")[:-1])
                    else:
                        alias = ns_parser.file

                # check if this dataset has been added already
                if alias in self.files:
                    console.print(
                        "[red]The file/dataset selected has already been loaded.[/red]\n"
                    )
                    return

                data = forecasting_model.load(file, self.file_types, self.DATA_FILES)

                if not data.empty:
                    data.columns = data.columns.map(
                        lambda x: x.lower().replace(" ", "_")
                    )

                    self.files.append(alias)
                    self.datasets[alias] = data

                    self.update_runtime_choices()

                    # Process new datasets to be updated
                    self.list_dataset_cols = list()
                    maxfile = max(len(file) for file in self.files)
                    self.loaded_dataset_cols = "\n"
                    for dataset, data in self.datasets.items():
                        self.loaded_dataset_cols += (
                            f"  {dataset} {(maxfile - len(dataset)) * ' '}: "
                            f"{', '.join(data.columns)}\n"
                        )

                        for col in data.columns:
                            self.list_dataset_cols.append(f"{dataset}.{col}")

                    console.print()

    # Show selected dataframe on console
    @log_start_end(log=logger)
    def call_show(self, other_args: List[str]):
        """Process show command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="show",
            description="Show a portion of the DataFrame",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            choices=self.files,
            dest="name",
            help="The name of the database you want to show data for",
        )
        parser.add_argument(
            "-s",
            "--sortcol",
            help="Sort based on a column in the DataFrame",
            nargs="+",
            type=str,
            dest="sortcol",
            default="",
        )
        parser.add_argument(
            "-a",
            "--ascend",
            help="Use this argument to sort in a descending order",
            action="store_true",
            default=False,
            dest="ascend",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED, limit=10
        )

        if ns_parser:
            if not ns_parser.name:
                dataset_names = list(self.datasets.keys())
            else:
                dataset_names = [ns_parser.name]

            for name in dataset_names:
                df = self.datasets[name]

                if name in self.datasets and self.datasets[name].empty:
                    return console.print(
                        f"[red]No data available for {ns_parser.name}.[/red]\n"
                    )
                if ns_parser.sortcol:
                    sort_column = " ".join(ns_parser.sortcol)
                    if sort_column not in self.datasets[name].columns:
                        console.print(
                            f"[red]{sort_column} not a valid column. Showing without sorting.\n[/red]"
                        )
                    else:
                        df = df.sort_values(by=sort_column, ascending=ns_parser.ascend)

                print_rich_table(
                    df.head(ns_parser.limit),
                    headers=list(df.columns),
                    show_index=True,
                    title=f"Dataset {name} | Showing {ns_parser.limit} of {len(df)} rows",
                )

                export_data(
                    ns_parser.export,
                    os.path.dirname(os.path.abspath(__file__)),
                    f"{ns_parser.name}_show",
                    df.head(ns_parser.limit),
                )

    """
    TODO:
    - target series and supplimental series
    - Timeseries frequency
    - past covariates aka. pick columns
    - create your own time series
    """

    # EXPO Model
    @log_start_end(log=logger)
    def call_expo(self, other_args: List[str]):
        """Process expo command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="expo",
            description="""
                Perform Probabilistic Exponential Smoothing forecast
                Trend: N: None, A: Additive, M: Multiplicative
                Seasonality: N: None, A: Additive, M: Multiplicative
                Dampen: T: True, F: False
            """,
        )
        parser.add_argument(
            "--td",
            type=str,
            choices=self.files,
            dest="target_dataset",
            help="Dataset name",
        )
        parser.add_argument(
            "--n_days",
            action="store",
            dest="n_days",
            type=check_positive,
            default=5,
            help="prediction days.",
        )
        parser.add_argument(
            "--tc",
            action="store",
            dest="target_col",
            default="close",
            help="target column.",
        )
        parser.add_argument(
            "--trend",
            action="store",
            dest="trend",
            choices=expo_model.TRENDS,
            default="A",
            help="Trend: N: None, A: Additive, M: Multiplicative.",
        )
        parser.add_argument(
            "-s",
            "--seasonal",
            action="store",
            dest="seasonal",
            choices=expo_model.SEASONS,
            default="A",
            help="Seasonality: N: None, A: Additive, M: Multiplicative.",
        )
        parser.add_argument(
            "-p",
            "--periods",
            action="store",
            dest="seasonal_periods",
            type=check_positive,
            default=7,
            help="Seasonal periods: 4: Quarterly, 7: Daily",
        )
        parser.add_argument(
            "-d",
            "--dampen",
            action="store",
            dest="dampen",
            default="F",
            help="Dampening",
        )
        parser.add_argument(
            "-w",
            "--window",
            action="store",
            dest="start_window",
            default=0.65,
            help="Start point for rolling training and forecast window. 0.0-1.0",
        )
        parser.add_argument(
            "--forecasthorizon",
            action="store",
            dest="forecast_horizon",
            default=3,
            help="Days/Points to forecast when training and performing historical back-testing",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        # TODO Convert this to multi series
        if ns_parser:

            # check proper file name is provided
            if not ns_parser.target_dataset:
                console.print("[red]Please enter valid dataset.\n[/red]")
                return

            # must check that target col is within target series
            if (
                ns_parser.target_col
                not in self.datasets[ns_parser.target_dataset].columns
            ):
                console.print(ns_parser.target_col)
                console.print(
                    f"[red]The target column {ns_parser.target_col} does not exist in dataframe.\n[/red]"
                )
                return

            expo_view.display_expo_forecast(
                data=self.datasets[ns_parser.target_dataset],
                ticker_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_col=ns_parser.target_col,
                trend=ns_parser.trend,
                seasonal=ns_parser.seasonal,
                seasonal_periods=ns_parser.seasonal_periods,
                dampen=ns_parser.dampen,
                start_window=ns_parser.start_window,
                forecast_horizon=ns_parser.forecast_horizon,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_theta(self, other_args: List[str]):
        """Process theta command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="theta",
            description="""
                Perform Theta forecast
            """,
        )
        parser.add_argument(
            "--td",
            type=str,
            choices=self.files,
            dest="target_dataset",
            help="Dataset name",
        )
        parser.add_argument(
            "-n",
            "--n_days",
            action="store",
            dest="n_days",
            type=check_positive,
            default=5,
            help="prediction days.",
        )
        parser.add_argument(
            "--tc",
            action="store",
            dest="target_col",
            default="close",
            help="target column.",
        )
        parser.add_argument(
            "-s",
            "--seasonal",
            action="store",
            dest="seasonal",
            choices=theta_model.SEASONS,
            default="M",
            help="Seasonality: N: None, A: Additive, M: Multiplicative.",
        )
        parser.add_argument(
            "-p",
            "--periods",
            action="store",
            dest="seasonal_periods",
            type=check_positive,
            default=7,
            help="Seasonal periods: 4: Quarterly, 7: Daily",
        )
        parser.add_argument(
            "-w",
            "--window",
            action="store",
            dest="start_window",
            default=0.65,
            help="Start point for rolling training and forecast window. 0.0-1.0",
        )
        parser.add_argument(
            "--forecasthorizon",
            action="store",
            dest="forecast_horizon",
            default=3,
            help="Days/Points to forecast when training and performing historical back-testing",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )

        if ns_parser:
            # check proper file name is provided
            if not ns_parser.target_dataset:
                console.print("[red]Please enter valid dataset.\n[/red]")
                return

            # must check that target col is within target series
            if (
                ns_parser.target_col
                not in self.datasets[ns_parser.target_dataset].columns
            ):
                console.print(
                    f"[red]The target column {ns_parser.target_col} does not exist in dataframe.\n[/red]"
                )
                return

            theta_view.display_theta_forecast(
                data=self.datasets[ns_parser.target_dataset],
                ticker_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_col=ns_parser.target_col,
                seasonal=ns_parser.seasonal,
                seasonal_periods=ns_parser.seasonal_periods,
                start_window=ns_parser.start_window,
                forecast_horizon=ns_parser.forecast_horizon,
                export=ns_parser.export,
            )

    # TODO add in all the hyperparameters ZzZzzzzZzzzZzzzzzz
    # TODO Add in Inference menu so that people can bring in their own models
    @log_start_end(log=logger)
    def call_rnn(self, other_args: List[str]):
        """Process RNN command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="rnn",
            description="""
                Perform RNN forecast (Vanilla RNN, LSTM, GRU)
            """,
        )
        parser.add_argument(
            "--target_dataset",
            type=str,
            choices=self.files,
            dest="target_dataset",
            help="Dataset name",
        )
        parser.add_argument(
            "-n",
            "--n_days",
            action="store",
            dest="n_days",
            type=check_positive,
            default=5,
            help="prediction days.",
        )
        parser.add_argument(
            "--target_forecast_column",
            action="store",
            dest="target_col",
            default="close",
            type=str,
            help="target column.",
        )
        parser.add_argument(
            "--train_split",
            action="store",
            dest="train_split",
            default=0.85,
            type=check_positive_float,
            help="Start point for rolling training and forecast window. 0.0-1.0",
        )
        parser.add_argument(
            "--forecasthorizon",
            action="store",
            dest="forecast_horizon",
            default=3,
            help="Days/Points to forecast when training and performing historical back-testing",
        )
        # RNN Hyperparameters
        parser.add_argument(
            "--model_type",
            type=str,
            action="store",
            dest="model_type",
            default="LSTM",
            help='Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU")',
        )
        parser.add_argument(
            "--hidden_dim",
            action="store",
            dest="hidden_dim",
            default=20,
            type=check_positive,
            help="Size for feature maps for each hidden RNN layer (h_n)",
        )
        parser.add_argument(
            "--dropout",
            action="store",
            dest="dropout",
            default=0,
            type=check_positive_float,
            help="Fraction of neurons afected by Dropout.",
        )
        parser.add_argument(
            "--batch_size",
            action="store",
            dest="batch_size",
            default=32,
            type=check_positive,
            help="Number of time series (input and output sequences) used in each training pass",
        )
        parser.add_argument(
            "--n_epochs",
            action="store",
            dest="n_epochs",
            default=100,
            type=check_positive,
            help="Number of epochs over which to train the model.",
        )
        parser.add_argument(
            "--learning_rate",
            action="store",
            dest="learning_rate",
            default=1e-3,
            type=check_positive_float,
            help="Learning rate during training.",
        )
        parser.add_argument(
            "--model_save_name",
            type=str,
            action="store",
            dest="model_save_name",
            default="rnn_model",
            help="Name of the model to save.",
        )
        parser.add_argument(
            "--training_length",
            action="store",
            dest="training_length",
            default=20,
            type=check_positive,
            help="""The length of both input (target and covariates) and output (target) time series used during training.
            Generally speaking, training_length should have a higher value than input_chunk_length because otherwise
            during training the RNN is never run for as many iterations as it will during training.""",
        )
        parser.add_argument(
            "--input_chunk_size",
            action="store",
            dest="input_chunk_size",
            default=14,
            type=check_positive,
            help="Number of past time steps that are fed to the forecasting module at prediction time.",
        )
        parser.add_argument(
            "--force_reset",
            action="store",
            dest="force_reset",
            default=True,
            type=bool,
            help="If set to True, any previously-existing model with the same name will be reset (all checkpoints will be discarded).",
        )
        parser.add_argument(
            "--save_checkpoints",
            action="store",
            dest="save_checkpoints",
            default=True,
            type=bool,
            help="Whether or not to automatically save the untrained model and checkpoints from training.",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )

        if ns_parser:
            # check proper file name is provided
            if not ns_parser.target_dataset:
                console.print("[red]Please enter valid dataset.\n[/red]")
                return

            # must check that target col is within target series
            if (
                ns_parser.target_col
                not in self.datasets[ns_parser.target_dataset].columns
            ):
                console.print(
                    f"[red]The target column {ns_parser.target_col} does not exist in dataframe.\n[/red]"
                )
                return

            rnn_view.display_rnn_forecast(
                data=self.datasets[ns_parser.target_dataset],
                ticker_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_col=ns_parser.target_col,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.forecast_horizon,
                model_type=ns_parser.model_type,
                hidden_dim=ns_parser.hidden_dim,
                dropout=ns_parser.dropout,
                batch_size=ns_parser.batch_size,
                n_epochs=ns_parser.n_epochs,
                learning_rate=ns_parser.learning_rate,
                model_save_name=ns_parser.model_save_name,
                training_length=ns_parser.training_length,
                input_chunk_size=ns_parser.input_chunk_size,
                force_reset=ns_parser.force_reset,
                save_checkpoints=ns_parser.save_checkpoints,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_nbeats(self, other_args: List[str]):
        """Process NBEATS command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="rnn",
            description="""
                Perform NBEATS forecast (Neural Bayesian Estimation of Time Series).
            """,
        )
        parser.add_argument(
            "--target_dataset",
            type=str,
            choices=self.files,
            dest="target_dataset",
            help="Dataset name",
        )
        parser.add_argument(
            "-n",
            "--n_days",
            action="store",
            dest="n_days",
            type=check_positive,
            default=5,
            help="prediction days.",
        )
        parser.add_argument(
            "--target_forecast_column",
            action="store",
            dest="target_col",
            default="close",
            type=str,
            help="target column.",
        )
        parser.add_argument(
            "--past_covariates",
            action="store",
            dest="past_covariates",
            default="",
            type=str,
            help="Past covariates(columns/features) in same dataset that may effect price. Comma seperated.",
        )
        parser.add_argument(
            "--train_split",
            action="store",
            dest="train_split",
            default=0.85,
            type=check_positive_float,
            help="Start point for rolling training and forecast window. 0.0-1.0",
        )
        parser.add_argument(
            "--forecasthorizon",
            action="store",
            dest="forecast_horizon",
            default=7,
            help="Days/Points to forecast when training and performing historical back-testing",
        )
        # NBEATS Hyperparameters
        parser.add_argument(
            "--input_chunk_length",
            action="store",
            dest="input_chunk_length",
            default=30,
            type=check_positive,
            help="The length of the input sequence fed to the model.",
        )
        parser.add_argument(
            "--output_chunk_length",
            action="store",
            dest="output_chunk_length",
            default=7,
            type=check_positive,
            help="The length of the forecast of the model.",
        )
        parser.add_argument(
            "--num_stacks",
            action="store",
            dest="num_stacks",
            default=10,
            type=check_positive_float,
            help="The number of stacks that make up the whole model.",
        )
        parser.add_argument(
            "--num_blocks",
            action="store",
            dest="num_blocks",
            default=3,
            type=check_positive,
            help="The number of blocks making up every stack.",
        )
        parser.add_argument(
            "--num_layers",
            action="store",
            dest="num_layers",
            default=4,
            type=check_positive,
            help="he number of fully connected layers preceding the final forking layers in each block of every stack.",
        )
        parser.add_argument(
            "--layer_widths",
            action="store",
            dest="layer_widths",
            default=512,
            type=check_positive,
            help="Determines the number of neurons that make up each fully connected layer in each block of every stack",
        )
        parser.add_argument(
            "--batch_size",
            action="store",
            dest="batch_size",
            default=800,
            type=check_positive,
            help="Number of time series (input and output sequences) used in each training pass.",
        )
        parser.add_argument(
            "--n_epochs",
            action="store",
            dest="n_epochs",
            default=100,
            type=check_positive,
            help="Number of epochs over which to train the model.",
        )
        parser.add_argument(
            "--learning_rate",
            action="store",
            dest="learning_rate",
            default=1e-3,
            type=check_positive_float,
            help="Learning rate during training.",
        )
        parser.add_argument(
            "--model_save_name",
            type=str,
            action="store",
            dest="model_save_name",
            default="nbeats_model",
            help="Name of the model to save.",
        )
        parser.add_argument(
            "--force_reset",
            action="store",
            dest="force_reset",
            default=True,
            type=bool,
            help="If set to True, any previously-existing model with the same name will be reset (all checkpoints will be discarded).",
        )
        parser.add_argument(
            "--save_checkpoints",
            action="store",
            dest="save_checkpoints",
            default=True,
            type=bool,
            help="Whether or not to automatically save the untrained model and checkpoints from training.",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )

        if ns_parser:
            # check proper file name is provided
            if not ns_parser.target_dataset:
                console.print("[red]Please enter valid dataset.\n[/red]")
                return

            # must check that target col is within target series
            if (
                ns_parser.target_col
                not in self.datasets[ns_parser.target_dataset].columns
            ):
                console.print(
                    f"[red]The target column {ns_parser.target_col} does not exist in dataframe.\n[/red]"
                )
                return

            NBEATS_view.display_nbeats_forecast(
                data=self.datasets[ns_parser.target_dataset],
                ticker_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_col=ns_parser.target_col,
                past_covariates=ns_parser.past_covariates,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.forecast_horizon,
                input_chunk_length=ns_parser.input_chunk_length,
                output_chunk_length=ns_parser.output_chunk_length,
                num_stacks=ns_parser.num_stacks,
                num_blocks=ns_parser.num_blocks,
                num_layers=ns_parser.num_layers,
                layer_widths=ns_parser.layer_widths,
                batch_size=ns_parser.batch_size,
                n_epochs=ns_parser.n_epochs,
                learning_rate=ns_parser.learning_rate,
                model_save_name=ns_parser.model_save_name,
                force_reset=ns_parser.force_reset,
                save_checkpoints=ns_parser.save_checkpoints,
                export=ns_parser.export,
            )
