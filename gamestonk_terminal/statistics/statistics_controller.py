"""Statistics Controller Module"""
__docformat__ = "numpy"

# pylint: disable=too-many-function-args
# pylint: disable=inconsistent-return-statements
# pylint: disable=too-many-lines
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-lines
# pylint: disable=too-many-branches

import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any
import os

import numpy as np
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
    export_data,
)
from gamestonk_terminal.helper_funcs import (
    print_rich_table,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.statistics import statistics_model, statistics_view

logger = logging.getLogger(__name__)


class StatisticsController(BaseController):
    """Statistics class"""

    CHOICES_COMMANDS: List[str] = [
        "load",
        "export",
        "remove",
        "options",
        "plot",
        "show",
        "info",
        "index",
        "clean",
        "modify",
        "norm",
        "root",
        "granger",
        "coint",
        "ols",
        "dwat",
        "panel",
        "compare",
        "bgod",
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
        self.regression: Dict[Any[Dict, Any], Any] = dict()

        for regression in ["OLS", "POLS", "BOLS", "RE", "FE", "FDOLS"]:
            self.regression[regression] = {
                "data": {},
                "independent": {},
                "dependent": {},
                "model": {},
            }

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

            for feature in [
                "general",
                "plot",
                "norm",
                "root",
                "granger",
                "cointegration",
                "regressions",
            ]:
                self.choices[feature] = dataset_columns
            for feature in ["export", "options", "show", "info", "clear", "index"]:
                self.choices[feature] = {c: None for c in self.files}

        self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help"""
        help_text = f"""[cmds]
    load            load in custom data sets
    export          export a dataset
    remove          remove a dataset
    options         show available column-dataset options[/cmds]

[param]Loaded files:[/param]    {", ".join(self.files) or None}[cmds]

Exploration
    show            show portion of loaded data
    plot            plot data from a dataset
    info            show descriptive statistics
    index           set (multi)index based on columns
    clean           clean the dataset by filling or dropping NaNs
    modify          combine columns of datasets and delete or rename columns

Timeseries
    ols             fit a (multi) linear regression model
    norm            perform normality tests on a column of a dataset
    root            perform unitroot tests (ADF & KPSS) on a column of a dataset
    dwat            perform Durbin-Watson autocorrelation test on the residuals of the regression
    granger         perform granger causality tests on two timeseries.
    coint           perform co-integration test on two timeseries

Panel Data
    panel           Estimate model based on various regression techniques.
    compare         Compare results of all estimated models
    bgod            perform Breusch-Godfrey autocorrelation tests on an OLS regression model
[/cmds]
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
            help="File to load in and the alias you wish to give to the dataset",
            nargs="+",
            type=str,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if len(ns_parser.file) == 1:
                console.print(
                    f"Please provide an alias to the dataset (format: <file> <alias>). For example: "
                    f"'load {ns_parser.file[0] if len(ns_parser.file) > 0 else 'TSLA.xlsx'} dataset'"
                )
            else:
                file, alias = ns_parser.file

                if file in self.DATA_FILES:
                    file = self.DATA_FILES[file]

                data = statistics_model.load(file, self.file_types)

                if not data.empty:
                    data.columns = data.columns.map(
                        lambda x: x.lower().replace(" ", "_")
                    )
                    for col in data.columns:
                        if col in ["date", "time", "timestamp", "quarter"]:
                            data[col] = pd.to_datetime(data[col])
                            data = data.set_index(col)

                    self.files.append(alias)
                    self.datasets[alias] = data

                    self.update_runtime_choices()

                    console.print("")

    def call_export(self, other_args: List[str]):
        """Process export command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="export",
            description="Export dataset to Excel",
        )

        parser.add_argument(
            "-n",
            "--name",
            help="The name of the dataset you wish to export",
            type=str,
        )

        parser.add_argument(
            "-t",
            "--type",
            help="The file type you wish to export to",
            choices=self.file_types,
            type=str,
            default="xlsx",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        export_data(
            ns_parser.type,
            os.path.dirname(os.path.abspath(__file__)),
            ns_parser.name,
            self.datasets[ns_parser.name],
        )

        console.print("")

    def call_remove(self, other_args: List[str]):
        """Process clear"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="remove",
            description="Remove a dataset from the loaded dataset list",
        )

        parser.add_argument(
            "-n",
            "--name",
            help="The name of the dataset you want to remove",
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

    def call_options(self, other_args: List[str]):
        """Process options command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="options",
            description="Show the column-dataset combination that can be entered within the functions.",
        )

        parser.add_argument(
            "-n",
            "--name",
            type=str,
            choices=self.files,
            dest="name",
            help="The dataset you would like to show the options for",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            option_tables = {}
            if ns_parser.name:
                columns = self.datasets[ns_parser.name].columns
                option_tables[ns_parser.name] = pd.DataFrame(
                    {
                        "dataset": [ns_parser.name] * len(columns),
                        "column": columns,
                        "option": [f"{column}-{ns_parser.name}" for column in columns],
                    }
                )
            else:
                for dataset, data_values in self.datasets.items():
                    columns = data_values.columns
                    option_tables[dataset] = pd.DataFrame(
                        {
                            "dataset": [dataset] * len(columns),
                            "column": columns,
                            "option": [f"{column}-{dataset}" for column in columns],
                        }
                    )

            for dataset, data_values in option_tables.items():
                print_rich_table(
                    data_values,
                    headers=list(data_values.columns),
                    show_index=False,
                    title=f"Options for {dataset}",
                )
                console.print("")

    def call_plot(self, other_args: List[str]):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="Plot data based on the index.ind",
        )
        parser.add_argument(
            "-c",
            "--column",
            help="Column to plot along the index",
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
            "-l",
            "--limit",
            type=int,
            dest="limit",
            help="The amount of data you wish to show",
            default=10,
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
            description="Show the descriptive statistics of the dataset",
        )

        parser.add_argument(
            "-n",
            "--name",
            type=str,
            choices=self.files,
            dest="name",
            help="The name of the database you want to show the descriptive statistics for",
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

    def call_index(self, other_args: List[str]):
        """Process index"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="index",
            description="Set a (multi) index for the dataset",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            nargs="+",
            help="The first argument is the name of the database, further arguments are "
            "the columns you wish to set as index",
        )

        parser.add_argument(
            "-i",
            "--ignore",
            help="Whether to allow for making adjustments to the dataset to align it with the use case for "
            "Timeseries and Panel Data regressions",
            dest="ignore",
            action="store_true",
            default=False,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser.name:
            name = ns_parser.name[0]
            columns = ns_parser.name[1:]

            dataset = self.datasets[name]

            if not pd.Index(np.arange(0, len(dataset))).equals(dataset.index):
                console.print("As an index has been set, resetting the current index.")
                dataset = dataset.reset_index()

            for column in columns:
                if column not in dataset.columns:
                    return console.print(
                        f"The column '{column}' is not available in the dataset {name}."
                        f"Please choose one of the following: {', '.join(dataset.columns)}"
                    )

            if (
                len(columns) > 1
                and dataset[columns[0]].isnull().any()
                and not ns_parser.ignore
            ):
                null_values = dataset[dataset[columns[0]].isnull()]
                console.print(
                    f"The column '{columns[0]}' contains {len(null_values)} NaN values. As multiple columns are "
                    f"provided, it is assumed this column represents entities (i), the NaN values are "
                    f"forward filled. Use the -i argument to disable this."
                )
                dataset[columns[0]] = dataset[columns[0]].fillna(method="ffill")
            if not isinstance(dataset[columns[-1]], pd.DatetimeIndex):
                dataset[columns[-1]] = pd.DatetimeIndex(dataset[columns[-1]])

                if dataset[columns[-1]].isnull().any() and not ns_parser.ignore:
                    # This checks whether NaT exists within the DataFrame
                    null_values = dataset[dataset[columns[-1]].isnull()]
                    console.print(
                        f"The time index '{columns[-1]}' contains {len(null_values)} "
                        f"NaTs which are removed from the dataset. Use the -i argument to disable this."
                    )
                    dataset = dataset[dataset[columns[-1]].notnull()]

            self.datasets[name] = dataset.set_index(columns)

            self.update_runtime_choices()

            console.print("")

    def call_clean(self, other_args: List[str]):
        """Process clean"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="clean",
            description="Clean a dataset by filling and dropping NaN values.",
        )

        parser.add_argument(
            "-n",
            "--name",
            help="The name of the dataset you want to clean up",
            dest="name",
            type=str,
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
            "-d",
            "--drop",
            help="The method of dropping NaNs. This either has the option rdrop (drop rows that contain NaNs) "
            "or cdrop (drop columns that contain NaNs)",
            dest="drop",
            choices=["rdrop", "cdrop"],
            default="",
        )

        parser.add_argument(
            "-l",
            "--limit",
            help="The max amount of columns/rows backward filled or forward filled that have NaNs or "
            "the max amount of columns/rows that have NaNs before being dropped.",
            dest="limit",
            type=int,
            default=5,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            self.datasets[ns_parser.name] = statistics_model.clean(
                self.datasets[ns_parser.name],
                ns_parser.fill,
                ns_parser.drop,
                ns_parser.limit,
            )

        console.print("")

    def call_modify(self, other_args: List[str]):
        """Process modify"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="modify",
            description="Modify a dataset by adding, removing or renaming columns. This also has the "
            "possibility to combine DataFrames together.",
        )

        parser.add_argument(
            "-a",
            "--add",
            help="Add columns to your dataframe with the option to use formulas. Use format: "
            "<column>-<dataset> <column-dataset> <sign> <criteria or column-dataset>. "
            "Two examples: high_revenue-thesis revenue-thesis > 1000 or debt_ratio-dataset "
            "debt-dataset div assets-dataset2",
            dest="add",
            nargs=4,
            type=str,
        )

        parser.add_argument(
            "-d",
            "--delete",
            help="The columns you want to delete from a dataset. Use format: <column-dataset>.",
            dest="delete",
            nargs="+",
            type=str,
        )

        parser.add_argument(
            "-c",
            "--combine",
            help="The columns you want to add to a dataset, the first argument is the dataset that you wish "
            "to place these columns in. Use format: <dataset> <column-dataset2> <column-<dataset3>",
            dest="combine",
            nargs="+",
            type=str,
        )

        parser.add_argument(
            "-r",
            "--rename",
            help="The columns you want to rename from a dataset. "
            "Use format: dataset OLD_COLUMN NEW_COLUMN",
            dest="rename",
            nargs=3,
            type=str,
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if ns_parser.add:
                new_column, dataset = ns_parser.add[0].split("-")
                existing_column, dataset2 = ns_parser.add[1].split("-")

                for sign, operator in self.signs.items():
                    if sign == ns_parser.add[2]:
                        ns_parser.add[2] = operator

                if dataset not in self.datasets:
                    console.print(
                        f"Not able to find the dataset {dataset}. Please choose one of "
                        f"the following: {', '.join(self.datasets)}"
                    )
                elif dataset2 not in self.datasets:
                    console.print(
                        f"Not able to find the dataset {dataset2}. Please choose one of "
                        f"the following: {', '.join(self.datasets)}"
                    )
                elif existing_column not in self.datasets[dataset2]:
                    console.print(
                        f"Not able to find the column {existing_column}. Please choose one of "
                        f"the following: {', '.join(self.datasets[dataset2].columns)}"
                    )
                elif len(ns_parser.add[3].split("-")) > 1:
                    existing_column2, dataset3 = ns_parser.add[3].split("-")

                    if dataset3 not in self.datasets:
                        console.print(
                            f"Not able to find the dataset {dataset3}. Please choose one of "
                            f"the following: {', '.join(self.datasets)}"
                        )

                    elif existing_column2 not in self.datasets[dataset3]:
                        console.print(
                            f"Not able to find the column {existing_column2}. Please choose one of "
                            f"the following: {', '.join(self.datasets[dataset3].columns)}"
                        )
                    else:
                        pd.eval(
                            f"{new_column} = self.datasets[dataset2][existing_column] "
                            f"{ns_parser.add[2]} self.datasets[dataset3][existing_column2]",
                            target=self.datasets[dataset],
                            inplace=True,
                        )
                else:
                    pd.eval(
                        f"{new_column} = self.datasets[dataset2][existing_column] "
                        f"{ns_parser.add[2]} {ns_parser.add[3]}",
                        target=self.datasets[dataset],
                        inplace=True,
                    )

            if ns_parser.delete:
                for option in ns_parser.delete:
                    column, dataset = option.split("-")

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

            if ns_parser.combine:
                if ns_parser.combine[0] not in self.datasets:
                    console.print(
                        f"Not able to find the dataset {ns_parser.combine[0]}. Please choose one of "
                        f"the following: {', '.join(self.datasets)}"
                    )
                else:
                    data = self.datasets[ns_parser.combine[0]]

                    for option in ns_parser.combine[1:]:
                        column, dataset = self.choices["general"][option].keys()

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
                            data[f"{column}_{dataset}"] = self.datasets[dataset][column]

            if ns_parser.rename:
                dataset = ns_parser.rename[0]
                column_old = ns_parser.rename[1]
                column_new = ns_parser.rename[2]

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

        console.print("")

    def call_norm(self, other_args: List[str]):
        """Process normality command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="norm",
            description="Test whether the used data is normally distributed.",
        )

        parser.add_argument(
            "-c",
            "--column",
            type=str,
            choices=self.choices["norm"],
            dest="column",
            help="The column and name of the database you want to test normality for",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser and ns_parser.column:
            column, dataset = self.choices["norm"][ns_parser.column].keys()

            if isinstance(self.datasets[dataset][column].index, pd.MultiIndex):
                console.print(
                    f"The column {column} from the dataset {dataset} is a MultiIndex. To test for normality in a "
                    f"timeseries, make sure to set a singular time index."
                )

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

        console.print("")

    def call_ols(self, other_args: List[str]):
        """Process ols command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ols",
            description="Performs an OLS regression on timeseries data.",
        )

        parser.add_argument(
            "-r",
            "--regression",
            nargs="+",
            type=str,
            choices=self.choices["regressions"],
            dest="regression",
            help="The regression you would like to perform",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-r")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser and ns_parser.regression:
            if len(ns_parser.regression) < 2:
                return console.print(
                    "Please provide both a dependent and independent variable."
                )

            (
                self.regression["OLS"]["data"],
                self.regression["OLS"]["dependent"],
                self.regression["OLS"]["independent"],
                self.regression["OLS"]["model"],
            ) = gamestonk_terminal.statistics.regression_model.get_ols(
                ns_parser.regression, self.datasets, self.choices["regressions"]
            )

    def call_root(self, other_args: List[str]):
        """Process unit root command"""
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
            help="The column and name of the database you want test unit root for",
        )

        parser.add_argument(
            "-r",
            "--fuller_reg",
            help="Type of regression. Can be ‘c’,’ct’,’ctt’,’nc’. c - Constant and t - trend order",
            choices=["c", "ct", "ctt", "nc"],
            default="c",
            type=str,
            dest="fuller_reg",
        )
        parser.add_argument(
            "-k",
            "--kps_reg",
            help="Type of regression. Can be ‘c’,’ct'. c - Constant and t - trend order",
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

            if isinstance(self.datasets[dataset][column].index, pd.MultiIndex):
                console.print(
                    f"The column {column} from the dataset {dataset} is a MultiIndex. To test for unitroot in a "
                    f"timeseries, make sure to set a singular time index."
                )
            else:
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

    def call_dwat(self, other_args: List[str]):
        """Process unitroot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dwat",
            description="Show autocorrelation tests from Durbin-Watson",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if not self.regression["OLS"]["model"]:
            console.print(
                "Please perform an OLS regression before estimating the Durbin-Watson statistic."
            )
        else:
            dependent_variable = self.regression["OLS"]["data"][
                self.regression["OLS"]["dependent"]
            ]

            gamestonk_terminal.statistics.regression_view.display_dwat(
                dependent_variable,
                self.regression["OLS"]["model"].resid,
                ns_parser.export,
            )

    def call_granger(self, other_args: List[str]):
        """Process granger command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="granger",
            description="Show Granger causality between two timeseries",
        )

        parser.add_argument(
            "-ts",
            "--timeseries",
            choices=self.choices["granger"],
            help="Requires two time series, the first time series is assumed to be Granger-caused "
            "by the second time series.",
            nargs=2,
            dest="ts",
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
            other_args.insert(0, "-ts")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser and ns_parser.ts:
            if len(ns_parser.ts) == 2:
                column_y, dataset_y = self.choices["granger"][ns_parser.ts[0]].keys()
                column_x, dataset_x = self.choices["granger"][ns_parser.ts[1]].keys()

                statistics_view.display_granger(
                    self.datasets[dataset_y][column_y],
                    self.datasets[dataset_x][column_x],
                    ns_parser.lags,
                    ns_parser.confidence,
                    ns_parser.export,
                )
            else:
                console.print(
                    "Please provide two time series for this function, "
                    "for example: granger <TS1> <TS2>"
                )

        console.print("")

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
            help="The time series you wish to test co-integration on. Can hold multiple timeseries.",
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

    def call_panel(self, other_args: List[str]):
        """Process panel command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="panel",
            description="Performs regression analysis on Panel Data. There are a multitude of options to select "
            "from to fit the needs of restrictions of the dataset.",
        )

        parser.add_argument(
            "-r",
            "--regression",
            nargs="+",
            type=str,
            choices=self.choices["regressions"],
            dest="regression",
            help="The regression you would like to perform, first variable is the dependent variable, "
            "consecutive variables the independent variables.",
        )

        parser.add_argument(
            "-t",
            "--type",
            type=str,
            choices=["pols", "re", "bols", "fe", "fdols"],
            dest="type",
            help="The type of regression you wish to perform. This can be either pols (Pooled OLS), "
            "re (Random Effects), bols (Between OLS), fe (Fixed Effects) or fdols (First Difference OLS)",
            default="pols",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-r")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser and ns_parser.regression:
            if len(ns_parser.regression) < 2:
                return console.print(
                    "Please provide both a dependent and independent variable."
                )
            for variable in ns_parser.regression:
                column, dataset = self.choices["regressions"][variable].keys()
                if not isinstance(self.datasets[dataset][column].index, pd.MultiIndex):
                    return console.print(
                        f"The column {column} from the dataset {dataset} is not a MultiIndex. Make sure you set "
                        f"the index correctly with the index command where the first level is the entity "
                        f"(e.g. Tesla Inc.) and the second level the date (e.g. 2021-03-31)"
                    )

            regression_type = ns_parser.type.upper()
            (
                self.regression[regression_type]["data"],
                self.regression[regression_type]["dependent"],
                self.regression[regression_type]["independent"],
                self.regression[regression_type]["model"],
            ) = gamestonk_terminal.statistics.regression_model.get_regressions_results(
                ns_parser.type,
                ns_parser.regression,
                self.datasets,
                self.choices["regressions"],
            )

        console.print("")

    def call_compare(self, other_args: List[str]):
        """Process compare command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="compare",
            description="Compare results between all activated regression models",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            comparison_result = (
                gamestonk_terminal.statistics.regression_model.get_comparison(
                    self.regression
                )
            )

            console.print(comparison_result)

    def call_bgod(self, other_args):
        """Process bgod command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="bgod",
            description="Show Breusch-Godfrey autocorrelation test results.",
        )

        parser.add_argument(
            "-l",
            "--lags",
            type=int,
            dest="lags",
            help="The lags for the Breusch-Godfrey test",
            default=3,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if not self.regression["OLS"]["model"]:
                console.print(
                    "Please perform an OLS regression before estimating the Breusch-Godfrey statistic."
                )
            else:
                gamestonk_terminal.statistics.regression_view.display_bgod(
                    self.regression["OLS"]["model"], ns_parser.lags, ns_parser.export
                )
