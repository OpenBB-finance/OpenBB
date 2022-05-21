"""Econometrics Controller Module"""
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

import openbb_terminal.econometrics.regression_model
import openbb_terminal.econometrics.regression_view
from openbb_terminal import feature_flags as obbff
from openbb_terminal.helper_funcs import (
    parse_known_args_and_warn,
    NO_EXPORT,
    EXPORT_ONLY_FIGURES_ALLOWED,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    export_data,
)
from openbb_terminal.helper_funcs import (
    print_rich_table,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console
from openbb_terminal.econometrics import econometrics_model, econometrics_view

logger = logging.getLogger(__name__)


class EconometricsController(BaseController):
    """Econometrics class"""

    CHOICES_COMMANDS: List[str] = [
        "load",
        "export",
        "remove",
        "options",
        "plot",
        "show",
        "type",
        "desc",
        "index",
        "clean",
        "modify",
        "ols",
        "norm",
        "root",
        "panel",
        "compare",
        "dwat",
        "bgod",
        "bpag",
        "granger",
        "coint",
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
    PATH = "/econometrics/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)
        self.files: List[str] = list()
        self.datasets: Dict[str, pd.DataFrame] = dict()
        self.regression: Dict[Any[Dict, Any], Any] = dict()

        self.DATA_EXAMPLES: Dict[str, str] = {
            "anes96": "American National Election Survey 1996",
            "cancer": "Breast Cancer Data",
            "ccard": "Bill Greene’s credit scoring data.",
            "cancer_china": "Smoking and lung cancer in eight cities in China.",
            "co2": "Mauna Loa Weekly Atmospheric CO2 Data",
            "committee": "First 100 days of the US House of Representatives 1995",
            "copper": "World Copper Market 1951-1975 Dataset",
            "cpunish": "US Capital Punishment dataset.",
            "danish_data": "Danish Money Demand Data",
            "elnino": "El Nino - Sea Surface Temperatures",
            "engel": "Engel (1857) food expenditure data",
            "fair": "Affairs dataset",
            "fertility": "World Bank Fertility Data",
            "grunfeld": "Grunfeld (1950) Investment Data",
            "heart": "Transplant Survival Data",
            "interest_inflation": "(West) German interest and inflation rate 1972-1998",
            "longley": "Longley dataset",
            "macrodata": "United States Macroeconomic data",
            "modechoice": "Travel Mode Choice",
            "nile": "Nile River flows at Ashwan 1871-1970",
            "randhie": "RAND Health Insurance Experiment Data",
            "scotland": "Taxation Powers Vote for the Scottish Parliament 1997",
            "spector": "Spector and Mazzeo (1980) - Program Effectiveness Data",
            "stackloss": "Stack loss data",
            "star98": "Star98 Educational Dataset",
            "statecrim": "Statewide Crime Data 2009",
            "strikes": "U.S. Strike Duration Data",
            "sunspots": "Yearly sunspots data 1700-2008",
            "wage_panel": "Veila and M. Verbeek (1998): Whose Wages Do Unions Raise?",
        }

        self.DATES = {
            "Y": "%Y",
            "m": "%m",
            "d": "%d",
            "m-d": "%m-%d",
            "Y-m": "%Y-%m",
            "Y-d": "%Y-%d",
            "Y-m-d": "%Y-%m-%d",
            "Y-d-m": "%Y-%d-%m",
            "default": None,
        }

        self.DATA_TYPES: List[str] = ["int", "float", "str", "bool", "date", "category"]

        for regression in [
            "OLS",
            "POLS",
            "BOLS",
            "RE",
            "FE",
            "FE_EE",
            "FE_IE",
            "FE_EE_IE",
            "FDOLS",
        ]:
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
            for filepath in chain(
                Path("exports").rglob(f"*.{file_type}"),
                Path("custom_imports").rglob(f"*.{file_type}"),
            )
            if filepath.is_file()
        }

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["load"] = {c: None for c in self.DATA_FILES.keys()}
            choices["show"] = {c: None for c in self.files}

            for feature in ["export", "options", "show", "desc", "clear", "index"]:
                choices[feature] = {c: None for c in self.files}

            for feature in [
                "general",
                "type",
                "plot",
                "norm",
                "root",
                "granger",
                "cointegration",
                "regressions",
            ]:
                choices[feature] = dict()

            self.choices = choices

            choices["support"] = self.SUPPORT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def update_runtime_choices(self):
        if session and obbff.USE_PROMPT_TOOLKIT:
            dataset_columns = {
                f"{column}-{dataset}": {column: None, dataset: None}
                for dataset, dataframe in self.datasets.items()
                for column in dataframe.columns
            }

            for feature in [
                "general",
                "type",
                "plot",
                "norm",
                "root",
                "granger",
                "cointegration",
                "regressions",
            ]:
                self.choices[feature] = dataset_columns
            for feature in ["export", "options", "show", "desc", "clear", "index"]:
                self.choices[feature] = {c: None for c in self.files}

            self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help"""
        help_text = f"""[cmds]
    load             load in custom data sets
    export           export a dataset
    remove           remove a dataset
    options          show available column-dataset options[/cmds]

[param]Loaded files:[/param] {", ".join(self.files) or None}[cmds]

[info]Exploration[/info]
    show             show a portion of a loaded dataset
    plot             plot data from a dataset
    type             change types of the columns or display their types
    desc             show descriptive statistics of a dataset
    index            set (multi) index based on columns
    clean            clean a dataset by filling or dropping NaNs
    modify           combine columns of datasets and delete or rename columns

[info]Timeseries[/info]
    ols              fit a (multi) linear regression model
    norm             perform normality tests on a column of a dataset
    root             perform unitroot tests (ADF & KPSS) on a column of a dataset

[info]Panel Data[/info]
    panel            estimate model based on various regression techniques
    compare          compare results of all estimated models

[info]Tests[/info]
    dwat             Durbin-Watson autocorrelation test on the residuals of the regression
    bgod             Breusch-Godfrey autocorrelation tests with lags on the residuals of the regression
    bpag             Breusch-Pagan heteroscedasticity test on the residuals of the regression
    granger          Granger causality tests on two columns
    coint            co-integration test on a multitude of columns[/cmds]
        """
        console.print(text=help_text, menu="Econometrics")

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

        parser.add_argument(
            "-ex",
            "--examples",
            help="Use this argument to show examples of Statsmodels to load in. "
            "See: https://www.statsmodels.org/devel/datasets/index.html",
            action="store_true",
            default=False,
            dest="examples",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = parse_known_args_and_warn(parser, other_args, NO_EXPORT)

        if ns_parser:
            if ns_parser.examples:
                df = pd.DataFrame.from_dict(self.DATA_EXAMPLES, orient="index")
                print_rich_table(
                    df,
                    headers=list(["description"]),
                    show_index=True,
                    index_name="file name",
                    title="Examples from Statsmodels",
                )
            elif ns_parser.file and len(ns_parser.file) == 1:
                console.print(
                    f"Please provide an alias to the dataset (format: <file> <alias>). For example: "
                    f"'load {ns_parser.file[0] if len(ns_parser.file) > 0 else 'TSLA.xlsx'} dataset'"
                )
            elif ns_parser.file:
                file, alias = ns_parser.file

                data = econometrics_model.load(
                    file, self.file_types, self.DATA_FILES, self.DATA_EXAMPLES
                )

                if not data.empty:
                    data.columns = data.columns.map(
                        lambda x: x.lower().replace(" ", "_")
                    )

                    self.files.append(alias)
                    self.datasets[alias] = data

                    self.update_runtime_choices()

                    console.print()

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
            dest="name",
            help="The name of the dataset you wish to export",
            type=str,
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
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=NO_EXPORT
        )

        if ns_parser:
            if not ns_parser.name or ns_parser.name not in self.datasets:
                console.print("Please enter a valid dataset.")
            else:
                export_data(
                    ns_parser.type,
                    os.path.dirname(os.path.abspath(__file__)),
                    ns_parser.name,
                    self.datasets[ns_parser.name],
                )

        console.print()

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
            dest="name",
            type=str,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args, NO_EXPORT)

        if not ns_parser.name:
            console.print("Please enter a valid dataset.")
        else:
            if ns_parser.name in self.datasets:
                del self.datasets[ns_parser.name]
                self.files.remove(ns_parser.name)
            else:
                console.print(f"{ns_parser.name} is not a loaded dataset.")

            self.update_runtime_choices()

        console.print()

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
            default=None,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            econometrics_view.show_options(
                self.datasets, ns_parser.name, ns_parser.export
            )

        console.print()

    def call_plot(self, other_args: List[str]):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="Plot data based on the index",
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

            econometrics_view.get_plot(
                data,
                dataset,
                column,
                ns_parser.export,
            )

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

                console.print()

    def call_desc(self, other_args: List[str]):
        """Process desc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="desc",
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser and ns_parser.name:
            if ns_parser.name in self.datasets and self.datasets[ns_parser.name].empty:
                console.print(f"[red]No data available for {ns_parser.name}.[/red]\n")
            else:
                df = self.datasets[ns_parser.name].describe()
                print_rich_table(
                    df, headers=list(df.columns), show_index=True, title=ns_parser.name
                )

                export_data(
                    ns_parser.export,
                    os.path.dirname(os.path.abspath(__file__)),
                    f"{ns_parser.name}_desc",
                    df,
                )

        console.print()

    def call_type(self, other_args: List[str]):
        """Process type"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="type",
            description="Show the type of the columns of the dataset and/or change the type of the column",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            nargs=2,
            dest="name",
            help="The first argument is the column and name of the dataset (format: <column-dataset>). The second "
            f"argument is the preferred type. This can be: {', '.join(self.DATA_TYPES)}",
        )

        parser.add_argument(
            "-d",
            "--dateformat",
            type=str,
            choices=self.DATES.keys(),
            dest="dateformat",
            default="default",
            help="Set the format of the date. This can be: 'Y', 'M', 'D', 'm-d', 'Y-m', 'Y-d',"
            "'Y-m-d', 'Y-d-m'",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args, NO_EXPORT)

        if ns_parser:
            if ns_parser.name:
                column, dataset = ns_parser.name[0].split("-")
                data_type = ns_parser.name[1]

                if data_type not in self.DATA_TYPES:
                    console.print(
                        f"{data_type} is not an option. Please choose between: {', '.join(self.DATA_TYPES)}"
                    )
                else:
                    if data_type == "date":
                        self.datasets[dataset][column] = pd.to_datetime(
                            self.datasets[dataset][column],
                            format=self.DATES[ns_parser.dateformat],
                        )
                    else:
                        self.datasets[dataset][column] = self.datasets[dataset][
                            column
                        ].astype(data_type)
            else:
                for dataset_name, data in self.datasets.items():
                    print_rich_table(
                        pd.DataFrame(data.dtypes),
                        headers=list(["dtype"]),
                        show_index=True,
                        index_name="column",
                        title=str(dataset_name),
                    )

            console.print()

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
            "-a",
            "--adjustment",
            help="Whether to allow for making adjustments to the dataset to align it with the use case for "
            "Timeseries and Panel Data regressions",
            dest="adjustment",
            action="store_true",
            default=False,
        )

        parser.add_argument(
            "-d",
            "--drop",
            help="Whether to drop the column(s) the index is set for.",
            dest="drop",
            action="store_true",
            default=False,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args, NO_EXPORT)

        if ns_parser and ns_parser.name:
            name = ns_parser.name[0]
            columns = ns_parser.name[1:]

            dataset = self.datasets[name]

            if not pd.Index(np.arange(0, len(dataset))).equals(dataset.index):
                console.print("As an index has been set, resetting the current index.")
                if dataset.index.name in dataset.columns:
                    dataset = dataset.reset_index(drop=True)
                else:
                    dataset = dataset.reset_index(drop=False)

            for column in columns:
                if column not in dataset.columns:
                    return console.print(
                        f"The column '{column}' is not available in the dataset {name}."
                        f"Please choose one of the following: {', '.join(dataset.columns)}"
                    )

            if ns_parser.adjustment:
                if len(columns) > 1 and dataset[columns[0]].isnull().any():
                    null_values = dataset[dataset[columns[0]].isnull()]
                    console.print(
                        f"The column '{columns[0]}' contains {len(null_values)} NaN values. As multiple columns are "
                        f"provided, it is assumed this column represents entities (i), the NaN values are "
                        f"forward filled. Remove the -a argument to disable this."
                    )
                    dataset[columns[0]] = dataset[columns[0]].fillna(method="ffill")
                if dataset[columns[-1]].isnull().any():
                    # This checks whether NaT (missing values) exists within the DataFrame
                    null_values = dataset[dataset[columns[-1]].isnull()]
                    console.print(
                        f"The time index '{columns[-1]}' contains {len(null_values)} "
                        f"NaTs which are removed from the dataset. Remove the -a argument to disable this."
                    )
                dataset = dataset[dataset[columns[-1]].notnull()]

            self.datasets[name] = dataset.set_index(columns, drop=ns_parser.drop)

            self.update_runtime_choices()

        return console.print()

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

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args, NO_EXPORT, limit=5)

        if ns_parser:
            if not ns_parser.name or ns_parser.name not in self.datasets:
                console.print("Please enter a valid dataset.")
            else:
                self.datasets[ns_parser.name] = econometrics_model.clean(
                    self.datasets[ns_parser.name],
                    ns_parser.fill,
                    ns_parser.drop,
                    ns_parser.limit,
                )

            console.print()

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

        ns_parser = parse_known_args_and_warn(parser, other_args, NO_EXPORT)

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

        console.print()

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
                console.print(
                    "Please provide both dependent and independent variables."
                )
            else:
                (
                    self.regression["OLS"]["data"],
                    self.regression["OLS"]["dependent"],
                    self.regression["OLS"]["independent"],
                    self.regression["OLS"]["model"],
                ) = openbb_terminal.econometrics.regression_model.get_ols(
                    ns_parser.regression,
                    self.datasets,
                    self.choices["regressions"],
                    export=ns_parser.export,
                )

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

        parser.add_argument(
            "-p",
            "--plot",
            dest="plot",
            help="Whether you wish to plot a histogram to visually depict normality",
            action="store_true",
            default=False,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser and ns_parser.column:
            column, dataset = self.choices["norm"][ns_parser.column].keys()

            if isinstance(self.datasets[dataset][column].index, pd.MultiIndex):
                return console.print(
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

            return econometrics_view.display_norm(
                data, dataset, column, ns_parser.plot, ns_parser.export
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

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
                else:
                    return console.print(
                        "Can not select data due to the data not being a DataFrame or Series."
                    )

                econometrics_view.display_root(
                    data,
                    dataset,
                    column,
                    ns_parser.fuller_reg,
                    ns_parser.kpss_reg,
                    ns_parser.export,
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
            choices=[
                "pols",
                "re",
                "bols",
                "fe",
                "fdols",
                "POLS",
                "RE",
                "BOLS",
                "FE",
                "FDOLS",
            ],
            dest="type",
            help="The type of regression you wish to perform. This can be either pols (Pooled OLS), "
            "re (Random Effects), bols (Between OLS), fe (Fixed Effects) or fdols (First Difference OLS)",
            default="pols",
        )

        parser.add_argument(
            "-ee",
            "--entity_effects",
            dest="entity_effects",
            help="Using this command creates entity effects, which is equivalent to including dummies for each entity. "
            "This is only used within Fixed Effects estimations (when type is set to 'fe')",
            action="store_true",
            default=False,
        )

        parser.add_argument(
            "-te",
            "--time_effects",
            dest="time_effects",
            help="Using this command creates time effects, which is equivalent to including dummies for each time. "
            "This is only used within Fixed Effects estimations (when type is set to 'fe')",
            action="store_true",
            default=False,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-r")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser and ns_parser.regression:
            if len(ns_parser.regression) < 2:
                return console.print(
                    "Please provide both dependent and independent variables."
                )
            for variable in ns_parser.regression:
                column, dataset = self.choices["regressions"][variable].keys()
                if not isinstance(self.datasets[dataset][column].index, pd.MultiIndex):
                    return console.print(
                        f"The column {column} from the dataset {dataset} is not a MultiIndex. Make sure you set "
                        f"the index correctly with the index command where the first level is the entity "
                        f"(e.g. Tesla Inc.) and the second level the date (e.g. 2021-03-31)"
                    )

            # Ensure that OLS is always ran to be able to perform tests
            regression_types = ["OLS", ns_parser.type.upper()]

            for regression in regression_types:
                regression_name = regression
                if regression == "FE":
                    if ns_parser.entity_effects:
                        regression_name = regression_name + "_EE"
                    if ns_parser.time_effects:
                        regression_name = regression_name + "_IE"

                (
                    self.regression[regression_name]["data"],
                    self.regression[regression_name]["dependent"],
                    self.regression[regression_name]["independent"],
                    self.regression[regression_name]["model"],
                ) = openbb_terminal.econometrics.regression_view.display_panel(
                    regression,
                    ns_parser.regression,
                    self.datasets,
                    self.choices["regressions"],
                    ns_parser.entity_effects,
                    ns_parser.time_effects,
                )

    def call_compare(self, other_args: List[str]):
        """Process compare command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="compare",
            description="Compare results between all activated Panel regression models",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            openbb_terminal.econometrics.regression_model.get_comparison(
                self.regression, ns_parser.export
            )

    def call_dwat(self, other_args: List[str]):
        """Process unitroot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dwat",
            description="Show autocorrelation tests from Durbin-Watson",
        )

        parser.add_argument(
            "-p",
            "--plot",
            help="Plot the residuals",
            dest="plot",
            action="store_true",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if not self.regression["OLS"]["model"]:
                console.print(
                    "Please perform an OLS regression before estimating the Durbin-Watson statistic."
                )
            else:
                dependent_variable = self.regression["OLS"]["data"][
                    self.regression["OLS"]["dependent"]
                ]

                openbb_terminal.econometrics.regression_view.display_dwat(
                    dependent_variable,
                    self.regression["OLS"]["model"].resid,
                    ns_parser.plot,
                    ns_parser.export,
                )

                console.print()

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

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if not self.regression["OLS"]["model"]:
                console.print(
                    "Please perform an OLS regression before estimating the Breusch-Godfrey statistic."
                )
            else:
                openbb_terminal.econometrics.regression_view.display_bgod(
                    self.regression["OLS"]["model"], ns_parser.lags, ns_parser.export
                )

        console.print()

    def call_bpag(self, other_args):
        """Process bpag command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="bpag",
            description="Show Breusch-Pagan heteroscedasticity test results.",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if not self.regression["OLS"]["model"]:
                console.print(
                    "Please perform an OLS regression before estimating the Breusch-Pagan statistic."
                )
            else:
                openbb_terminal.econometrics.regression_view.display_bpag(
                    self.regression["OLS"]["model"], ns_parser.export
                )

        console.print()

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

                econometrics_view.display_granger(
                    self.datasets[dataset_y][column_y],
                    self.datasets[dataset_x][column_x],
                    ns_parser.lags,
                    ns_parser.confidence,
                    ns_parser.export,
                )
            else:
                console.print(
                    "Please provide two time series for this function, "
                    "for example: granger adj_close-aapl adj_close-tsla"
                )

        console.print()

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

            econometrics_view.display_cointegration_test(
                datasets, ns_parser.significant, ns_parser.plot, ns_parser.export
            )

        console.print()
