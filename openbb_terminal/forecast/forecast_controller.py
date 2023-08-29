"""Forecast Controller Module"""
__docformat__ = "numpy"

# pylint: disable=C0302,too-many-branches,too-many-arguments,R0904,R0902,W0707
# flake8: noqa

# IMPORT STANDARD
import argparse
import logging
from typing import Any, Dict, List, Optional

# IMPORT THIRDPARTY
import pandas as pd
import psutil

try:
    import darts
    import torch

    darts_latest = "0.23.0"
    # check darts version
    if darts.__version__ != darts_latest:
        print(f"You are currently using Darts version {darts.__version__}")
        print(
            "Follow instructions on creating a new conda environment with the latest "
            f"Darts version ({darts_latest}):"
        )
        print("https://my.openbb.co/app/sdk/installation")
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "Please install the forecast version of the terminal. Instructions can be found "
        "under the python tab: https://my.openbb.co/app/sdk/installation"
    )

try:
    import whisper
    import transformers
    from whisper.tokenizer import LANGUAGES, TO_LANGUAGE_CODE
    from openbb_terminal.forecast.whisper_utils import str2bool

    transformers_ver = transformers.__version__
    # if imports are successful, set flag to True
    WHISPER_AVAILABLE = True

except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "Please use poetry to install latest whisper model and dependencies. \n"
        "poetry install -E forecast \n"
        "\n"
        "If you are not using poetry, please install whisper model. Instructions can be found here: \n"
        "https://github.com/openai/whisper \n"
        "Please install the transformers library with the following command: \n"
        "pip install transformers \n"
    )


# ignore  pylint(ungrouped-imports)
# pylint: disable=ungrouped-imports

# IMPORT INTERNAL
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.common import common_model
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end

from openbb_terminal.helper_funcs import (
    check_positive,
    check_positive_float,
    NO_EXPORT,
    EXPORT_ONLY_FIGURES_ALLOWED,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    log_and_raise,
    valid_date,
    parse_and_split_input,
    check_non_negative,
    check_positive_float_list,
    check_list_values,
    check_valid_date,
)

from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText

from openbb_terminal.forecast import (
    anom_view,
    autoarima_view,
    autoces_view,
    autoets_view,
    autoselect_view,
    brnn_view,
    expo_model,
    expo_view,
    forecast_model,
    forecast_view,
    helpers,
    linregr_view,
    mstl_view,
    nbeats_view,
    nhits_view,
    regr_view,
    rnn_view,
    rwd_view,
    seasonalnaive_view,
    tcn_view,
    tft_view,
    theta_view,
    trans_view,
    whisper_model,
    timegpt_view,
)

logger = logging.getLogger(__name__)
empty_df = pd.DataFrame()


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


class ForecastController(BaseController):
    """Forecast class"""

    CHOICES_COMMANDS: List[str] = [
        "load",
        "show",
        "plot",
        "clean",
        "combine",
        "setndays",
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
        "autoselect",
        "autoarima",
        "autoces",
        "autoets",
        "mstl",
        "rwd",
        "seasonalnaive",
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
        "season",
        "which",
        "nhits",
        "anom",
        "whisper",
        "timegpt",
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
    Investing involves monetary risk that OpenBB does not take a role in. Please research any
    prediction techniques fully before attempting to use. OpenBB is not liable for any loss or
    damages."""

    PATH = "/forecast/"
    CHOICES_GENERATION = True

    loaded_dataset_cols = "\n"
    list_dataset_cols: list = list()

    def __init__(
        self,
        ticker: str = "",
        data: pd.DataFrame = empty_df,
        queue: Optional[List[str]] = None,
    ):
        """Constructor"""
        super().__init__(queue)
        self.files: List[str] = []
        self.choices = {}
        # The full file name with extension, this allows the rest command to work
        self.files_full: List[List[str]] = []
        self.datasets: Dict[str, pd.DataFrame] = dict()
        self.MINIMUM_DATA_LENGTH = 100
        self.ndays = 5

        if ticker and not data.empty:
            data = data.reset_index()
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
        self.DATA_FILES = forecast_model.get_default_files()

        # setting device on GPU if available, else CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.comp_ram = f"{round(psutil.virtual_memory().total / (1024.0 ** 3),2)}G"
        self.rec_data_size = f"{(psutil.virtual_memory().total / (1024.0 ** 3))//3}G"
        self.torch_version = torch.__version__
        self.darts_version = darts.__version__

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            self.choices = choices
            self.completer = NestedCompleter.from_nested_dict(choices)

    def call_exit(self, _) -> None:
        """Process exit terminal command from forecast menu."""
        self.save_class()
        for _ in range(self.PATH.count("/") + 1):
            self.queue.insert(0, "quit")

    def get_dataset_columns(self):
        return {
            f"{dataset}.{column}": {column: None, dataset: None}
            for dataset, dataframe in self.datasets.items()
            for column in dataframe.columns
        }

    def parse_input(self, an_input: str) -> List:
        """Parse controller input

        Overrides the parent class function to handle YouTube video URL conventions.
        See `BaseController.parse_input()` for details.
        """

        # Filtering out YouTube video parameters like "v=" and removing the domain name
        youtube_filter = r"(youtube\.com/watch\?v=)"

        custom_filters = [youtube_filter]

        commands = parse_and_split_input(
            an_input=an_input.replace("https://", ""), custom_filters=custom_filters
        )
        return commands

    def update_runtime_choices(self):
        # Load in any newly exported files
        self.DATA_FILES = forecast_model.get_default_files()
        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default  # type: ignore

            self.choices = choices
            self.completer = NestedCompleter.from_nested_dict(choices)

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
        self.update_runtime_choices()
        current_user = get_current_user()
        mt = MenuText("forecast/")
        mt.add_param("_disclaimer_", self.disclaimer)
        mt.add_raw("\n")
        mt.add_param(
            "_data_loc",
            f"\n\t{current_user.preferences.USER_EXPORTS_DIRECTORY}\n"
            f"\t{current_user.preferences.USER_CUSTOM_IMPORTS_DIRECTORY}",
        )
        mt.add_raw("\n")
        mt.add_cmd("load")
        mt.add_raw("\n")
        mt.add_param("_loaded", self.loaded_dataset_cols)
        mt.add_info("_exploration_")
        mt.add_cmd("show", self.files)
        mt.add_cmd("plot", self.files)
        mt.add_cmd("clean", self.files)
        mt.add_cmd("combine", self.files)
        mt.add_cmd("setndays", self.ndays)
        mt.add_cmd("desc", self.files)
        mt.add_cmd("corr", self.files)
        mt.add_cmd("season", self.files)
        mt.add_cmd("delete", self.files)
        mt.add_cmd("rename", self.files)
        mt.add_cmd("export", self.files)
        mt.add_raw("\n")
        mt.add_info("_feateng_")
        mt.add_cmd("ema", self.files)
        mt.add_cmd("sto", self.files)
        mt.add_cmd("rsi", self.files)
        mt.add_cmd("roc", self.files)
        mt.add_cmd("mom", self.files)
        mt.add_cmd("delta", self.files)
        mt.add_cmd("atr", self.files)
        mt.add_cmd("signal", self.files)
        mt.add_raw("\n")
        mt.add_info("_tsforecasting_")
        mt.add_cmd("autoselect", self.files)
        mt.add_cmd("autoarima", self.files)
        mt.add_cmd("autoces", self.files)
        mt.add_cmd("autoets", self.files)
        mt.add_cmd("mstl", self.files)
        mt.add_cmd("rwd", self.files)
        mt.add_cmd("seasonalnaive", self.files)
        mt.add_cmd("expo", self.files)
        mt.add_cmd("theta", self.files)
        mt.add_cmd("linregr", self.files)
        mt.add_cmd("regr", self.files)
        mt.add_cmd("rnn", self.files)
        mt.add_cmd("brnn", self.files)
        mt.add_cmd("nbeats", self.files)
        mt.add_cmd("nhits", self.files)
        mt.add_cmd("tcn", self.files)
        mt.add_cmd("trans", self.files)
        mt.add_cmd("tft", self.files)
        mt.add_raw("\n")
        mt.add_info("_anomaly_")
        mt.add_cmd("anom", self.files)
        mt.add_raw("\n")
        mt.add_info("_misc_")
        mt.add_cmd("timegpt", self.files)
        mt.add_cmd("whisper", WHISPER_AVAILABLE)

        console.print(text=mt.menu_text, menu="Forecast")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.files_full:
            queue = ["forecast"]
            for file, alias in self.files_full:
                load = f"'load {file}"
                if alias:
                    load += f" -a {alias}'"
                else:
                    load += "'"
                queue.append(load)
            return queue
        return []

    def add_standard_args(
        self,
        parser: argparse.ArgumentParser,
        target_dataset: bool = False,
        target_column: bool = False,
        period: Optional[int] = None,
        n_days: bool = False,
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
        all_past_covariates: bool = False,
        lags: bool = False,
        hidden_size: int = 0,
        n_jumps: bool = False,
        end: bool = False,
        start: bool = False,
        residuals: bool = False,
        forecast_only: bool = False,
        naive: bool = False,
        explainability_raw: bool = False,
        export_pred_raw: bool = False,
        metric: bool = False,
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
        if all_past_covariates:
            parser.add_argument(
                "--all-past-covariates",
                action="store_true",
                dest="all_past_covariates",
                default=False,
                help="Adds all rows as past covariates except for date and the target column.",
            )
        if naive:
            parser.add_argument(
                "--naive",
                action="store_true",
                dest="naive",
                default=False,
                help="Show the naive baseline for a model.",
            )
        if target_dataset:
            parser.add_argument(
                "-d",
                "--dataset",
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
                type=check_positive,
                default=self.ndays,
                help="prediction days.",
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
                type=check_positive_float,
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
                help='Enter a string specifying the RNN module type ("RNN", "LSTM" or "GRU")',
            )
        if dropout is not None:
            parser.add_argument(
                "--dropout",
                action="store",
                dest="dropout",
                default=dropout,
                type=check_positive_float,
                help="Fraction of neurons affected by Dropout, from 0 to 1.",
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
                "--end",
                action="store",
                type=valid_date,
                dest="s_end_date",
                default=None,
                help="The end date (format YYYY-MM-DD) to select for testing",
            )
        if start:
            parser.add_argument(
                "--start",
                action="store",
                type=valid_date,
                dest="s_start_date",
                default=None,
                help="The start date (format YYYY-MM-DD) to select for testing",
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
                default=14,
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
                "--forecast-only",
                help="Do not plot the historical data without forecasts.",
                action="store_true",
                default=False,
                dest="forecast_only",
            )
        if explainability_raw:
            parser.add_argument(
                "--explainability-raw",
                action="store_true",
                dest="explainability_raw",
                default=False,
                help="Prints out a raw dataframe showing explainability results.",
            )

        if export_pred_raw:
            parser.add_argument(
                "--export-pred-raw",
                action="store_true",
                dest="export_pred_raw",
                default=False,
                help="Export predictions to a csv file.",
            )

        if metric:
            parser.add_argument(
                "--metric",
                type=str,
                action="store",
                dest="metric",
                default="mape",
                choices=["rmse", "mse", "mape", "smape"],
                help="Calculate precision based on a specific metric (rmse, mse, mape)",
            )

            # if user does not put in --dataset
        return parser

    def load(self, ticker: str, data: pd.DataFrame):
        """Loads news dataframes into memory"""

        # check if data has minimum number of rows
        if ticker and len(data) < self.MINIMUM_DATA_LENGTH:
            console.print(
                f"[red]Dataset is smaller than recommended minimum {self.MINIMUM_DATA_LENGTH} data points. [/red]"
            )
            console.print(
                f"[red]Please increase the number of data points for [ {ticker} ] and try again.[/red]"
            )
            return

        if not data.empty:
            data.columns = data.columns.map(lambda x: x.lower().replace(" ", "_"))

            # If the index is a date, move this into a normal column
            if data.index.name == "date":
                data = data.reset_index()
            # Convert date to datetime
            # TODO: for now we drop time, once we add handling for time remove this
            if "date" in data.columns:
                data["date"] = data["date"].apply(helpers.dt_format)
                data["date"] = pd.to_datetime(data["date"])

            # if we import a custom dataset, remove the old index "unnamed:_0"
            if "unnamed:_0" in data.columns:
                # Some loaded datasets have the date as unnamed, which is not helpful
                if check_valid_date(data["unnamed:_0"].iloc[0]):
                    data["date"] = data["unnamed:_0"].copy()
                data = data.drop(columns=["unnamed:_0"])

            self.files.append(ticker)
            self.datasets[ticker] = data

            # Process new datasets to be updated
            self.list_dataset_cols = list()
            maxfile = max(len(file) for file in self.files)
            self.loaded_dataset_cols = "\n"
            for dataset, x_data in self.datasets.items():
                self.loaded_dataset_cols += (
                    f"  {dataset} {(maxfile - len(dataset)) * ' '}: "
                    f"{', '.join(x_data.columns)}\n"
                )

                for col in data.columns:
                    self.list_dataset_cols.append(f"{dataset}.{col}")

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
            choices=self.DATA_FILES.keys(),
            type=str,
        )
        parser.add_argument(
            "-a",
            "--alias",
            help="Alias name to give to the dataset",
            type=str,
        )
        parser.add_argument(
            "--sheet-name",
            dest="sheet_name",
            default=None,
            nargs="+",
            help="Name of excel sheet to save data to. Only valid for .xlsx files.",
        )

        # Load in any newly exported files
        self.DATA_FILES = forecast_model.get_default_files()

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
                data = common_model.load(
                    file,
                    data_files=self.DATA_FILES,
                    data_examples={},
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
                if not data.empty:
                    self.files_full.append([ns_parser.file, ns_parser.alias])
                    self.load(alias, data)
            self.update_runtime_choices()

    # Show selected dataframe on console
    @log_start_end(log=logger)
    def call_which(self, other_args: List[str]):
        """Process which command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="which",
            description="Show library versions of required packages.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
        )

        if ns_parser:
            console.print(
                f"[green]Current Compute Device (CPU or GPU):[/green] {self.device.upper()}"
            )
            console.print(f"[green]Current RAM:[/green] {self.comp_ram}")
            console.print(
                f"[green]Recommended Max dataset size based on current RAM:[/green] {self.rec_data_size}"
            )
            console.print(f"[green]Torch version:[/green] {self.torch_version}")
            console.print(f"[green]Darts version:[/green] {self.darts_version}")

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
            "--sortby",
            help="Sort based on a column in the DataFrame",
            nargs="+",
            type=str,
            dest="sortby",
            default="",
        )
        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        parser.add_argument(
            "--limit-col",
            action="store",
            dest="limit_col",
            default=10,
            type=check_positive,
            help="Set the number of columns to display when showing the dataset",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_RAW_DATA_ALLOWED,
            limit=10,
        )

        if ns_parser:
            if not ns_parser.name:
                dataset_names = list(self.datasets.keys())
            else:
                dataset_names = [ns_parser.name]

            for name in dataset_names:
                df = self.datasets[name]

                if name in self.datasets and self.datasets[name].empty:
                    console.print(
                        f"[red]No data available for {ns_parser.name}.[/red]\n"
                    )
                elif ns_parser.sortby:
                    sort_column = " ".join(ns_parser.sortby)
                    if sort_column not in self.datasets[name].columns:
                        console.print(
                            f"[red]{sort_column} not a valid column."
                            "Showing without sorting.\n[/red]"
                        )
                    else:
                        df = df.sort_values(by=sort_column, ascending=ns_parser.reverse)

                forecast_view.show_df(
                    df, ns_parser.limit, ns_parser.limit_col, name, ns_parser.export
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
            choices=self.datasets.keys(),
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
            else:
                self.datasets[dataset] = forecast_model.rename_column(
                    self.datasets[dataset], column_old, column_new
                )
            self.update_runtime_choices()
            self.refresh_datasets_on_menu()

            console.print(
                f"[green]Successfully renamed {column_old} into {column_new}, in {dataset}[/green]"
            )

    @log_start_end(log=logger)
    def call_setndays(self, other_args: List[str]):
        """Process setndays command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="setndays",
            description="Set the number of days to forecast",
        )
        parser.add_argument(
            "-n",
            "--n-days",
            help="Number of days to forecast",
            dest="n_days",
            type=check_positive,
            default=5,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")

        ns_parser = self.parse_known_args_and_warn(parser, other_args, NO_EXPORT)

        if ns_parser:
            self.ndays = ns_parser.n_days
            console.print(
                f"[green]Number of days to forecast set to {self.ndays}[/green]"
            )
            self.update_runtime_choices()

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

        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(parser, target_dataset=True)
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_RAW_DATA_ALLOWED,
        )

        if ns_parser:
            # check proper file name is provided
            if not ns_parser.target_dataset:
                console.print(
                    "[red]Please select a valid dataset with the -d flag.\n[/red]"
                )
                return

            df = self.datasets[ns_parser.target_dataset]
            forecast_view.describe_df(
                df,
                ns_parser.target_dataset,
                ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
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
            help="Dataset.column values to be displayed in a plot. Use comma to separate multiple",
            choices=self.get_dataset_columns(),
            dest="values",
            type=str,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if not ns_parser:
            return

        if not ns_parser.values:
            console.print(
                "[red]Please select a valid dataset with the -d flag.\n[/red]"
            )
            return

        values = [x.strip() for x in ns_parser.values.split(",")]
        target_df = values[0].split(".")[0]
        if target_df not in self.datasets:
            console.print(
                "[red]Please select a valid dataset with the -d flag.\n[/red]"
            )
            return

        for value in values:
            if value.split(".")[0] != target_df:
                console.print("[red]Please enter values from the same dataset.\n[/red]")
                return

        forecast_view.display_plot(
            self.datasets[target_df],
            [x.split(".")[1] for x in values],
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
            "-d",
            "--dataset",
            help="Dataset.column values to be displayed in a plot",
            dest="values",
            choices=self.get_dataset_columns(),
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
            console.print(
                "[red]Please select a valid dataset with the -d flag.\n[/red]"
            )
            return

        try:
            dataset, col = ns_parser.values.split(".")
            data = self.datasets[dataset]
        except ValueError:
            console.print("[red]Please enter 'dataset'.'column'.[/red]\n")
            return

        forecast_view.display_seasonality(
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

        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(parser, target_dataset=True)
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_FIGURES_ALLOWED,
        )

        if ns_parser:
            # check proper file name is provided
            if not ns_parser.target_dataset:
                console.print(
                    "[red]Please select a valid dataset with the -d flag.\n[/red]"
                )
                return

            data = self.datasets[ns_parser.target_dataset]

            forecast_view.display_corr(
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
            description="Combine two entire datasets, or add specific columns. Add specific"
            "columns with the syntax: <datasetX.column2>",
        )
        parser.add_argument(
            "--dataset",
            help="Dataset to add columns to",
            dest="dataset",
            choices=list(self.datasets.keys()),
        )
        # pylint: disable=consider-using-dict-items
        column_choices = [
            f"{x}.{y}" for x in self.datasets for y in self.datasets[x].columns
        ]
        column_choices.extend(list(self.datasets))
        parser.add_argument(
            "-c",
            "--columns",
            help="The columns we want to add <dataset.column>",
            dest="columns",
            choices=column_choices,
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

            for option in ns_parser.columns.split(","):
                if "." in option:
                    dataset, col = option.split(".")
                    columns = [col]
                else:
                    dataset = option
                    columns = [x for x in self.datasets[dataset].columns if x != "date"]

                if dataset not in self.datasets:
                    console.print(
                        f"Not able to find the dataset {dataset}. Please choose one of "
                        f"the following: {', '.join(self.datasets)}"
                    )
                    continue
                for column in columns:
                    data = forecast_model.combine_dfs(
                        data, self.datasets[dataset], column, dataset
                    )

            self.datasets[ns_parser.dataset] = data
            self.update_runtime_choices()
            self.refresh_datasets_on_menu()

            console.print(
                f"[green]Successfully added {ns_parser.columns} into {ns_parser.dataset}[/green]"
            )

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
        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(parser, target_dataset=True)
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
            limit=5,
        )
        if ns_parser:
            # check proper file name is provided
            if not ns_parser.target_dataset:
                console.print(
                    "[red]Please select a valid dataset with the -d flag.\n[/red]"
                )
                return

            (
                self.datasets[ns_parser.target_dataset],
                clean_status,
            ) = forecast_model.clean(
                self.datasets[ns_parser.target_dataset],
                ns_parser.fill,
                ns_parser.drop,
                ns_parser.limit,
            )
            if not clean_status:
                console.print(
                    f"[green]Successfully cleaned '{ns_parser.target_dataset}' dataset[/green]"
                )
            else:
                console.print(f"[red]{ns_parser.name} still contains NaNs.[/red]")

    @log_start_end(log=logger)
    def call_ema(self, other_args: List[str]):
        """Process EMA"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ema",
            description="Add exponential moving average to dataset based on specific column.",
        )

        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser, target_dataset=True, period=10, target_column=True
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
        )
        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            self.datasets[ns_parser.target_dataset] = forecast_model.add_ema(
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

    @log_start_end(log=logger)
    def call_sto(self, other_args: List[str]):
        """Process Stochastic Oscillator"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sto",
            description="Add in Stochastic Oscillator %K and %D",
        )
        parser.add_argument(
            "--close-col",
            help="Close column name to use for Stochastic Oscillator",
            dest="close_col",
            type=str,
            default="close",
        )
        parser.add_argument(
            "--high-col",
            help="High column name to use for Stochastic Oscillator",
            dest="high_col",
            type=str,
            default="high",
        )
        parser.add_argument(
            "--low-col",
            help="Low column name to use for Stochastic Oscillator",
            dest="low_col",
            type=str,
            default="low",
        )
        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(parser, target_dataset=True, period=10)
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, NO_EXPORT, limit=5
        )
        if ns_parser:
            # check proper file name is provided
            if not ns_parser.target_dataset:
                console.print(
                    "[red]Please select a valid dataset with the -d flag.\n[/red]"
                )
                return

            df = forecast_model.add_sto(
                self.datasets[ns_parser.target_dataset],
                close_column=ns_parser.close_col,
                high_column=ns_parser.high_col,
                low_column=ns_parser.low_col,
                period=ns_parser.period,
            )
            if not df.empty:
                self.datasets[ns_parser.target_dataset] = df
                console.print(
                    f"Successfully added 'STOCH&D_{ns_parser.period}' to '{ns_parser.target_dataset}' dataset"
                )
                # update forecast menu with new column on modified dataset
                self.refresh_datasets_on_menu()
                self.update_runtime_choices()

    def handle_delete(self, dataset, column):
        if dataset not in self.datasets:
            console.print(
                f"Not able to find the dataset {dataset}. Please choose one of "
                f"the following: {', '.join(self.datasets)}"
            )
        else:
            forecast_model.delete_column(self.datasets[dataset], column)

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
            choices=self.get_dataset_columns(),
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--delete")
        ns_parser = self.parse_known_args_and_warn(parser, other_args, NO_EXPORT)

        if ns_parser:
            if "," in ns_parser.delete:
                for option in ns_parser.delete:
                    print(option)
                    dataset, column = option.split(".")
                    self.handle_delete(dataset, column)
            else:
                dataset, column = ns_parser.delete.split(".")
                self.handle_delete(dataset, column)

            self.update_runtime_choices()
            self.refresh_datasets_on_menu()

            console.print(f"[green]Successfully deleted {ns_parser.delete}[/green]")

    @log_start_end(log=logger)
    def call_rsi(self, other_args: List[str]):
        """Process RSI"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rsi",
            description="Add rsi to dataset based on specific column.",
        )
        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser, target_dataset=True, target_column=True, period=10
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
        )
        if ns_parser:
            # check proper file name is provided
            if not ns_parser.target_dataset:
                console.print(
                    "[red]Please select a valid dataset with the -d flag.\n[/red]"
                )
                return

            self.datasets[ns_parser.target_dataset] = forecast_model.add_rsi(
                self.datasets[ns_parser.target_dataset],
                ns_parser.target_column,
                ns_parser.period,
            )
            console.print(
                f"Successfully added 'RSI_{ns_parser.period}_{ns_parser.target_column}' "
                f"to '{ns_parser.target_dataset}' dataset"
            )

            # update forecast menu with new column on modified dataset
            self.refresh_datasets_on_menu()

            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_roc(self, other_args: List[str]):
        """Process ROC"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="roc",
            description="Add rate of change to dataset based on specific column.",
        )
        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser, target_dataset=True, target_column=True, period=10
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
        )
        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            self.datasets[ns_parser.target_dataset] = forecast_model.add_roc(
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

    @log_start_end(log=logger)
    def call_mom(self, other_args: List[str]):
        """Process Momentum"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="mom",
            description="Add momentum to dataset based on specific column.",
        )
        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser, target_dataset=True, target_column=True, period=10
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
        )
        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            self.datasets[ns_parser.target_dataset] = forecast_model.add_momentum(
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

    @log_start_end(log=logger)
    def call_delta(self, other_args: List[str]):
        """Process %Change (Delta)"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="delta",
            description="Add %Change (Delta) to dataset based on specific column.",
        )

        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(parser, target_dataset=True, target_column=True)
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
        )
        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            self.datasets[ns_parser.target_dataset] = forecast_model.add_delta(
                self.datasets[ns_parser.target_dataset], ns_parser.target_column
            )
            console.print(
                f"Successfully added 'Delta_{ns_parser.target_column}' to '{ns_parser.target_dataset}' dataset"
            )

            # update forecast menu with new column on modified dataset
            self.refresh_datasets_on_menu()

            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_atr(self, other_args: List[str]):
        """Process Average True Range"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="atr",
            description="Add Average True Range to dataset of specific stock ticker.",
        )
        parser.add_argument(
            "--close-col",
            help="Close column name to use for Average True Range.",
            dest="close_col",
            type=str,
            default="close",
        )
        parser.add_argument(
            "--high-col",
            help="High column name to use for Average True Range.",
            dest="high_col",
            type=str,
            default="high",
        )
        parser.add_argument(
            "--low-col",
            help="Low column name to use for Average True Range.",
            dest="low_col",
            type=str,
            default="low",
        )

        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(parser, target_dataset=True, target_column=True)
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
        )
        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            self.datasets[ns_parser.target_dataset] = forecast_model.add_atr(
                self.datasets[ns_parser.target_dataset],
                close_column=ns_parser.close_col,
                high_column=ns_parser.high_col,
                low_column=ns_parser.low_col,
            )
            # check if true range was added
            if "true_range" in self.datasets[ns_parser.target_dataset].columns:
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
        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(parser, target_dataset=True, target_column=True)
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            NO_EXPORT,
        )
        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            self.datasets[ns_parser.target_dataset] = forecast_model.add_signal(
                self.datasets[ns_parser.target_dataset],
                target_column=ns_parser.target_column,
            )
            console.print(
                f"Successfully added 'Price Signal' to '{ns_parser.target_dataset}' dataset"
            )

            # update forecast menu with new column on modified dataset
            self.refresh_datasets_on_menu()

            self.update_runtime_choices()

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
            choices=common_model.file_types,
            type=str,
            default="xlsx",
        )
        parser.add_argument(
            "--sheet-name",
            help="The name of the sheet to export to when type is XLSX.",
            dest="sheet_name",
            type=str,
            default="",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(parser, target_dataset=True)
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=NO_EXPORT,
        )

        if not helpers.check_parser_input(ns_parser, self.datasets, "ignore_column"):
            return

        forecast_view.export_df(
            self.datasets[ns_parser.target_dataset],
            ns_parser.type,
            ns_parser.target_dataset,
            ns_parser.sheet_name,
        )

    # Best Statistical Model
    @log_start_end(log=logger)
    def call_autoselect(self, other_args: List[str]):
        """Process autoselect command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="autoselect",
            description="""
                Perform Automatic Statistical Forecast
                (select best statistical model from AutoARIMA, AutoETS, AutoCES, MSTL, ...)
            """,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            target_dataset=True,
            target_column=True,
            n_days=True,
            seasonal="A",
            periods=True,
            window=True,
            residuals=True,
            forecast_only=True,
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )
        # TODO Convert this to multi series
        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return
            autoselect_view.display_autoselect_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                seasonal_periods=ns_parser.seasonal_periods,
                start_window=ns_parser.start_window,
                forecast_horizon=ns_parser.n_days,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
            )

    # AutoARIMA Model
    @log_start_end(log=logger)
    def call_autoarima(self, other_args: List[str]):
        """Process autoarima command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="autoarima",
            description="""
                Perform Automatic ARIMA forecast:
                https://nixtla.github.io/statsforecast/examples/getting_started_with_auto_arima_and_ets.html
            """,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            target_dataset=True,
            target_column=True,
            n_days=True,
            seasonal="A",
            periods=True,
            window=True,
            residuals=True,
            forecast_only=True,
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )
        # TODO Convert this to multi series
        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            autoarima_view.display_autoarima_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                seasonal_periods=ns_parser.seasonal_periods,
                start_window=ns_parser.start_window,
                forecast_horizon=ns_parser.n_days,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
            )

    # AutoCES Model
    @log_start_end(log=logger)
    def call_autoces(self, other_args: List[str]):
        """Process autoces command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="autoces",
            description="""
                Perform Automatic Complex Exponential Smoothing forecast:
                https://nixtla.github.io/statsforecast/models.html#autoces
            """,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            target_dataset=True,
            target_column=True,
            n_days=True,
            seasonal="A",
            periods=True,
            window=True,
            residuals=True,
            forecast_only=True,
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )
        # TODO Convert this to multi series
        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            autoces_view.display_autoces_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                seasonal_periods=ns_parser.seasonal_periods,
                start_window=ns_parser.start_window,
                forecast_horizon=ns_parser.n_days,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
            )

    # AutoETS Model
    @log_start_end(log=logger)
    def call_autoets(self, other_args: List[str]):
        """Process autoets command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="autoets",
            description="""
                Perform Automatic ETS (Error, Trend, Seasonality) forecast:
                https://nixtla.github.io/statsforecast/examples/getting_started_with_auto_arima_and_ets.html
            """,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            target_dataset=True,
            target_column=True,
            n_days=True,
            seasonal="A",
            periods=True,
            window=True,
            residuals=True,
            forecast_only=True,
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )
        # TODO Convert this to multi series
        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            autoets_view.display_autoets_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                seasonal_periods=ns_parser.seasonal_periods,
                start_window=ns_parser.start_window,
                forecast_horizon=ns_parser.n_days,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
            )

    # MSTL Model
    @log_start_end(log=logger)
    def call_mstl(self, other_args: List[str]):
        """Process mstl command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="mstl",
            description="""
                Perform Multiple Seasonalities and Trend using Loess (MSTL) forecast:
                https://nixtla.github.io/statsforecast/examples/multipleseasonalities.html
            """,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            target_dataset=True,
            target_column=True,
            n_days=True,
            seasonal="A",
            periods=True,
            window=True,
            residuals=True,
            forecast_only=True,
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )
        # TODO Convert this to multi series
        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            mstl_view.display_mstl_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                seasonal_periods=ns_parser.seasonal_periods,
                start_window=ns_parser.start_window,
                forecast_horizon=ns_parser.n_days,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
            )

    # RWD Model
    @log_start_end(log=logger)
    def call_rwd(self, other_args: List[str]):
        """Process rwd command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="rwd",
            description="""
                Perform Random Walk with Drift forecast:
                https://nixtla.github.io/statsforecast/models.html#randomwalkwithdrift
            """,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            target_dataset=True,
            target_column=True,
            n_days=True,
            seasonal="A",
            periods=False,
            window=True,
            residuals=True,
            forecast_only=True,
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )
        # TODO Convert this to multi series
        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            rwd_view.display_rwd_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                start_window=ns_parser.start_window,
                forecast_horizon=ns_parser.n_days,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
            )

    # SeasonalNaive Model
    @log_start_end(log=logger)
    def call_seasonalnaive(self, other_args: List[str]):
        """Process seasonalnaive command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="seasonalnaive",
            description="""
                Perform SeasonalNaive forecasting:
                https://nixtla.github.io/statsforecast/models.html#seasonalnaive
            """,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            target_dataset=True,
            target_column=True,
            n_days=True,
            seasonal="A",
            periods=True,
            window=True,
            residuals=True,
            forecast_only=True,
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )
        # TODO Convert this to multi series
        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            seasonalnaive_view.display_seasonalnaive_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                seasonal_periods=ns_parser.seasonal_periods,
                start_window=ns_parser.start_window,
                forecast_horizon=ns_parser.n_days,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
            )

    # EXPO Model
    @log_start_end(log=logger)
    def call_expo(self, other_args: List[str]):
        """Process expo command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="expo",
            description="""
                Perform Probabilistic Exponential Smoothing forecast:
                https://unit8co.github.io/darts/generated_api/darts.models.forecasting.exponential_smoothing.html
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
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            target_dataset=True,
            target_column=True,
            n_days=True,
            seasonal="A",
            periods=True,
            window=True,
            residuals=True,
            forecast_only=True,
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
            metric=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )
        # TODO Convert this to multi series
        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            expo_view.display_expo_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                trend=ns_parser.trend,
                seasonal=ns_parser.seasonal,
                seasonal_periods=ns_parser.seasonal_periods,
                dampen=ns_parser.dampen,
                start_window=ns_parser.start_window,
                forecast_horizon=ns_parser.n_days,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
                metric=ns_parser.metric,
            )

    @log_start_end(log=logger)
    def call_theta(self, other_args: List[str]):
        """Process theta command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="theta",
            description="""
                Perform Theta forecast:
                https://unit8co.github.io/darts/generated_api/darts.models.forecasting.theta.html
            """,
        )
        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            target_dataset=True,
            n_days=True,
            target_column=True,
            seasonal="M",
            periods=True,
            window=True,
            residuals=True,
            forecast_only=True,
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
            metric=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )

        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            theta_view.display_theta_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                seasonal=ns_parser.seasonal,
                seasonal_periods=ns_parser.seasonal_periods,
                start_window=ns_parser.start_window,
                forecast_horizon=ns_parser.n_days,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
                metric=ns_parser.metric,
            )

    @log_start_end(log=logger)
    def call_rnn(self, other_args: List[str]):
        """Process RNN command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="rnn",
            description="""
                Perform RNN forecast (Vanilla RNN, LSTM, GRU):
                https://unit8co.github.io/darts/generated_api/darts.models.forecasting.rnn_model.html
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

        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            target_dataset=True,
            n_days=True,
            target_column=True,
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
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
            metric=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )

        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            rnn_view.display_rnn_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.n_days,
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
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
                metric=ns_parser.metric,
            )

    @log_start_end(log=logger)
    def call_nbeats(self, other_args: List[str]):
        """Process NBEATS command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="nbeats",
            description="""
                Perform NBEATS forecast (Neural Bayesian Estimation of Time Series):
                https://unit8co.github.io/darts/generated_api/darts.models.forecasting.nbeats.html
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

        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            target_dataset=True,
            n_days=True,
            target_column=True,
            train_split=True,
            input_chunk_length=True,
            output_chunk_length=True,
            save_checkpoints=True,
            force_reset=True,
            model_save_name="nbeats_model",
            learning_rate=True,
            n_epochs=True,
            batch_size=800,
            past_covariates=True,
            all_past_covariates=True,
            residuals=True,
            forecast_only=True,
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
            metric=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )

        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            covariates = helpers.clean_covariates(
                ns_parser, self.datasets[ns_parser.target_dataset]
            )

            nbeats_view.display_nbeats_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                past_covariates=covariates,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.n_days,
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
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
                metric=ns_parser.metric,
            )

    @log_start_end(log=logger)
    def call_tcn(self, other_args: List[str]):
        """Process TCN command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="tcn",
            description="""
                Perform TCN forecast:
                https://unit8co.github.io/darts/generated_api/darts.models.forecasting.tcn_model.html
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

        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            target_dataset=True,
            n_days=True,
            target_column=True,
            train_split=True,
            past_covariates=True,
            all_past_covariates=True,
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
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
            metric=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )

        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            covariates = helpers.clean_covariates(
                ns_parser, self.datasets[ns_parser.target_dataset]
            )

            tcn_view.display_tcn_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                past_covariates=covariates,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.n_days,
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
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
                metric=ns_parser.metric,
            )

    @log_start_end(log=logger)
    def call_regr(self, other_args: List[str]):
        """Process REGR command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="regr",
            description="""
                Perform a regression forecast:
                https://unit8co.github.io/darts/generated_api/darts.models.forecasting.regression_model.html
            """,
        )

        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            output_chunk_length=True,
            train_split=True,
            past_covariates=True,
            all_past_covariates=True,
            n_days=True,
            target_dataset=True,
            target_column=True,
            lags=True,
            residuals=True,
            forecast_only=True,
            start=True,
            end=True,
            naive=True,
            explainability_raw=True,
            export_pred_raw=True,
            metric=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )

        if ns_parser:
            # check proper file name is provided
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            covariates = helpers.clean_covariates(
                ns_parser, self.datasets[ns_parser.target_dataset]
            )

            regr_view.display_regression(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                past_covariates=covariates,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.n_days,
                output_chunk_length=ns_parser.output_chunk_length,
                lags=ns_parser.lags,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                explainability_raw=ns_parser.explainability_raw,
                export_pred_raw=ns_parser.export_pred_raw,
                metric=ns_parser.metric,
            )

    @log_start_end(log=logger)
    def call_linregr(self, other_args: List[str]):
        """Process LINREGR command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="linregr",
            description="""
                Perform a linear regression forecast:
                https://unit8co.github.io/darts/generated_api/darts.models.forecasting.linear_regression_model.html
            """,
        )
        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            lags=True,
            output_chunk_length=True,
            train_split=True,
            past_covariates=True,
            all_past_covariates=True,
            target_column=True,
            n_days=True,
            target_dataset=True,
            residuals=True,
            forecast_only=True,
            start=True,
            end=True,
            naive=True,
            explainability_raw=True,
            export_pred_raw=True,
            metric=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )

        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            covariates = helpers.clean_covariates(
                ns_parser, self.datasets[ns_parser.target_dataset]
            )

            linregr_view.display_linear_regression(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                past_covariates=covariates,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.n_days,
                output_chunk_length=ns_parser.output_chunk_length,
                lags=ns_parser.lags,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                explainability_raw=ns_parser.explainability_raw,
                export_pred_raw=ns_parser.export_pred_raw,
                metric=ns_parser.metric,
            )

    @log_start_end(log=logger)
    def call_brnn(self, other_args: List[str]):
        """Process BRNN command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="brnn",
            description="""
                Perform BRNN forecast (Vanilla RNN, LSTM, GRU):
                https://unit8co.github.io/darts/generated_api/darts.models.forecasting.block_rnn_model.html
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
        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
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
            train_split=True,
            past_covariates=True,
            all_past_covariates=True,
            target_dataset=True,
            n_days=True,
            target_column=True,
            residuals=True,
            forecast_only=True,
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
            metric=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )

        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            covariates = helpers.clean_covariates(
                ns_parser, self.datasets[ns_parser.target_dataset]
            )

            brnn_view.display_brnn_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                past_covariates=covariates,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.n_days,
                input_chunk_length=ns_parser.input_chunk_length,
                output_chunk_length=ns_parser.output_chunk_length,
                model_type=ns_parser.model_type,
                n_rnn_layers=ns_parser.n_rnn_layers,
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
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
                metric=ns_parser.metric,
            )

    @log_start_end(log=logger)
    def call_trans(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="trans",
            description="""
                Perform Transformer Forecast:
                https://unit8co.github.io/darts/generated_api/darts.models.forecasting.transformer_model.html
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
            help="The number of encoder layers in the encoder.",
        )
        parser.add_argument(
            "--num_decoder_layers",
            action="store",
            dest="num_decoder_layers",
            default=3,
            type=check_positive,
            help="The number of decoder layers in the encoder.",
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
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            n_days=True,
            target_column=True,
            target_dataset=True,
            past_covariates=True,
            all_past_covariates=True,
            train_split=True,
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
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
            metric=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )
        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            covariates = helpers.clean_covariates(
                ns_parser, self.datasets[ns_parser.target_dataset]
            )

            trans_view.display_trans_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                past_covariates=covariates,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.n_days,
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
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
                metric=ns_parser.metric,
            )

    @log_start_end(log=logger)
    def call_tft(self, other_args: List[str]):
        """Process TFT command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="tft",
            description="""
                Perform TFT forecast (Temporal Fusion Transformer):
                https://unit8co.github.io/darts/generated_api/darts.models.forecasting.tft_model.html
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

        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            save_checkpoints=True,
            target_dataset=True,
            n_days=True,
            force_reset=True,
            model_save_name="tft_model",
            train_split=True,
            hidden_size=16,
            batch_size=32,
            n_epochs=True,
            dropout=0.1,
            input_chunk_length=True,
            output_chunk_length=True,
            past_covariates=True,
            all_past_covariates=True,
            target_column=True,
            residuals=True,
            forecast_only=True,
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
            metric=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )

        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            covariates = helpers.clean_covariates(
                ns_parser, self.datasets[ns_parser.target_dataset]
            )

            tft_view.display_tft_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                past_covariates=covariates,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.n_days,
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
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
                metric=ns_parser.metric,
            )

    @log_start_end(log=logger)
    def call_nhits(self, other_args: List[str]):
        """Process nhits command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="nhits",
            description="""
                Perform nhits forecast:
                https://unit8co.github.io/darts/generated_api/darts.models.forecasting.tft_model.html
            """,
        )
        parser.add_argument(
            "--num-stacks",
            dest="num_stacks",
            type=check_positive,
            default=3,
            help="The number of stacks that make up the model",
        )
        parser.add_argument(
            "--num-blocks",
            dest="num_blocks",
            type=check_positive,
            default=1,
            help="The number of blocks making up every stack",
        )
        parser.add_argument(
            "--num-layers",
            dest="num_layers",
            type=check_positive,
            default=2,
            help="The number of fully connected layers",
        )
        parser.add_argument(
            "--layer_widths",
            dest="layer_widths",
            type=check_positive,
            default=512,
            help="The number of neurons in each layer",
        )
        parser.add_argument(
            "--activation",
            dest="activation",
            type=str,
            default="ReLU",
            choices=[
                "ReLU",
                "RReLU",
                "PReLU",
                "Softplus",
                "Tanh",
                "SELU",
                "LeakyReLU",
                "Sigmoid",
            ],
            help="The desired activation",
        )
        parser.add_argument(
            "--max_pool_1d",
            action="store_true",
            dest="maxpool1d",
            default=True,
            help="Whether to use max_pool_1d or AvgPool1d",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            save_checkpoints=True,
            target_dataset=True,
            n_days=True,
            force_reset=True,
            model_save_name="nhits_model",
            train_split=True,
            dropout=0.1,
            input_chunk_length=True,
            output_chunk_length=True,
            batch_size=32,
            n_epochs=True,
            past_covariates=True,
            all_past_covariates=True,
            target_column=True,
            residuals=True,
            forecast_only=True,
            start=True,
            end=True,
            naive=True,
            export_pred_raw=True,
            metric=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )

        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            covariates = helpers.clean_covariates(
                ns_parser, self.datasets[ns_parser.target_dataset]
            )

            nhits_view.display_nhits_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                n_predict=ns_parser.n_days,
                target_column=ns_parser.target_column,
                past_covariates=covariates,
                train_split=ns_parser.train_split,
                forecast_horizon=ns_parser.n_days,
                input_chunk_length=ns_parser.input_chunk_length,
                output_chunk_length=ns_parser.output_chunk_length,
                num_stacks=ns_parser.num_stacks,
                num_blocks=ns_parser.num_blocks,
                num_layers=ns_parser.num_layers,
                layer_widths=ns_parser.layer_widths,
                activation=ns_parser.activation,
                max_pool_1d=ns_parser.maxpool1d,
                batch_size=ns_parser.batch_size,
                n_epochs=ns_parser.n_epochs,
                dropout=ns_parser.dropout,
                model_save_name=ns_parser.model_save_name,
                force_reset=ns_parser.force_reset,
                save_checkpoints=ns_parser.save_checkpoints,
                export=ns_parser.export,
                residuals=ns_parser.residuals,
                forecast_only=ns_parser.forecast_only,
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                naive=ns_parser.naive,
                export_pred_raw=ns_parser.export_pred_raw,
                metric=ns_parser.metric,
            )

    @log_start_end(log=logger)
    def call_anom(self, other_args: List[str]):
        """Process ANOM command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="anom",
            description="""
                Perform a Quantile Anomaly detection on a given dataset:
                https://unit8co.github.io/darts/generated_api/darts.ad.detectors.quantile_detector.html
            """,
        )

        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        parser = self.add_standard_args(
            parser,
            train_split=True,
            target_column=True,
            target_dataset=True,
            forecast_only=True,
            start=True,
            end=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )

        if ns_parser:
            if not helpers.check_parser_input(ns_parser, self.datasets):
                return

            anom_view.display_anomaly_detection(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                target_column=ns_parser.target_column,
                train_split=ns_parser.train_split,
                export=ns_parser.export,
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
            )

    @log_start_end(log=logger)
    def call_whisper(self, other_args: List[str]):
        """Utilize Whisper Model to transcribe a video. Currently only supports Youtube URLS"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="whisper",
            description="""
                Utilize Whisper Model to transcribe a video. Currently only supports Youtube URLS:
                https://github.com/openai/whisper
            """,
        )
        parser.add_argument(
            "--video",
            dest="video",
            type=str,
            default="",
            help="video URLs to transcribe",
        )
        parser.add_argument(
            "--model_name",
            dest="model_name",
            choices=whisper.available_models(),
            default="base",
            help="name of the Whisper model to use",
        )
        parser.add_argument(
            "--subtitles_format",
            dest="subtitles_format",
            type=str,
            choices=["vtt", "srt"],
            help="the subtitle format to output",
        )
        parser.add_argument(
            "--verbose",
            dest="verbose",
            type=str2bool,
            default=False,
            help="Whether to print out the progress and debug messages",
        )
        parser.add_argument(
            "--task",
            dest="task",
            type=str,
            choices=["transcribe", "translate"],
            help="whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')",
        )
        parser.add_argument(
            "--language",
            dest="language",
            type=str,
            default=None,
            choices=sorted(LANGUAGES.keys())
            + sorted([k.title() for k in TO_LANGUAGE_CODE.keys()]),
            help="language spoken in the audio, skip to perform language detection",
        )
        parser.add_argument(
            "--breaklines",
            dest="breaklines",
            type=int,
            default=0,
            help="Whether to break lines into a bottom-heavy pyramid shape if line length exceeds N characters. 0 disables line breaking.",
        )
        parser.add_argument(
            "--save",
            dest="save",
            type=str,
            default=get_current_user().preferences.USER_FORECAST_WHISPER_DIRECTORY,
            help="Directory to save the subtitles file",
        )

        parser = self.add_standard_args(
            parser,
        )
        if other_args and "--video" not in other_args:
            other_args.insert(0, "--video")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
        )

        if ns_parser:
            if ns_parser.save is None:
                ns_parser.save = (
                    get_current_user().preferences.USER_FORECAST_WHISPER_DIRECTORY
                )

            whisper_model.transcribe_and_summarize(
                video=ns_parser.video,
                model_name=ns_parser.model_name,
                subtitles_format=ns_parser.subtitles_format,
                verbose=ns_parser.verbose,
                task=ns_parser.task,
                language=ns_parser.language,
                breaklines=ns_parser.breaklines,
                output_dir=ns_parser.save,
            )

    # TimeGPT Model
    @log_start_end(log=logger)
    def call_timegpt(self, other_args: List[str]):
        """Process expo command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
            prog="timegpt",
            description="""
                TODO: Update me
            """,
        )
        parser.add_argument(
            "--horizon",
            action="store",
            dest="horizon",
            type=check_positive,
            default=12,
            help="Forecasting horizon",
        )
        parser.add_argument(
            "--freq",
            action="store",
            dest="freq",
            choices=["H", "D", "W", "M", "MS", "B"],
            default=None,
            help="Frequency of the data.",
        )
        parser.add_argument(
            "--finetune",
            action="store",
            dest="finetune",
            type=check_non_negative,
            default=0,
            help="Number of steps used to finetune TimeGPT in the new data.",
        )
        parser.add_argument(
            "--ci",
            action="store",
            dest="confidence",
            type=check_positive_float_list,
            default=[80, 90],
            help="Number of steps used to finetune TimeGPT in the new data.",
        )
        parser.add_argument(
            "--cleanex",
            action="store_false",
            help="Clean exogenous signal before making forecasts using TimeGPT.",
            dest="cleanex",
            default=True,
        )
        parser.add_argument(
            "--timecol",
            action="store",
            dest="timecol",
            default="ds",
            type=str,
            help="Dataframe column that represents datetime",
        )
        parser.add_argument(
            "--targetcol",
            action="store",
            dest="targetcol",
            default="y",
            type=str,
            help="Dataframe column that represents the target to forecast for",
        )
        parser.add_argument(
            "--sheet-name",
            help="The name of the sheet to export to when type is XLSX.",
            dest="sheet_name",
            type=str,
            default="",
        )
        parser.add_argument(
            "--datefeatures",
            help="Specifies which date attributes have highest weight according to model.",
            dest="date_features",
            type=check_list_values(["auto", "year", "month", "week", "day", "weekday"]),
            default=[],
        )
        parser = self.add_standard_args(
            parser,
            target_dataset=True,
            target_column=True,
            start=True,
            end=True,
            residuals=True,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_FIGURES_ALLOWED,
        )
        if ns_parser:
            timegpt_view.display_timegpt_forecast(
                data=self.datasets[ns_parser.target_dataset],
                dataset_name=ns_parser.target_dataset,
                time_col=ns_parser.timecol,
                target_col=ns_parser.targetcol,
                forecast_horizon=ns_parser.horizon,
                freq=ns_parser.freq,
                levels=ns_parser.confidence,
                finetune_steps=ns_parser.finetune,
                clean_ex_first=ns_parser.cleanex,
                export=ns_parser.export,
                sheet_name=ns_parser.sheet_name,
                start_date=ns_parser.s_start_date,
                end_date=ns_parser.s_end_date,
                residuals=ns_parser.residuals,
                date_features=ns_parser.date_features,
            )
