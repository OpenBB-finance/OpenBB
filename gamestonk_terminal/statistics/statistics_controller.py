"""Custom Data Controller Module"""
__docformat__ = "numpy"
# pylint: disable=too-many-function-args
# pylint: disable=inconsistent-return-statements

import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
from prompt_toolkit.completion import NestedCompleter

import gamestonk_terminal.statistics.regression_model
import gamestonk_terminal.statistics.regression_view
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    EXPORT_ONLY_FIGURES_ALLOWED,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
)
from gamestonk_terminal.helper_funcs import (
    print_rich_table,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.statistics import statistics_model, statistics_view

logger = logging.getLogger(__name__)


# pylint:disable=import-outside-toplevel


class StatisticsController(BaseController):
    """Statistics class"""

    CHOICES_COMMANDS: List[str] = [
        "load",
        "index",
        "clear",
        "plot",
        "show",
        "info",
        "norm",
        "root",
        "granger",
        "coint",
        "ols",
        "auto",
    ]
    CHOICES_MENUS: List[str] = ["qa", "pred"]
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
    PATH = "/statistics/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)
        self.files: List[str] = list()
        self.datasets: Dict[pd.DataFrame, Any] = dict()
        self.regression: Dict[pd.DataFrame, Any] = dict()
        self.file_types = ["csv", "xlsx"]
        self.DATA_FILES = {
            filepath.name: filepath
            for file_type in self.file_types
            for filepath in Path("exports").rglob(f"*.{file_type}")
            if filepath.is_file()
        }

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["load"] = {c: None for c in self.DATA_FILES.keys()}
            choices["show"] = {c: None for c in self.files}
            self.choices = choices
            self.completer = NestedCompleter.from_nested_dict(choices)

    def update_runtime_choices(self):
        if session and gtff.USE_PROMPT_TOOLKIT:
            dataset_columns = {
                f"{column}-{dataset}": {column: None, dataset: None}
                for dataset, dataframe in self.datasets.items()
                for column in dataframe.columns
            }

            for feature in ["plot", "norm", "root", "granger", "cointegration", "ols"]:
                self.choices[feature] = dataset_columns
            for feature in ["index", "show", "info", "clear"]:
                self.choices[feature] = {c: None for c in self.files}

        self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help"""
        help_text = f"""[cmds]
    load            load in custom data sets
    index           set (multi)index based on columns
    clear           remove a dataset[/cmds]

[param]Current file:[/param]    {self.files or None}[cmds]

Dataset Discovery
    show            show portion of loaded data
    plot            plot data from a dataset
    info            show descriptive statistics

General Tests
    norm            perform normality tests on a column of a dataset
    root            perform unitroot tests (ADF & KPSS) on a column of a dataset
    granger         perform granger causality tests on two timeseries.
    coint           perform co-integration test on two timeseries

Regression Analysis
    ols             fit a (multi) linear regression model
    auto            perform autocorrelation test on the residuals of the regression[/cmds]
        """
        console.print(text=help_text, menu="Statistics")

    def call_load(self, other_args: List[str]):
        """Process load"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load custom data set into a dataframe",
        )
        parser.add_argument(
            "-f",
            "--file",
            help="File to load in",
            type=str,
        )

        parser.add_argument(
            "-n",
            "--name",
            help="The name or abbreviation you want to give to the database",
            type=str,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if ns_parser.file in self.DATA_FILES:
                file = self.DATA_FILES[ns_parser.file]
            else:
                file = ns_parser.file

            data = statistics_model.load(file, self.file_types)

            if not data.empty:
                data.columns = data.columns.map(lambda x: x.lower())
                for col in data.columns:
                    if col in ["date", "time", "timestamp"]:  # Could be others?
                        data[col] = pd.to_datetime(data[col])
                        data = data.set_index(col)

                if ns_parser.name:
                    self.files.append(ns_parser.name)
                    self.datasets[ns_parser.name] = data
                else:
                    self.files.append(ns_parser.file)
                    self.datasets[ns_parser.file] = data

                self.update_runtime_choices()

                console.print("")

    def call_index(self, other_args: List[str]):
        """Process index"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="index",
            description="Set (multi)index for the dataset",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            nargs="+",
            help="The first argument is the name of the database, further arguments are "
            "the columns you wish to set a index",
        )

        parser.add_argument(
            "-i",
            "--index",
            help="Save the original index as a column",
            action="store_true",
            dest="index",
            default=False,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser.name:
            name = ns_parser.name[0]
            columns = ns_parser.name[1:]

            print(columns)

            dataset = self.datasets[name]

            for column in columns:
                if column not in dataset.columns:
                    return console.print(
                        f"The column '{column}' is not available in the dataset {name}."
                        f"Please choose one of the following: {', '.join(dataset.columns)}"
                    )

            if ns_parser.index:
                dataset = dataset.reset_index()

            self.datasets[name] = dataset.set_index(columns)

            self.update_runtime_choices()

            console.print("")

    def call_clear(self, other_args: List[str]):
        """Process clear"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="clear",
            description="Remove a dataset from the list",
        )

        parser.add_argument(
            "-n",
            "--name",
            help="The name of the dataset you want to clear",
            type=str,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if ns_parser.name in self.datasets:
                del self.datasets[ns_parser.name]
                self.files.remove(ns_parser.name)
            else:
                console.print(f"{ns_parser.name} is not a loaded dataset.")
            self.update_runtime_choices()

        console.print("")

    def call_plot(self, other_args: List[str]):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="Plot 2 columns of loaded data",
        )
        parser.add_argument(
            "-c",
            "--column",
            help="Column to plot along y",
            dest="column",
            type=str,
            choices=self.choices["plot"],
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )

        if ns_parser and ns_parser.column:
            column, dataset = self.choices["plot"][ns_parser.column].keys()
            data = self.datasets[dataset]

            statistics_view.custom_plot(
                data,
                dataset,
                column,
                export=ns_parser.export,
            )

        console.print("")

    def call_show(self, other_args: List[str]):
        """Process show command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="show",
            description="Show loaded dataframe",
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
            "-l",
            "--limit",
            type=int,
            dest="limit",
            help="The amount of data you wish to show",
            default=10,
        )

        parser.add_argument(
            "-s", "--sortcol", nargs="+", type=str, dest="sortcol", default=""
        )
        parser.add_argument(
            "-a", "--ascend", action="store_true", default=False, dest="ascend"
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser and ns_parser.name:
            df = self.datasets[ns_parser.name]

            if ns_parser.name in self.datasets and self.datasets[ns_parser.name].empty:
                return console.print(
                    f"[red]No data available for {ns_parser.name}.[/red]\n"
                )
            if ns_parser.sortcol:
                sort_column = " ".join(ns_parser.sortcol)
                if sort_column not in self.datasets[ns_parser.name].columns:
                    console.print(
                        f"[red]{sort_column} not a valid column. Showing without sorting.\n[/red]"
                    )
                else:
                    df = df.sort_values(by=sort_column, ascending=ns_parser.ascend)

            print_rich_table(
                df.head(ns_parser.limit),
                headers=list(df.columns),
                show_index=True,
                title=ns_parser.name,
            )

        return console.print("")

    def call_info(self, other_args: List[str]):
        """Process info command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="info",
            description="Show information of custom data.",
        )

        parser.add_argument(
            "-n",
            "--name",
            type=str,
            choices=self.files,
            dest="name",
            help="The name of the database you want to show data for",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser and ns_parser.name:
            if ns_parser.name in self.datasets and self.datasets[ns_parser.name].empty:
                console.print(f"[red]No data available for {ns_parser.name}.[/red]\n")
            else:
                df = self.datasets[ns_parser.name].describe()
                print_rich_table(
                    df, headers=list(df.columns), show_index=True, title=ns_parser.name
                )

        console.print("")

    def call_norm(self, other_args: List[str]):
        """Process normality command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="norm",
            description="Show information of custom data.",
        )

        parser.add_argument(
            "-c",
            "--column",
            type=str,
            choices=self.choices["norm"],
            dest="column",
            help="The column and name of the database you want test normality for",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser and ns_parser.column:
            column, dataset = self.choices["norm"][ns_parser.column].keys()

            if dataset in self.datasets:
                if isinstance(self.datasets[dataset], pd.Series):
                    data = self.datasets[dataset]
                elif isinstance(self.datasets[dataset], pd.DataFrame):
                    data = self.datasets[dataset][column]
                else:
                    return console.print(
                        f"The type of {dataset} ({type(dataset)} is not an option."
                    )
            else:
                return console.print(f"Can not find {dataset}. Did you load the data?")

            statistics_view.display_norm(data, dataset, column, ns_parser.export)

    def call_root(self, other_args: List[str]):
        """Process unitroot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="root",
            description="Show unit root tests of a column of a dataset",
        )

        parser.add_argument(
            "-c",
            "--column",
            type=str,
            choices=self.choices["root"],
            dest="column",
            help="The column and name of the database you want test unitroot for",
        )

        parser.add_argument(
            "-r",
            "--fuller_reg",
            help="Type of regression. Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order",
            choices=["c", "ct", "ctt", "nc"],
            default="c",
            type=str,
            dest="fuller_reg",
        )
        parser.add_argument(
            "-k",
            "--kps_reg",
            help="Type of regression. Can be ‘c’,’ct'",
            choices=["c", "ct"],
            type=str,
            dest="kpss_reg",
            default="c",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser and ns_parser.column:
            column, dataset = self.choices["root"][ns_parser.column].keys()

            if isinstance(self.datasets[dataset], pd.Series):
                data = self.datasets[dataset]
            elif isinstance(self.datasets[dataset], pd.DataFrame):
                data = self.datasets[dataset][column]

            df = statistics_model.get_unitroot(
                data, ns_parser.fuller_reg, ns_parser.kpss_reg
            )
            print_rich_table(
                df,
                headers=list(df.columns),
                show_index=True,
                title=f"Unitroot Test [Column: {column} | Dataset: {dataset}]",
            )

        console.print("")

    def call_granger(self, other_args: List[str]):
        """Process granger command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="granger",
            description="Show Granger causality between two timeseries",
        )

        parser.add_argument(
            "-y",
            "--time_series_y",
            help="The time series that is assumed to be Granger-caused by x",
            choices=self.choices["granger"],
            dest="y",
        )

        parser.add_argument(
            "-x",
            "--time_series_x",
            help="The time series that is assumed to Granger-cause y",
            choices=self.choices["granger"],
            dest="x",
        )
        parser.add_argument(
            "-l",
            "--lags",
            help="How many lags should be included",
            type=int,
            dest="lags",
            default=3,
        )

        parser.add_argument(
            "-cl",
            "--confidence",
            help="Set the confidence level",
            type=int,
            dest="confidence",
            default=0.05,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-y")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser and ns_parser.y and ns_parser.x:
            column_y, dataset_y = self.choices["granger"][ns_parser.y].keys()
            column_x, dataset_x = self.choices["granger"][ns_parser.x].keys()

            statistics_view.display_granger(
                self.datasets[dataset_y][column_y],
                self.datasets[dataset_x][column_x],
                ns_parser.lags,
                ns_parser.confidence,
                ns_parser.export,
            )

    def call_coint(self, other_args: List[str]):
        """Process coint command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="coint",
            description="Show co-integration between two timeseries",
        )

        parser.add_argument(
            "-ts",
            "--time_series",
            help="The first time series",
            choices=self.choices["cointegration"],
            dest="ts",
            nargs="+",
        )

        parser.add_argument(
            "-p",
            "--plot",
            help="Plot Z-Values",
            dest="plot",
            action="store_true",
            default=False,
        )

        parser.add_argument(
            "-s",
            "--significant",
            help="Show only companies that have p-values lower than this percentage",
            dest="significant",
            type=float,
            default=0,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-ts")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser and ns_parser.ts:

            datasets = {}
            for stock in ns_parser.ts:
                column, dataset = self.choices["cointegration"][stock].keys()
                datasets[stock] = self.datasets[dataset][column]

            statistics_view.display_cointegration_test(
                datasets, ns_parser.significant, ns_parser.plot, ns_parser.export
            )

    def call_ols(self, other_args: List[str]):
        """Process unitroot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="root",
            description="Show unit root tests of a column of a dataset",
        )

        parser.add_argument(
            "-r",
            "--regression",
            nargs="+",
            type=str,
            choices=self.choices["ols"],
            dest="regression",
            help="The regression you would like to perform",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-r")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser and ns_parser.regression:
            (
                self.regression["data"],
                self.regression["dependent"],
                self.regression["independent"],
                self.regression["model"],
            ) = gamestonk_terminal.statistics.regression_model.get_ols(
                ns_parser.regression, self.datasets, self.choices["ols"]
            )

            print(self.regression["model"].summary())

    def call_auto(self, other_args: List[str]):
        """Process unitroot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="root",
            description="Show unit root tests of a column of a dataset",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            dependent_variable = self.regression["data"][self.regression["dependent"]]

            gamestonk_terminal.statistics.regression_view.display_auto(
                dependent_variable, self.regression["model"].resid, ns_parser.export
            )
