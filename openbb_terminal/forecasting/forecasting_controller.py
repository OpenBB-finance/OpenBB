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
    forecasting_controller,
    forecasting_model,
    forecasting_view,
)
from openbb_terminal.forecasting import expo_model, expo_view

logger = logging.getLogger(__name__)

# pylint: disable=R0902


class ForecastingController(BaseController):
    """Forecasting class"""

    CHOICES_COMMANDS: List[str] = [
        "load",
        "export",
        "remove",
        "plot",
        "show",
        "type",
        "desc",
        "index",
        "clean",
        "add",
        "delete",
        "combine",
        "rename",
        "expo",
    ]
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

        # self.DATA_EXAMPLES: Dict[str, str] = {
        #     "anes96": "American National Election Survey 1996",
        #     "cancer": "Breast Cancer Data",
        #     "ccard": "Bill Greene’s credit scoring data.",
        #     "cancer_china": "Smoking and lung cancer in eight cities in China.",
        #     "co2": "Mauna Loa Weekly Atmospheric CO2 Data",
        #     "committee": "First 100 days of the US House of Representatives 1995",
        #     "copper": "World Copper Market 1951-1975 Dataset",
        #     "cpunish": "US Capital Punishment dataset.",
        #     "danish_data": "Danish Money Demand Data",
        #     "elnino": "El Nino - Sea Surface Temperatures",
        #     "engel": "Engel (1857) food expenditure data",
        #     "fair": "Affairs dataset",
        #     "fertility": "World Bank Fertility Data",
        #     "grunfeld": "Grunfeld (1950) Investment Data",
        #     "heart": "Transplant Survival Data",
        #     "interest_inflation": "(West) German interest and inflation rate 1972-1998",
        #     "longley": "Longley dataset",
        #     "macrodata": "United States Macroeconomic data",
        #     "modechoice": "Travel Mode Choice",
        #     "nile": "Nile River flows at Ashwan 1871-1970",
        #     "randhie": "RAND Health Insurance Experiment Data",
        #     "scotland": "Taxation Powers Vote for the Scottish Parliament 1997",
        #     "spector": "Spector and Mazzeo (1980) - Program Effectiveness Data",
        #     "stackloss": "Stack loss data",
        #     "star98": "Star98 Educational Dataset",
        #     "statecrim": "Statewide Crime Data 2009",
        #     "strikes": "U.S. Strike Duration Data",
        #     "sunspots": "Yearly sunspots data 1700-2008",
        #     "wage_panel": "Veila and M. Verbeek (1998): Whose Wages Do Unions Raise?",
        # }

        self.DATA_TYPES: List[str] = ["int", "float", "str", "bool", "category", "date"]

        # for regression in [
        #     "OLS",
        #     "POLS",
        #     "BOLS",
        #     "RE",
        #     "FE",
        #     "FE_EE",
        #     "FE_IE",
        #     "FE_EE_IE",
        #     "FDOLS",
        # ]:
        #     self.regression[regression] = {
        #         "data": {},
        #         "independent": {},
        #         "dependent": {},
        #         "model": {},
        #     }

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

            for feature in ["export", "show", "desc", "clear", "index"]:
                choices[feature] = {c: None for c in self.files}

            # TODO what is this?
            for feature in [
                "general",
                "type",
                "plot",
                "norm",
                "root",
                "granger",
                "coint",
                "regressions",
            ]:
                choices[feature] = dict()

            self.choices = choices

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
                "general",
                "plot",
                "norm",
                "root",
                "coint",
                "regressions",
                "ols",
                "panel",
                "delete",
            ]:
                self.choices[feature] = dataset_columns
            for feature in [
                "export",
                "show",
                "clean",
                "index",
                "remove",
                "combine",
                "rename",
            ]:
                self.choices[feature] = {c: None for c in self.files}

            self.choices["type"] = {
                c: None for c in self.files + list(dataset_columns.keys())
            }
            self.choices["desc"] = {
                c: None for c in self.files + list(dataset_columns.keys())
            }

            pairs_timeseries = list()
            for dataset_col in list(dataset_columns.keys()):
                pairs_timeseries += [
                    f"{dataset_col},{dataset_col2}"
                    for dataset_col2 in list(dataset_columns.keys())
                    if dataset_col != dataset_col2
                ]

            self.choices["granger"] = {c: None for c in pairs_timeseries}

            self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("econometrics/")
        mt.add_param(
            "_data_loc",
            f"\n\t{obbff.EXPORT_FOLDER_PATH}\n\t{Path('custom_imports').resolve()}",
        )
        mt.add_raw("\n")
        mt.add_cmd("load")
        mt.add_cmd("remove", "", self.files)
        mt.add_raw("\n")
        mt.add_param("_loaded", self.loaded_dataset_cols)

        mt.add_info("_exploration_")
        mt.add_cmd("show", "", self.files)
        mt.add_cmd("plot", "", self.files)
        mt.add_cmd("type", "", self.files)
        mt.add_cmd("desc", "", self.files)
        mt.add_cmd("index", "", self.files)
        mt.add_cmd("clean", "", self.files)
        mt.add_cmd("add", "", self.files)
        mt.add_cmd("delete", "", self.files)
        mt.add_cmd("combine", "", self.files)
        mt.add_cmd("rename", "", self.files)
        mt.add_cmd("export", "", self.files)
        mt.add_info("_timeseries_forecasting_")
        mt.add_cmd("expo", "", self.files)

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

        # parser.add_argument(
        #     "-e",
        #     "--examples",
        #     help="Use this argument to show examples of Statsmodels to load in. "
        #     "See: https://www.statsmodels.org/devel/datasets/index.html",
        #     action="store_true",
        #     default=False,
        #     dest="examples",
        # )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            # show examples from statsmodels
            # if ns_parser.examples:
            #     df = pd.DataFrame.from_dict(self.DATA_EXAMPLES, orient="index")
            #     print_rich_table(
            #         df,
            #         headers=list(["description"]),
            #         show_index=True,
            #         index_name="file name",
            #         title="Examples from Statsmodels",
            #     )
            #     return

            if ns_parser.file:
                # possible_data = list(self.DATA_EXAMPLES.keys()) + list(
                #     self.DATA_FILES.keys()
                # )
                # if ns_parser.file not in possible_data:
                #     file = ""
                #     # Try to see if the user is just missing the extension
                #     for file_ext in list(self.DATA_FILES.keys()):
                #         if file_ext.startswith(ns_parser.file):
                #             # found the correct file
                #             file = file_ext
                #             break

                #     if not file:
                #         console.print(
                #             "[red]The file/dataset selected does not exist.[/red]\n"
                #         )
                #         return
                # else:
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

    @log_start_end(log=logger)
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
            choices=list(self.datasets.keys()),
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args, NO_EXPORT)

        if not ns_parser.name:
            console.print("Please enter a valid dataset.\n")
            return

        if ns_parser.name not in self.datasets:
            console.print(f"[red]'{ns_parser.name}' is not a loaded dataset.[/red]\n")
            return

        del self.datasets[ns_parser.name]
        self.files.remove(ns_parser.name)

        self.update_runtime_choices()

        # Process new datasets to be updated
        self.list_dataset_cols = list()
        maxfile = max(len(file) for file in self.files)
        self.loaded_dataset_cols = "\n"
        for dataset, data in self.datasets.items():
            self.loaded_dataset_cols += f"\t{dataset} {(maxfile - len(dataset)) * ' '}: {', '.join(data.columns)}\n"

            for col in data.columns:
                self.list_dataset_cols.append(f"{dataset}.{col}")

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )

        if ns_parser and ns_parser.values:
            data: Dict = {}
            for datasetcol in ns_parser.values:
                dataset, col = datasetcol.split(".")
                data[datasetcol] = self.datasets[dataset][col]
            # TODO - Display plot with multiple different simulatenous series
            forecasting_view.display_plot(
                data,
                ns_parser.export,
            )

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
            choices=self.choices["desc"],
            dest="name",
            help="The name of the dataset.column you want to show the descriptive statistics",
            required="-h" not in other_args,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if "." in ns_parser.name:
                dataset, col = ns_parser.name.split(".")

                df = self.datasets[dataset][col].describe()
                print_rich_table(
                    df.to_frame(),
                    headers=[col],
                    show_index=True,
                    title=f"Statistics for dataset: '{dataset}'",
                )

                export_data(
                    ns_parser.export,
                    os.path.dirname(os.path.abspath(__file__)),
                    f"{dataset}_{col}_desc",
                    df,
                )
            else:
                df = self.datasets[ns_parser.name].describe()
                print_rich_table(
                    df,
                    headers=self.datasets[ns_parser.name].columns,
                    show_index=True,
                    title=f"Statistics for dataset: '{ns_parser.name}'",
                )

                export_data(
                    ns_parser.export,
                    os.path.dirname(os.path.abspath(__file__)),
                    f"{ns_parser.name}_desc",
                    df,
                )

    @log_start_end(log=logger)
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
            dest="name",
            help="Provide dataset.column series to change type or dataset to see types.",
            choices=self.choices["type"],
        )
        parser.add_argument(
            "-f",
            "--format",
            type=str,
            choices=self.DATA_TYPES,
            dest="format",
            help=(
                "Set the format for the dataset.column defined. This can be: "
                "date, int, float, str, bool or category"
            ),
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args, NO_EXPORT)

        if ns_parser:
            if ns_parser.name:
                if "." in ns_parser.name:
                    dataset, column = ns_parser.name.split(".")
                    if ns_parser.format:
                        if ns_parser.format == "date":
                            self.datasets[dataset][column] = pd.to_datetime(
                                self.datasets[dataset][column].values,
                            )
                        else:
                            self.datasets[dataset][column] = self.datasets[dataset][
                                column
                            ].astype(ns_parser.format)

                        console.print(
                            f"Update '{ns_parser.name}' with type '{ns_parser.format}'"
                        )
                    else:
                        console.print(
                            f"The type of '{ns_parser.name}' is '{self.datasets[dataset][column].dtypes}'"
                        )

                else:
                    print_rich_table(
                        pd.DataFrame(self.datasets[ns_parser.name].dtypes),
                        headers=list(["dtype"]),
                        show_index=True,
                        index_name="column",
                        title=str(ns_parser.name),
                    )
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

    @log_start_end(log=logger)
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
            choices=list(self.datasets.keys()),
            help="Name of dataset to select index from",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-i",
            "--index",
            type=str,
            dest="index",
            help="Columns from the dataset the user wishes to set as default",
            default="",
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

        if ns_parser:
            name = ns_parser.name
            index = ns_parser.index

            if index:
                if "," in index:
                    values_found = [val.strip() for val in index.split(",")]
                else:
                    values_found = [index]

                columns = list()
                for value in values_found:
                    # check if the value is valid
                    if value in self.datasets[name].columns:
                        columns.append(value)
                    else:
                        console.print(f"[red]'{value}' is not valid.[/red]")

                dataset = self.datasets[name]

                if not pd.Index(np.arange(0, len(dataset))).equals(dataset.index):
                    console.print(
                        "As an index has been set, resetting the current index."
                    )
                    if dataset.index.name in dataset.columns:
                        dataset = dataset.reset_index(drop=True)
                    else:
                        dataset = dataset.reset_index(drop=False)

                for column in columns:
                    if column not in dataset.columns:
                        console.print(
                            f"[red]The column '{column}' is not available in the dataset {name}."
                            f"Please choose one of the following: {', '.join(dataset.columns)}[/red]"
                        )
                        return

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
                            "NaNs which are removed from the dataset. Remove the -a argument to disable this."
                        )
                    dataset = dataset[dataset[columns[-1]].notnull()]

                self.datasets[name] = dataset.set_index(columns, drop=ns_parser.drop)
                console.print(
                    f"Successfully updated '{name}' index to be '{', '.join(columns)}'\n"
                )

                self.update_runtime_choices()
            else:
                print_rich_table(
                    self.datasets[name].head(3),
                    headers=list(self.datasets[name].columns),
                    show_index=True,
                    title=f"Dataset '{name}'",
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
            "-n",
            "--name",
            help="The name of the dataset you want to clean up",
            dest="name",
            type=str,
            choices=list(self.datasets.keys()),
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
            self.datasets[ns_parser.name] = forecasting_model.clean(
                self.datasets[ns_parser.name],
                ns_parser.fill,
                ns_parser.drop,
                ns_parser.limit,
            )
            console.print(f"Successfully cleaned '{ns_parser.name}' dataset")
        console.print()

    @log_start_end(log=logger)
    def call_add(self, other_args: List[str]):
        """Process add"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="add",
            description="Add columns to your dataframe with the option to use formulas. E.g."
            "   newdatasetcol = basedatasetcol sign criteriaordatasetcol"
            "   thesis.high_revenue = thesis.revenue > 1000"
            "   dataset.debt_ratio = dataset.debt div dataset2.assets",
        )
        parser.add_argument(
            "-n",
            "--newdatasetcol",
            help="New dataset column to be added with format: dataset.column",
            dest="newdatasetcol",
            type=str,
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-b",
            "--basedatasetcol",
            help="Base dataset column to be used as base with format: dataset.column",
            dest="basedatasetcol",
            type=str,
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-s",
            "--sign",
            help="Sign to be applied to the base dataset column",
            dest="sign",
            choices=list(self.signs.keys()) + [">", "<", ">=", "<=", "=="],
            required="-h" not in other_args,
            type=str,
        )
        parser.add_argument(
            "-c",
            "--criteriaordatasetcol",
            help="Either dataset column to be applied on top of base dataset or criteria",
            dest="criteriaordatasetcol",
            required="-h" not in other_args,
            type=str,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args, NO_EXPORT)

        if ns_parser:
            dataset, new_column = ns_parser.newdatasetcol.split(".")
            dataset2, existing_column = ns_parser.basedatasetcol.split(".")

            for sign, operator in self.signs.items():
                if sign == ns_parser.sign:
                    ns_parser.sign = operator

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
            elif len(ns_parser.criteriaordatasetcol.split(".")) > 1:
                dataset3, existing_column2 = ns_parser.criteriaordatasetcol.split(".")

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
                        f"{ns_parser.sign} self.datasets[dataset3][existing_column2]",
                        target=self.datasets[dataset],
                        inplace=True,
                    )
            else:
                pd.eval(
                    f"{new_column} = self.datasets[dataset2][existing_column] "
                    f"{ns_parser.sign} {ns_parser.criteriaordatasetcol}",
                    target=self.datasets[dataset],
                    inplace=True,
                )

            self.update_runtime_choices()
        console.print()

    @log_start_end(log=logger)
    def call_delete(self, other_args: List[str]):
        """Process add"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="delete",
            description="The column you want to delete from a dataset.",
        )
        parser.add_argument(
            "-d",
            "--delete",
            help="The columns you want to delete from a dataset. Use format: <dataset.column> or"
            " multiple with <dataset.column>,<datasetb.column2>",
            dest="delete",
            type=check_list_values(self.choices["delete"]),
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-d")
        ns_parser = parse_known_args_and_warn(parser, other_args, NO_EXPORT)

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
            "-d",
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
            other_args.insert(0, "-d")
        ns_parser = parse_known_args_and_warn(parser, other_args, NO_EXPORT)

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
        ns_parser = parse_known_args_and_warn(parser, other_args, NO_EXPORT)

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

    # EXPO Models
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
            "-n",
            "--n_days",
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
            "-f",
            "--forecasthorizon",
            action="store",
            dest="forecast_horizon",
            default=3,
            help="Days/Points to forecast when training and performing historical back-testing",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        print(self.datasets)
        # print(self.files)
        # TODO Convert this to multi series
        if ns_parser:
            expo_view.display_expo_forecast(
                data=self.datasets,
                ticker_name=self.files,
                n_predict=ns_parser.n_days,
                trend=ns_parser.trend,
                seasonal=ns_parser.seasonal,
                seasonal_periods=ns_parser.seasonal_periods,
                dampen=ns_parser.dampen,
                start_window=ns_parser.start_window,
                forecast_horizon=ns_parser.forecast_horizon,
                export=ns_parser.export,
            )
