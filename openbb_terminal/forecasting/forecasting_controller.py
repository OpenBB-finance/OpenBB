"""Forecasting Controller Module"""
__docformat__ = "numpy"

# pylint: disable=too-many-lines, too-many-branches, inconsistent-return-statements
# pylint: disable=too-many-arguments, R0904

import argparse
import logging
from itertools import chain
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

import torch
import darts
import pandas as pd
import psutil
from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    check_positive,
    check_positive_float,
    NO_EXPORT,
    EXPORT_ONLY_FIGURES_ALLOWED,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    export_data,
    log_and_raise,
    get_next_stock_market_days,
    valid_date,
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
    linregr_view,
    nbeats_view,
    regr_view,
    tcn_view,
    theta_view,
    rnn_view,
    brnn_view,
    tft_view,
    arima_view,
    arima_model,
    knn_view,
    helpers,
    trans_view,
    mc_model,
    mc_view,
)

logger = logging.getLogger(__name__)
empty_df = pd.DataFrame()

# pylint: disable=R0902


def check_greater_than_one(value) -> int:
    """Argparse type to check positive int above 1"""
    new_value = int(value)
    if new_value <= 1:
        log_and_raise(
            argparse.ArgumentTypeError(
                f"{value} is an invalid positive int value. Must be greater than 1."
            )
        )
    return new_value


class ForecastingController(BaseController):
    """Forecasting class"""

    CHOICES_COMMANDS: List[str] = [
        "load",
        "show",
        "plot",
        "clean",
        "combine",
        "desc",
        "corr",
        "rename",
        "delete",
        "export",
        "ema",
        "sto",
        "rsi",
        "roc",
        "mom",
        "delta",
        "atr",
        "signal",
        "expo",
        "theta",
        "rnn",
        "brnn",
        "nbeats",
        "tcn",
        "regr",
        "linregr",
        "trans",
        "tft",
        # "arima",
        "knn",
        "mc",
        "season",
    ]
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
    disclaimer = """
    All models are for educational purposes only. The techniques available in this menu are not
    fine tuned or guaranteed to work. Backtesting results is not a guarantee of future accuracy.
    Investing involves monetary risk that OpenBB does not take a role in. Please research any prediction techniques
    fully before attempting to use. OpenBB is not liable for any loss or damages."""

    PATH = "/forecasting/"

    loaded_dataset_cols = "\n"
    list_dataset_cols: List = list()

    def __init__(
        self, ticker: str = "", data: pd.DataFrame = empty_df, queue: List[str] = None
    ):
        """Constructor"""
        super().__init__(queue)
        self.files: List[str] = list()
        self.datasets: Dict[str, pd.DataFrame] = dict()

        if ticker and not data.empty:
            # data["date"] = data.index
            data = data.reset_index()  # convert date from index to column
            data.columns = data.columns.map(lambda x: x.lower().replace(" ", "_"))

            self.files.append(ticker)
            self.datasets[ticker] = data
            self.loaded_dataset_cols = "\n"

            self.loaded_dataset_cols += (
                f"  {ticker} {(20 - len(ticker)) * ' '}: "
                f"{', '.join(data.columns)}\n"
            )

            for col in data.columns:
                self.list_dataset_cols.append(f"{ticker}.{col}")

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
        for file_type in self.file_types:
            print(list(Path("exports").rglob(f"*.{file_type}")))
        self.DATA_FILES = {
            filepath.name: filepath
            for file_type in self.file_types
            for filepath in chain(
                Path("exports").rglob(f"*.{file_type}"),
                Path("custom_imports").rglob(f"*.{file_type}"),
            )
            if filepath.is_file()
        }

        # setting device on GPU if available, else CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.comp_ram = f"{round(psutil.virtual_memory().total / (1024.0 ** 3),2)}G"
        self.rec_data_size = f"{(psutil.virtual_memory().total / (1024.0 ** 3))//3}G"
        self.torch_version = torch.__version__
        self.darts_version = darts.__version__

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["load"] = {c: None for c in self.DATA_FILES.keys()}
            choices["show"] = {c: None for c in self.files}

            for feature in ["export", "show"]:
                choices[feature] = {c: None for c in self.files}

            for feature in ["plot"]:
                choices[feature] = dict()

            self.choices = choices

            # To link to the support HTML
            choices["support"] = self.SUPPORT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def update_runtime_choices(self):
        if session and obbff.USE_PROMPT_TOOLKIT:
            dataset_columns = {
                f"{dataset}.{column}": {column: None, dataset: None}
                for dataset, dataframe in self.datasets.items()
                for column in dataframe.columns
            }

            for feature in [
                "plot",
                "delete",
            ]:
                self.choices[feature] = dataset_columns

            for feature in [
                "export",
                "show",
                "clean",
                "desc",
                "corr",
                "ema",
                "sto",
                "rsi",
                "roc",
                "mom",
                "delta",
                "atr",
                "signal",
                # "index",
                # "remove",
                "combine",
                "rename",
                "expo",
                "theta",
                "rnn",
                "brnn",
                "nbeats",
                "tcn",
                "regr",
                "linregr",
                "trans",
                "tft",
                "knn",
                "mc",
                "season",
            ]:
                self.choices[feature] = {c: None for c in self.files}

            pairs_timeseries = list()
            for dataset_col in list(dataset_columns.keys()):
                pairs_timeseries += [
                    f"{dataset_col},{dataset_col2}"
                    for dataset_col2 in list(dataset_columns.keys())
                    if dataset_col != dataset_col2
                ]

            self.completer = NestedCompleter.from_nested_dict(self.choices)

    def refresh_datasets_on_menu(self):
        """Refresh datasets on menu with new columns when adding new features"""

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

    def print_help(self):
        """Print help"""
        mt = MenuText("forecasting/")
        mt.add_param("_disclaimer_", self.disclaimer)
        mt.add_raw("\n")
        mt.add_param("_comp_device", self.device.upper())
        mt.add_param("_comp_ram", self.comp_ram)
        mt.add_param("_rec_data_size", self.rec_data_size)
        mt.add_param("_torch_ver", self.torch_version)
        mt.add_param("_darts_ver", self.darts_version)
        mt.add_raw("\n")
        mt.add_param(
            "_data_loc",
            f"\n\t{obbff.EXPORT_FOLDER_PATH}\n\t{Path('custom_imports').resolve()}/forecasting",
        )
        mt.add_raw("\n")
        mt.add_cmd("load")
        mt.add_raw("\n")
        mt.add_param("_loaded", self.loaded_dataset_cols)
        mt.add_info("_exploration_")
        mt.add_cmd("show", "", self.files)
        mt.add_cmd("plot", "", self.files)
        mt.add_cmd("clean", "", self.files)
        mt.add_cmd("combine", "", self.files)
        mt.add_cmd("desc", "", self.files)
        mt.add_cmd("corr", "", self.files)
        mt.add_cmd("season", "", self.files)
        mt.add_cmd("delete", "", self.files)
        mt.add_cmd("rename", "", self.files)
        mt.add_cmd("export", "", self.files)
        mt.add_info("_feateng_")
        mt.add_cmd("ema", "", self.files)
        mt.add_cmd("sto", "", self.files)
        mt.add_cmd("rsi", "", self.files)
        mt.add_cmd("roc", "", self.files)
        mt.add_cmd("mom", "", self.files)
        mt.add_cmd("delta", "", self.files)
        mt.add_cmd("atr", "", self.files)
        mt.add_cmd("signal", "", self.files)
        mt.add_info("_tsforecasting_")
        # mt.add_cmd("arima", "", self.files)
        mt.add_cmd("knn", "", self.files)
        mt.add_cmd("mc", "", self.files)
        mt.add_cmd("expo", "", self.files)
        mt.add_cmd("theta", "", self.files)
        mt.add_cmd("linregr", "", self.files)
        mt.add_cmd("regr", "", self.files)
        mt.add_cmd("rnn", "", self.files)
        mt.add_cmd("brnn", "", self.files)
        mt.add_cmd("nbeats", "", self.files)
        mt.add_cmd("tcn", "", self.files)
        mt.add_cmd("trans", "", self.files)
        mt.add_cmd("tft", "", self.files)
        # mt.add_info("_comingsoon_")

        console.print(text=mt.menu_text, menu="Forecasting")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.files:
            load_files = [f"load {file} --search-file-types" for file in self.files]
            return ["forecasting"] + load_files
        return []

    def parse_known_args_and_warn(
        self,
        parser: argparse.ArgumentParser,
        other_args: List[str],
        export_allowed: int = NO_EXPORT,
        raw: bool = False,
        limit: int = 0,
        # Custom items
        target_dataset: bool = False,
        target_column: bool = False,
        period: Optional[int] = None,
        n_days: bool = False,
        forecast_horizon: bool = False,
        seasonal: Optional[str] = None,
        periods: bool = False,
        window: bool = False,
        train_split: bool = False,
        input_chunk_length: bool = False,
        output_chunk_length: bool = False,
        force_reset: bool = False,
        save_checkpoints: bool = False,
        model_save_name: Optional[str] = None,
        n_epochs: bool = False,
        model_type: bool = False,
        dropout: Optional[float] = None,
        batch_size: Optional[int] = None,
        learning_rate: bool = False,
        past_covariates: bool = False,
        lags: bool = False,
        hidden_size: int = None,
        n_jumps: bool = False,
        end: bool = False,
        residuals: bool = False,
        forecast_only: bool = False,
    ):
        if hidden_size:
            parser.add_argument(
                "--hidden-size",
                action="store",
                dest="hidden_size",
                default=hidden_size,
                type=check_positive,
                help="Size for feature maps for each hidden RNN layer (h_n)",
            )
        if past_covariates:
            parser.add_argument(
                "--past-covariates",
                action="store",
                dest="past_covariates",
                default=None,
                type=str,
                help="Past covariates(columns/features) in same dataset. Comma separated.",
            )
        if target_dataset:
            parser.add_argument(
                "-d",
                "--target-dataset",
                help="The name of the dataset you want to select",
                dest="target_dataset",
                type=str,
                choices=list(self.datasets.keys()),
            )
        if target_column:
            parser.add_argument(
                "-c",
                "--target-column",
                help="The name of the specific column you want to use",
                dest="target_column",
                type=str,
                default="close",
            )
        if period is not None:
            parser.add_argument(
                "--period",
                help="The period to use",
                dest="period",
                type=check_greater_than_one,
                default=period,
            )
        if n_days:
            parser.add_argument(
                "-n",
                "--n-days",
                action="store",
                dest="n_days",
                type=check_greater_than_one,
                default=5,
                help="prediction days.",
            )
        if forecast_horizon:
            parser.add_argument(
                "--forecast-horizon",
                action="store",
                dest="forecast_horizon",
                default=5,
                type=check_greater_than_one,
                help="Days/Points to forecast for historical back-testing",
            )
        if seasonal is not None:
            parser.add_argument(
                "-s",
                "--seasonal",
                action="store",
                dest="seasonal",
                choices=expo_model.SEASONS,
                default=seasonal,
                help="Seasonality: N: None, A: Additive, M: Multiplicative.",
            )
        if periods:
            parser.add_argument(
                "-p",
                "--periods",
                action="store",
                dest="seasonal_periods",
                type=check_positive,
                default=7,
                help="Seasonal periods: 4: Quarterly, 7: Daily",
            )
        if window:
            parser.add_argument(
                "-w",
                "--window",
                action="store",
                dest="start_window",
                default=0.85,
                help="Start point for rolling training and forecast window. 0.0-1.0",
            )
        if train_split:
            parser.add_argument(
                "-t",
                "--train-split",
                action="store",
                dest="train_split",
                default=0.85,
                type=check_positive_float,
                help="Start point for rolling training and forecast window. 0.0-1.0",
            )
        if input_chunk_length:
            parser.add_argument(
                "-i",
                "--input-chunk-length",
                action="store",
                dest="input_chunk_length",
                default=14,
                type=check_positive,
                help="Number of past time steps for forecasting module at prediction time.",
            )
        if output_chunk_length:
            parser.add_argument(
                "-o",
                "--output-chunk-length",
                action="store",
                dest="output_chunk_length",
                default=5,
                type=check_positive,
                help="The length of the forecast of the model.",
            )
        if force_reset:
            parser.add_argument(
                "--force-reset",
                action="store",
                dest="force_reset",
                default=True,
                type=bool,
                help="""If set to True, any previously-existing model with the same name will be reset
                        (all checkpoints will be discarded).""",
            )
        if save_checkpoints:
            parser.add_argument(
                "--save-checkpoints",
                action="store",
                dest="save_checkpoints",
                default=True,
                type=bool,
                help="Whether to automatically save the untrained model and checkpoints.",
            )
        if model_save_name is not None:
            parser.add_argument(
                "--model-save-name",
                type=str,
                action="store",
                dest="model_save_name",
                default=model_save_name,
                help="Name of the model to save.",
            )
        if n_epochs:
            parser.add_argument(
                "--n-epochs",
                action="store",
                dest="n_epochs",
                default=300,
                type=check_positive,
                help="Number of epochs over which to train the model.",
            )
        if model_type:
            parser.add_argument(
                "--model-type",
                type=str,
                action="store",
                dest="model_type",
                default="LSTM",
                help='Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU")',
            )
        if dropout is not None:
            parser.add_argument(
                "--dropout",
                action="store",
                dest="dropout",
                default=dropout,
                type=check_positive_float,
                help="Fraction of neurons afected by Dropout.",
            )
        if batch_size is not None:
            parser.add_argument(
                "--batch-size",
                action="store",
                dest="batch_size",
                default=batch_size,
                type=check_positive,
                help="Number of time series (input and output) used in each training pass",
            )
        if end:
            parser.add_argument(
                "-e",
                "--end",
                action="store",
                type=valid_date,
                dest="s_end_date",
                default=None,
                help="The end date (format YYYY-MM-DD) to select for testing",
            )
        if learning_rate:
            parser.add_argument(
                "--learning-rate",
                action="store",
                dest="learning_rate",
                default=1e-3,
                type=check_positive_float,
                help="Learning rate during training.",
            )
        if n_jumps:
            parser.add_argument(
                "-j",
                "--jumps",
                action="store",
                dest="n_jumps",
                type=check_positive,
                default=1,
                help="number of jumps in training data.",
            )
        if lags:
            parser.add_argument(
                "--lags",
                action="store",
                dest="lags",
                type=check_greater_than_one,
                default=72,
                help="Lagged target values used to predict the next time step.",
            )
        if residuals:
            parser.add_argument(
                "--residuals",
                help="Show the residuals for the model.",
                action="store_true",
                default=False,
                dest="residuals",
            )
        if forecast_only:
            parser.add_argument(
                "-f",
                "--forecast_only",
                help="Do not plot the hisotorical data without forecasts.",
                action="store_true",
                default=False,
                dest="forecast_only",
            )
            # if user does not put in --target-dataset
        return super().parse_known_args_and_warn(
            parser, other_args, export_allowed, raw, limit
        )

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
        parser.add_argument(
            "--search-file-types",
            action="store_true",
            default=False,
            dest="search_file_types",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

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

                data = forecasting_model.load(
                    file, self.file_types, self.DATA_FILES, ns_parser.search_file_types
                )

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
        ns_parser = self.parse_known_args_and_warn(
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

                # print shape of dataframe
                console.print(
                    f"[green]{name} has following shape (rowxcolumn): {df.shape}[/green]"
                )
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

    @log_start_end(log=logger)
    def call_rename(self, other_args: List[str]):
        """Process rename"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rename",
            description="The column you want to rename from a dataset.",
        )
        parser.add_argument(
            "-d",
            "--dataset",
            help="Dataset that will get a column renamed",
            dest="dataset",
            choices=self.choices["rename"],
            type=str,
        )
        parser.add_argument(
            "-o",
            "--oldcol",
            help="Old column from dataset to be renamed",
            dest="oldcol",
            type=str,
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-n",
            "--newcol",
            help="New column from dataset to be renamed",
            dest="newcol",
            type=str,
            required="-h" not in other_args,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-d")
        ns_parser = self.parse_known_args_and_warn(parser, other_args, NO_EXPORT)

        if ns_parser:
            dataset = ns_parser.dataset
            column_old = ns_parser.oldcol
            column_new = ns_parser.newcol

            if dataset not in self.datasets:
                console.print(
                    f"Not able to find the dataset {dataset}. Please choose one of "
                    f"the following: {', '.join(self.datasets)}"
                )
            elif column_old not in self.datasets[dataset]:
                console.print(
                    f"Not able to find the column {column_old}. Please choose one of "
                    f"the following: {', '.join(self.datasets[dataset].columns)}"
                )
            else:
                self.datasets[dataset] = self.datasets[dataset].rename(
                    columns={column_old: column_new}
                )

            self.update_runtime_choices()

        console.print()

    # Show selected dataframe on console
    @log_start_end(log=logger)
    def call_desc(self, other_args: List[str]):
        """Process descriptive stats command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="desc",
            description="Show descriptive statistics of a dataset",
        )

        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_RAW_DATA_ALLOWED,
            target_dataset=True,
        )

        if ns_parser:
            # check proper file name is provided
            if not ns_parser.target_dataset:
                console.print("[red]Please enter valid dataset.\n[/red]")
                return

            df = self.datasets[ns_parser.target_dataset]

            print_rich_table(
                df.describe(),
                headers=list(df.describe().columns),
                show_index=True,
                title=f"Showing Descriptive Statistics for Dataset {ns_parser.target_dataset}",
            )

            export_data(
                ns_parser.export,
                os.path.dirname(os.path.abspath(__file__)),
                f"{ns_parser.target_dataset}_show",
            )

    @log_start_end(log=logger)
    def call_plot(self, other_args: List[str]):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="Plot data based on the index",
        )
        parser.add_argument(
            "-v",
            "--values",
            help="Dataset.column values to be displayed in a plot",
            dest="values",
            type=check_list_values(self.choices["plot"]),
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if not ns_parser:
            return

        if not ns_parser.values:
            console.print("[red]Please enter valid dataset.\n[/red]")
            return

        data: Dict = {}
        for datasetcol in ns_parser.values:
            dataset, col = datasetcol.split(".")
            data[datasetcol] = self.datasets[dataset][col]

        forecasting_view.display_plot(
            data,
            ns_parser.export,
        )

    @log_start_end(log=logger)
    def call_season(self, other_args: List[str]):
        """Process season command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="season",
            description="The seasonality for a given column",
        )
        parser.add_argument(
            "-v",
            "--values",
            help="Dataset.column values to be displayed in a plot",
            dest="values",
            type=str,
        )
        parser.add_argument(
            "-m",
            help="A time lag to highlight on the plot",
            dest="m",
            type=int,
            default=None,
        )
        parser.add_argument(
            "--max_lag",
            help="The maximal lag order to consider",
            dest="max_lag",
            type=int,
            default=24,
        )
        parser.add_argument(
            "-a",
            "--alpha",
            help="The confidence interval to display",
            dest="alpha",
            type=float,
            default=0.05,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )

        if not ns_parser:
            return

        if not ns_parser.values:
            console.print("[red]Please enter valid dataset.\n[/red]")
            return

        try:
            dataset, col = ns_parser.values.split(".")
            data = self.datasets[dataset]
        except ValueError:
            console.print("[red]Please enter 'dataset'.'column'.[/red]\n")
            return

        forecasting_view.display_seasonality(
            data=data,
            column=col,
            export=ns_parser.export,
            m=ns_parser.m,
            max_lag=ns_parser.max_lag,
            alpha=ns_parser.alpha,
        )

    @log_start_end(log=logger)
    def call_corr(self, other_args: List[str]):
        """Process correlation command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="corr",
            description="Plot correlation coefficients.",
        )

        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_FIGURES_ALLOWED,
            target_dataset=True,
        )

        if ns_parser:
            # check proper file name is provided
            if not ns_parser.target_dataset:
                console.print("[red]Please enter valid dataset.\n[/red]")
                return

            data = self.datasets[ns_parser.target_dataset]

            forecasting_view.display_corr(
                data,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_combine(self, other_args: List[str]):
        """Process combine"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="combine",
            description="The columns you want to add to a dataset. The first argument is the dataset to add columns in"
            "and the remaining could be: <datasetX.column2>,<datasetY.column3>",
        )
        parser.add_argument(
            "--dataset",
            help="Dataset to add columns to",
            dest="dataset",
            choices=self.choices["combine"],
        )
        parser.add_argument(
            "-c",
            "--columns",
            help="The columns we want to add <dataset.column>,<datasetb.column2>",
            dest="columns",
            type=check_list_values(self.choices["delete"]),
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")
        ns_parser = self.parse_known_args_and_warn(parser, other_args, NO_EXPORT)

        if ns_parser:
            if ns_parser.dataset not in self.datasets:
                console.print(
                    f"Not able to find the dataset {ns_parser.dataset}. Please choose one of "
                    f"the following: {', '.join(self.datasets)}"
                )
                return

            data = self.datasets[ns_parser.dataset]

            for option in ns_parser.columns:
                dataset, column = option.split(".")

                if dataset not in self.datasets:
                    console.print(
                        f"Not able to find the dataset {dataset}. Please choose one of "
                        f"the following: {', '.join(self.datasets)}"
                    )
                elif column not in self.datasets[dataset]:
                    console.print(
                        f"Not able to find the column {column}. Please choose one of "
                        f"the following: {', '.join(self.datasets[dataset].columns)}"
                    )
                else:
                    data[f"{dataset}_{column}"] = self.datasets[dataset][column]

            self.update_runtime_choices()
        console.print()

    @log_start_end(log=logger)
    def call_clean(self, other_args: List[str]):
        """Process clean"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="clean",
            description="Clean a dataset by filling and dropping NaN values.",
        )
        parser.add_argument(
            "-f",
            "--fill",
            help="The method of filling NaNs. This has options to fill rows (rfill, rbfill, rffill) or fill "
            "columns (cfill, cbfill, cffill). Furthermore, it has the option to forward fill and backward fill "
            "(up to --limit) which refer to how many rows/columns can be set equal to the last non-NaN value",
            dest="fill",
            choices=["rfill", "cfill", "rbfill", "cbfill", "rffill", "bffill"],
            default="",
        )
        parser.add_argument(
            "--drop",
            help="The method of dropping NaNs. This either has the option rdrop (drop rows that contain NaNs) "
            "or cdrop (drop columns that contain NaNs)",
            dest="drop",
            choices=["rdrop", "cdrop"],
            default="",
        )
        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
            target_dataset=True,
            limit=5,
        )
        print(ns_parser)
        if ns_parser:
            # check proper file name is provided
            if not ns_parser.target_dataset:
                console.print("[red]Please enter valid dataset.\n[/red]")
                return

            (
                self.datasets[ns_parser.target_dataset],
                clean_status,
            ) = forecasting_model.clean(
                self.datasets[ns_parser.target_dataset],
                ns_parser.fill,
                ns_parser.drop,
                ns_parser.limit,
            )
            if not clean_status:
                console.print(
                    f"Successfully cleaned '{ns_parser.target_dataset}' dataset"
                )
            else:
                console.print(f"[red]{ns_parser.name} still contains NaNs.[/red]")

        console.print()

    @log_start_end(log=logger)
    def call_ema(self, other_args: List[str]):
        """Process EMA"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ema",
            description="Add exponential moving average to dataset based on specific column.",
        )

        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
            period=10,
            target_dataset=True,
            target_column=True,
        )
        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            self.datasets[ns_parser.target_dataset] = forecasting_model.add_ema(
                self.datasets[ns_parser.target_dataset],
                ns_parser.target_column,
                ns_parser.period,
            )
            console.print(
                f"Successfully added 'EMA_{ns_parser.period}' to '{ns_parser.target_dataset}' dataset"
            )

            # update forecast menu with new column on modified dataset
            self.refresh_datasets_on_menu()

        self.update_runtime_choices()
        console.print()

    @log_start_end(log=logger)
    def call_sto(self, other_args: List[str]):
        """Process Stoch Oscill"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sto",
            description="Add in Stochastic Oscillator %K and %D",
        )
        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, NO_EXPORT, limit=5, period=10, target_dataset=True
        )
        if ns_parser:
            # check proper file name is provided
            if not ns_parser.target_dataset:
                console.print("[red]Please enter valid dataset.\n[/red]")
                return

            self.datasets[ns_parser.target_dataset] = forecasting_model.add_sto(
                self.datasets[ns_parser.target_dataset],
                ns_parser.period,
            )
            console.print(
                f"Successfully added 'STOK&D_{ns_parser.period}' to '{ns_parser.target_dataset}' dataset"
            )

            # update forecast menu with new column on modified dataset
            self.refresh_datasets_on_menu()

        self.update_runtime_choices()
        console.print()

    @log_start_end(log=logger)
    def call_delete(self, other_args: List[str]):
        """Process delete"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="delete",
            description="The column you want to delete from a dataset.",
        )
        parser.add_argument(
            "--delete",
            help="The columns you want to delete from a dataset. Use format: <dataset.column> or"
            " multiple with <dataset.column>,<datasetb.column2>",
            dest="delete",
            type=check_list_values(self.choices["delete"]),
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--delete")
        ns_parser = self.parse_known_args_and_warn(parser, other_args, NO_EXPORT)

        if ns_parser:
            for option in ns_parser.delete:
                dataset, column = option.split(".")

                if dataset not in self.datasets:
                    console.print(
                        f"Not able to find the dataset {dataset}. Please choose one of "
                        f"the following: {', '.join(self.datasets)}"
                    )
                elif column not in self.datasets[dataset]:
                    console.print(
                        f"Not able to find the column {column}. Please choose one of "
                        f"the following: {', '.join(self.datasets[dataset].columns)}"
                    )
                else:
                    del self.datasets[dataset][column]

            self.update_runtime_choices()
        console.print()

    @log_start_end(log=logger)
    def call_rsi(self, other_args: List[str]):
        """Process RSI"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rsi",
            description="Add rsi to dataset based on specific column.",
        )
        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
            target_dataset=True,
            target_column=True,
            period=10,
        )
        if ns_parser:
            # check proper file name is provided
            if not ns_parser.target_dataset:
                console.print("[red]Please enter valid dataset.\n[/red]")
                return

            self.datasets[ns_parser.target_dataset] = forecasting_model.add_rsi(
                self.datasets[ns_parser.target_dataset],
                ns_parser.target_column,
                ns_parser.period,
            )
            console.print(
                f"Successfully added 'RSI_{ns_parser.period}' to '{ns_parser.target_dataset}' dataset"
            )

            # update forecast menu with new column on modified dataset
            self.refresh_datasets_on_menu()

        self.update_runtime_choices()
        console.print()

    @log_start_end(log=logger)
    def call_roc(self, other_args: List[str]):
        """Process ROC"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="roc",
            description="Add rate of change to dataset based on specific column.",
        )
        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
            target_dataset=True,
            target_column=True,
            period=10,
        )
        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            self.datasets[ns_parser.target_dataset] = forecasting_model.add_roc(
                self.datasets[ns_parser.target_dataset],
                ns_parser.target_column,
                ns_parser.period,
            )
            console.print(
                f"Successfully added 'ROC_{ns_parser.period}' to '{ns_parser.target_dataset}' dataset"
            )

            # update forecast menu with new column on modified dataset
            self.refresh_datasets_on_menu()

        self.update_runtime_choices()
        console.print()

    @log_start_end(log=logger)
    def call_mom(self, other_args: List[str]):
        """Process Momentum"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="mom",
            description="Add momentum to dataset based on specific column.",
        )
        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
            target_dataset=True,
            target_column=True,
            period=10,
        )
        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            self.datasets[ns_parser.target_dataset] = forecasting_model.add_momentum(
                self.datasets[ns_parser.target_dataset],
                ns_parser.target_column,
                ns_parser.period,
            )
            console.print(
                f"Successfully added 'Momentum_{ns_parser.period}' to '{ns_parser.target_dataset}' dataset"
            )

            # update forecast menu with new column on modified dataset
            self.refresh_datasets_on_menu()

        self.update_runtime_choices()
        console.print()

    @log_start_end(log=logger)
    def call_delta(self, other_args: List[str]):
        """Process %Change (Delta)"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="delta",
            description="Add %Change (Delta) to dataset based on specific column.",
        )

        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
            target_dataset=True,
            target_column=True,
        )
        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            self.datasets[ns_parser.target_dataset] = forecasting_model.add_delta(
                self.datasets[ns_parser.target_dataset], ns_parser.target_column
            )
            console.print(
                f"Successfully added 'Delta_{ns_parser.target_column}' to '{ns_parser.target_dataset}' dataset"
            )

            # update forecast menu with new column on modified dataset
            self.refresh_datasets_on_menu()

        self.update_runtime_choices()
        console.print()

    @log_start_end(log=logger)
    def call_atr(self, other_args: List[str]):
        """Process Average True Range"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="atr",
            description="Add Average True Range to dataset of specific stock ticker.",
        )

        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
            target_dataset=True,
            target_column=True,
        )
        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            check = False
            self.datasets[ns_parser.target_dataset], check = forecasting_model.add_atr(
                self.datasets[ns_parser.target_dataset]
            )
            if check:
                console.print(
                    f"Successfully added 'Average True Range' to '{ns_parser.target_dataset}' dataset"
                )
            else:
                console.print(
                    "Could not add 'Average True Range' as it does not have one/all specific columns (low/close/high)"
                )

            # update forecast menu with new column on modified dataset
            self.refresh_datasets_on_menu()

        self.update_runtime_choices()
        console.print()

    @log_start_end(log=logger)
    def call_signal(self, other_args: List[str]):
        """Process Price Signal"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="signal",
            description="""Add price signal to dataset based on closing price.
            1 if the signal is that short term price will go up as compared to the long term.
            0 if the signal is that short term price will go down as compared to the long term.
            """,
        )
        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
            target_dataset=True,
            target_column=True,
        )
        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            self.datasets[ns_parser.target_dataset] = forecasting_model.add_signal(
                self.datasets[ns_parser.target_dataset]
            )
            console.print(
                f"Successfully added 'Price Signal' to '{ns_parser.target_dataset}' dataset"
            )

            # update forecast menu with new column on modified dataset
            self.refresh_datasets_on_menu()

        self.update_runtime_choices()
        console.print()

    @log_start_end(log=logger)
    def call_export(self, other_args: List[str]):
        """Process export command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="export",
            description="Export dataset to Excel",
        )
        parser.add_argument(
            "-t",
            "--type",
            help="The file type you wish to export to",
            dest="type",
            choices=self.file_types,
            type=str,
            default="xlsx",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=NO_EXPORT,
            target_dataset=True,
        )

        if not helpers.check_parser_input(ns_parser, self.datasets, "ignore_column"):
            return

        export_data(
            ns_parser.type,
            os.path.dirname(os.path.abspath(__file__)),
            ns_parser.target_dataset,
            self.datasets[ns_parser.target_dataset],
        )

        console.print()

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
            "--trend",
            action="store",
            dest="trend",
            choices=expo_model.TRENDS,
            default="A",
            help="Trend: N: None, A: Additive, M: Multiplicative.",
        )
        parser.add_argument(
            "--dampen",
            action="store",
            dest="dampen",
            default="F",
            help="Dampening",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
            target_dataset=True,
            target_column=True,
            n_days=True,
            forecast_horizon=True,
            seasonal="A",
            periods=True,
            window=True,
            residuals=True,
            forecast_only=True,
        )
        # TODO Convert this to multi series
        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            expo_view.display_expo_forecast(
                data=self.datasets[ns_parser.target_dataset],
                ticker_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_col=ns_parser.target_column,
                trend=ns_parser.trend,
                seasonal=ns_parser.seasonal,
                seasonal_periods=ns_parser.seasonal_periods,
                dampen=ns_parser.dampen,
                start_window=ns_parser.start_window,
                forecast_horizon=ns_parser.forecast_horizon,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
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
        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
            target_dataset=True,
            n_days=True,
            target_column=True,
            seasonal="M",
            periods=True,
            window=True,
            forecast_horizon=True,
            residuals=True,
            forecast_only=True,
        )

        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            theta_view.display_theta_forecast(
                data=self.datasets[ns_parser.target_dataset],
                ticker_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_col=ns_parser.target_column,
                seasonal=ns_parser.seasonal,
                seasonal_periods=ns_parser.seasonal_periods,
                start_window=ns_parser.start_window,
                forecast_horizon=ns_parser.forecast_horizon,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
            )

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
        # RNN Hyperparameters
        parser.add_argument(
            "--hidden-dim",
            action="store",
            dest="hidden_dim",
            default=20,
            type=check_positive,
            help="Size for feature maps for each hidden RNN layer (h_n)",
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

        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
            target_dataset=True,
            n_days=True,
            target_column=True,
            forecast_horizon=True,
            train_split=True,
            input_chunk_length=True,
            force_reset=True,
            save_checkpoints=True,
            model_save_name="rnn_model",
            n_epochs=True,
            model_type=True,
            dropout=0,
            batch_size=32,
            learning_rate=True,
            residuals=True,
            forecast_only=True,
        )

        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            rnn_view.display_rnn_forecast(
                data=self.datasets[ns_parser.target_dataset],
                ticker_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_col=ns_parser.target_column,
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
                input_chunk_size=ns_parser.input_chunk_length,
                force_reset=ns_parser.force_reset,
                save_checkpoints=ns_parser.save_checkpoints,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
            )

    @log_start_end(log=logger)
    def call_nbeats(self, other_args: List[str]):
        """Process NBEATS command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="nbeats",
            description="""
                Perform NBEATS forecast (Neural Bayesian Estimation of Time Series).
            """,
        )
        # NBEATS Hyperparameters
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
            help="""The number of fully connected layers preceding the final forking layers
            in each block of every stack.""",
        )
        parser.add_argument(
            "--layer_widths",
            action="store",
            dest="layer_widths",
            default=512,
            type=check_positive,
            help="""Determines the number of neurons that make up each fully connected layer
                in each block of every stack""",
        )

        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
            target_dataset=True,
            n_days=True,
            target_column=True,
            train_split=True,
            forecast_horizon=True,
            input_chunk_length=True,
            output_chunk_length=True,
            save_checkpoints=True,
            force_reset=True,
            model_save_name="nbeats_model",
            learning_rate=True,
            n_epochs=True,
            batch_size=800,
            past_covariates=True,
            residuals=True,
            forecast_only=True,
        )

        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            nbeats_view.display_nbeats_forecast(
                data=self.datasets[ns_parser.target_dataset],
                ticker_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_col=ns_parser.target_column,
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
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
            )

    @log_start_end(log=logger)
    def call_tcn(self, other_args: List[str]):
        """Process TCN command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="tcn",
            description="""
                Perform TCN forecast.
            """,
        )
        # TCN Hyperparameters
        parser.add_argument(
            "--num-filters",
            action="store",
            dest="num_filters",
            default=3,
            type=check_positive,
            help="The number of filters in a convolutional layer of the TCN",
        )
        parser.add_argument(
            "--weight-norm",
            action="store",
            dest="weight_norm",
            default=True,
            type=bool,
            help="Boolean value indicating whether to use weight normalization.",
        )
        parser.add_argument(
            "--dilation-base",
            action="store",
            dest="dilation_base",
            default=2,
            type=check_positive,
            help="The base of the exponent that will determine the dilation on every level.",
        )

        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
            target_dataset=True,
            n_days=True,
            target_column=True,
            train_split=True,
            past_covariates=True,
            forecast_horizon=True,
            save_checkpoints=True,
            force_reset=True,
            model_save_name="tcn_model",
            learning_rate=True,
            n_epochs=True,
            dropout=0.1,
            batch_size=32,
            input_chunk_length=True,
            output_chunk_length=True,
            residuals=True,
            forecast_only=True,
        )

        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            tcn_view.display_tcn_forecast(
                data=self.datasets[ns_parser.target_dataset],
                ticker_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_col=ns_parser.target_column,
                past_covariates=ns_parser.past_covariates,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.forecast_horizon,
                input_chunk_length=ns_parser.input_chunk_length,
                output_chunk_length=ns_parser.output_chunk_length,
                dropout=ns_parser.dropout,
                num_filters=ns_parser.num_filters,
                weight_norm=ns_parser.weight_norm,
                dilation_base=ns_parser.dilation_base,
                batch_size=ns_parser.batch_size,
                n_epochs=ns_parser.n_epochs,
                learning_rate=ns_parser.learning_rate,
                model_save_name=ns_parser.model_save_name,
                force_reset=ns_parser.force_reset,
                save_checkpoints=ns_parser.save_checkpoints,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
            )

    @log_start_end(log=logger)
    def call_regr(self, other_args: List[str]):
        """Process REGR command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="regr",
            description="""
                Perform a regression forecast
            """,
        )

        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
            output_chunk_length=True,
            forecast_horizon=True,
            train_split=True,
            past_covariates=True,
            n_days=True,
            target_dataset=True,
            target_column=True,
            lags=True,
            residuals=True,
            forecast_only=True,
        )

        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            regr_view.display_regression(
                data=self.datasets[ns_parser.target_dataset],
                ticker_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_col=ns_parser.target_column,
                past_covariates=ns_parser.past_covariates,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.forecast_horizon,
                output_chunk_length=ns_parser.output_chunk_length,
                lags=ns_parser.lags,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
            )

    @log_start_end(log=logger)
    def call_linregr(self, other_args: List[str]):
        """Process LINREGR command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="linregr",
            description="""
                Perform a linear regression forecast
            """,
        )
        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
            lags=True,
            output_chunk_length=True,
            forecast_horizon=True,
            train_split=True,
            past_covariates=True,
            target_column=True,
            n_days=True,
            target_dataset=True,
            residuals=True,
            forecast_only=True,
        )

        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            linregr_view.display_linear_regression(
                data=self.datasets[ns_parser.target_dataset],
                ticker_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_col=ns_parser.target_column,
                past_covariates=ns_parser.past_covariates,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.forecast_horizon,
                output_chunk_length=ns_parser.output_chunk_length,
                lags=ns_parser.lags,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
            )

    @log_start_end(log=logger)
    def call_brnn(self, other_args: List[str]):
        """Process BRNN command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="brnn",
            description="""
                Perform BRNN forecast (Vanilla RNN, LSTM, GRU)
            """,
        )
        # BRNN Hyperparameters
        parser.add_argument(
            "--n-rnn-layers",
            action="store",
            dest="n_rnn_layers",
            default=1,
            type=check_positive,
            help="Number of layers in the RNN module.",
        )
        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
            save_checkpoints=True,
            force_reset=True,
            model_save_name="brnn_model",
            learning_rate=True,
            n_epochs=True,
            batch_size=32,
            dropout=0,
            input_chunk_length=True,
            output_chunk_length=True,
            model_type=True,
            forecast_horizon=True,
            train_split=True,
            past_covariates=True,
            target_dataset=True,
            n_days=True,
            target_column=True,
            hidden_size=20,
            residuals=True,
            forecast_only=True,
        )

        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            brnn_view.display_brnn_forecast(
                data=self.datasets[ns_parser.target_dataset],
                ticker_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_col=ns_parser.target_column,
                past_covariates=ns_parser.past_covariates,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.forecast_horizon,
                input_chunk_length=ns_parser.input_chunk_length,
                output_chunk_length=ns_parser.output_chunk_length,
                model_type=ns_parser.model_type,
                n_rnn_layers=ns_parser.n_rnn_layers,
                hidden_size=ns_parser.hidden_size,
                dropout=ns_parser.dropout,
                batch_size=ns_parser.batch_size,
                n_epochs=ns_parser.n_epochs,
                learning_rate=ns_parser.learning_rate,
                model_save_name=ns_parser.model_save_name,
                force_reset=ns_parser.force_reset,
                save_checkpoints=ns_parser.save_checkpoints,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
            )

    @log_start_end(log=logger)
    def call_trans(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="trans",
            description="""
                Perform Transformer Forecast.
            """,
        )
        parser.add_argument(
            "--d-model",
            action="store",
            dest="d_model",
            default=64,
            type=check_positive,
            help="Number of expected features in inputs.",
        )
        parser.add_argument(
            "--nhead",
            action="store",
            dest="nhead",
            default=4,
            type=check_positive,
            help="Number of head in the attention mechanism.",
        )
        parser.add_argument(
            "--num_encoder_layers",
            action="store",
            dest="num_encoder_layers",
            default=3,
            type=check_positive,
            help="The number of encoder leayers in the encoder.",
        )
        parser.add_argument(
            "--num_decoder_layers",
            action="store",
            dest="num_decoder_layers",
            default=3,
            type=check_positive,
            help="The number of decoder leayers in the encoder.",
        )
        parser.add_argument(
            "--dim_feedforward",
            action="store",
            dest="dim_feedforward",
            default=512,
            type=check_positive,
            help="The dimension of the feedforward model.",
        )
        parser.add_argument(
            "--activation",
            action="store",
            dest="activation",
            default="relu",
            choices=["relu", "gelu"],
            type=str,
            help="Number of LSTM layers.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
            n_days=True,
            target_column=True,
            target_dataset=True,
            past_covariates=True,
            train_split=True,
            forecast_horizon=True,
            input_chunk_length=True,
            output_chunk_length=True,
            dropout=0,
            batch_size=32,
            n_epochs=True,
            model_save_name="trans_model",
            force_reset=True,
            save_checkpoints=True,
            residuals=True,
            forecast_only=True,
        )
        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            trans_view.display_trans_forecast(
                data=self.datasets[ns_parser.target_dataset],
                ticker_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_col=ns_parser.target_column,
                past_covariates=ns_parser.past_covariates,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.forecast_horizon,
                input_chunk_length=ns_parser.input_chunk_length,
                output_chunk_length=ns_parser.output_chunk_length,
                d_model=ns_parser.d_model,
                nhead=ns_parser.nhead,
                num_encoder_layers=ns_parser.num_encoder_layers,
                num_decoder_layers=ns_parser.num_decoder_layers,
                dim_feedforward=ns_parser.dim_feedforward,
                activation=ns_parser.activation,
                dropout=ns_parser.dropout,
                n_epochs=ns_parser.n_epochs,
                batch_size=ns_parser.batch_size,
                model_save_name=ns_parser.model_save_name,
                force_reset=ns_parser.force_reset,
                save_checkpoints=ns_parser.save_checkpoints,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
            )

    # Below this is ports to the old pred menu

    @log_start_end(log=logger)
    def call_tft(self, other_args: List[str]):
        """Process TFT command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="tft",
            description="""
                Perform TFT forecast (Temporal Fusion Transformer).
            """,
        )
        parser.add_argument(
            "--lstm-layers",
            action="store",
            dest="lstm_layers",
            default=1,
            type=check_positive,
            help="Number of LSTM layers.",
        )
        parser.add_argument(
            "--num-attention-heads",
            action="store",
            dest="num_attention_heads",
            default=4,
            type=check_positive,
            help="Number of attention heads.",
        )
        parser.add_argument(
            "--full-attention",
            action="store_true",
            dest="full_attention",
            default=False,
            help="Whether to apply a multi-head attention query.",
        )
        parser.add_argument(
            "--hidden-continuous-size",
            action="store",
            dest="hidden_continuous_size",
            default=8,
            type=check_positive,
            help="Default hidden size for processing continuous variables.",
        )

        # if user does not put in --target-dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
            save_checkpoints=True,
            target_dataset=True,
            n_days=True,
            force_reset=True,
            model_save_name="tft_model",
            train_split=True,
            forecast_horizon=True,
            hidden_size=16,
            batch_size=32,
            n_epochs=True,
            dropout=0.1,
            input_chunk_length=True,
            output_chunk_length=True,
            past_covariates=True,
            target_column=True,
            residuals=True,
            forecast_only=True,
        )

        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            tft_view.display_tft_forecast(
                data=self.datasets[ns_parser.target_dataset],
                ticker_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_col=ns_parser.target_column,
                past_covariates=ns_parser.past_covariates,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.forecast_horizon,
                input_chunk_length=ns_parser.input_chunk_length,
                output_chunk_length=ns_parser.output_chunk_length,
                hidden_size=ns_parser.hidden_size,
                lstm_layers=ns_parser.lstm_layers,
                num_attention_heads=ns_parser.num_attention_heads,
                full_attention=ns_parser.full_attention,
                dropout=ns_parser.dropout,
                hidden_continuous_size=ns_parser.hidden_continuous_size,
                n_epochs=ns_parser.n_epochs,
                batch_size=ns_parser.batch_size,
                model_save_name=ns_parser.model_save_name,
                force_reset=ns_parser.force_reset,
                save_checkpoints=ns_parser.save_checkpoints,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
            )

    # Below this is ports to the old pred menu
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
            target_column=True,
            target_dataset=True,
            n_days=True,
            end=True,
        )
        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            # BACKTESTING CHECK
            if ns_parser.s_end_date:

                if ns_parser.s_end_date < self.datasets[ns_parser.target_dataset][0]:
                    console.print(
                        "Backtesting not allowed, End Date is older than Start Date of data\n"
                    )

                if (
                    ns_parser.s_end_date
                    < get_next_stock_market_days(
                        last_stock_day=self.datasets[ns_parser.target_dataset][0],
                        n_next_days=5 + ns_parser.n_days,
                    )[-1]
                ):
                    console.print(
                        "Backtesting not allowed, End Date is too close to Start Date \n"
                    )

            arima_view.display_arima(
                dataset=ns_parser.target_dataset,
                values=self.datasets[ns_parser.target_dataset],
                target_column=ns_parser.target_column,
                arima_order=ns_parser.s_order,
                n_predict=ns_parser.n_days,
                seasonal=ns_parser.b_seasonal,
                ic=ns_parser.s_ic,
                results=ns_parser.b_results,
                s_end_date=ns_parser.s_end_date,
                export=ns_parser.export,
            )

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
            "--neighbors",
            action="store",
            dest="n_neighbors",
            type=check_positive,
            default=20,
            help="number of neighbors to use on the algorithm.",
        )
        parser.add_argument(
            "--no_shuffle",
            action="store_false",
            dest="no_shuffle",
            default=True,
            help="Specify if shuffling validation inputs.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_FIGURES_ALLOWED,
            n_jumps=True,
            n_days=True,
            input_chunk_length=True,
            train_split=True,
            target_dataset=True,
            target_column=True,
            end=True,
        )
        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return
            data = self.datasets[ns_parser.target_dataset]
            try:
                data["date"] = data["date"].apply(helpers.dt_format)
                data["date"] = data["date"].apply(lambda x: pd.to_datetime(x))
                data = data.set_index("date")
            except (KeyError, ValueError):
                if data.index.name != "date":
                    console.print("[red]Dataframe must have 'date' column.[/red]\n")
                    return
            data = data[ns_parser.target_column]
            if ns_parser:
                knn_view.display_k_nearest_neighbors(
                    ticker=ns_parser.target_dataset,
                    data=data,
                    n_neighbors=ns_parser.n_neighbors,
                    n_input_days=ns_parser.input_chunk_length,
                    n_predict_days=ns_parser.n_days,
                    test_size=1 - ns_parser.train_split,
                    end_date=ns_parser.s_end_date,
                    no_shuffle=ns_parser.no_shuffle,
                )

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
            "--dist",
            choices=mc_model.DISTRIBUTIONS,
            default="lognormal",
            dest="dist",
            help="Whether to model returns or log returns",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--target-dataset")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
            n_days=True,
            target_dataset=True,
            target_column=True,
            n_epochs=True,
        )
        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return
            data = self.datasets[ns_parser.target_dataset]
            try:
                data["date"] = data["date"].apply(helpers.dt_format)
                data["date"] = data["date"].apply(lambda x: pd.to_datetime(x))
                data = data.set_index("date")
            except (KeyError, ValueError):
                if data.index.name != "date":
                    console.print("[red]Dataframe must have 'date' column.[/red]\n")
                    return
            data = data[ns_parser.target_column]

            mc_view.display_mc_forecast(
                data=data,
                n_future=ns_parser.n_days,
                n_sims=ns_parser.n_epochs,
                use_log=ns_parser.dist == "lognormal",
                export=ns_parser.export,
            )
