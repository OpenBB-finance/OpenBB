"""Econometrics Controller Module"""
__docformat__ = "numpy"

# pylint: disable=too-many-arguments,too-many-lines,too-many-branches,inconsistent-return-statements,R0904

import argparse
import logging
import os
from itertools import chain
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from openbb_terminal.common import common_model
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.econometrics import (
    econometrics_helpers,
    econometrics_model,
    econometrics_view,
    regression_model,
    regression_view,
)
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_FIGURES_ALLOWED,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    NO_EXPORT,
    check_list_values,
    check_positive,
    check_positive_float,
    export_data,
    print_rich_table,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)

# pylint: disable=R0902,C0302


class EconometricsController(BaseController):
    """Econometrics class"""

    CHOICES_COMMANDS: List[str] = [
        "load",
        "export",
        "remove",
        "plot",
        "show",
        "type",
        "desc",
        "corr",
        "index",
        "clean",
        "add",
        "eval",
        "delete",
        "combine",
        "rename",
        "lag",
        "ret",
        "ols",
        "norm",
        "root",
        "panel",
        "compare",
        "dwat",
        "bgod",
        "bpag",
        "garch",
        "granger",
        "coint",
        "vif",
    ]
    CHOICES_MENUS: List[str] = [
        "qa",
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

    PANEL_CHOICES = [
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
    ]
    PATH = "/econometrics/"

    loaded_dataset_cols = "\n"
    list_dataset_cols: List = list()

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)
        self.files: List[str] = list()
        self.datasets: Dict[str, pd.DataFrame] = dict()
        self.regression: Dict[Any[Dict, Any], Any] = dict()

        self.DATA_TYPES: List[str] = ["int", "float", "str", "bool", "category", "date"]

        current_user = get_current_user()

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
        self.DATA_FILES = {
            filepath.name: filepath
            for file_type in common_model.file_types
            for filepath in chain(
                Path(current_user.preferences.USER_EXPORTS_DIRECTORY).rglob(
                    f"*.{file_type}"
                ),
                Path(
                    current_user.preferences.USER_CUSTOM_IMPORTS_DIRECTORY
                    / "econometrics"
                ).rglob(f"*.{file_type}"),
            )
            if filepath.is_file()
        }

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            choices["load"] = {
                "--file": {c: {} for c in self.DATA_FILES},
                "-f": "--file",
                "-alias": None,
                "-a": "-alias",
                "--examples": None,
                "-e": "--examples",
                "--sheet-name": None,
            }

            for feature in ["export", "show", "desc", "clear", "index"]:
                choices[feature] = {c: {} for c in self.files}

            for feature in [
                "type",
                "plot",
                "norm",
                "root",
                "garch",
                "granger",
                "coint",
                "corr",
                "lag",
                "vif",
                "panel",
            ]:
                choices[feature] = dict()

            # Initialize this for regressions to be able to use -h flag
            choices["regressions"] = {}
            self.choices = choices

            choices["support"] = self.SUPPORT_CHOICES
            choices["about"] = self.ABOUT_CHOICES
            choices["panel"]["-r"] = {c: {} for c in self.PANEL_CHOICES}
            self.completer = NestedCompleter.from_nested_dict(choices)
        else:
            self.choices = {}

    def update_runtime_choices(self):
        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            dataset_columns = {
                f"{dataset}.{column}": {}
                for dataset, dataframe in self.datasets.items()
                for column in dataframe.columns
            }

            for feature in [
                "plot",
                "norm",
                "root",
                "coint",
                "lag",
                "regressions",
                "ols",
                "panel",
                "delete",
                "garch",
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
                "corr",
            ]:
                self.choices[feature] = {c: {} for c in self.files}

            for feature in ["type", "desc", "vif"]:
                self.choices[feature] = {
                    c: {} for c in self.files + list(dataset_columns.keys())
                }
            self.choices["vif"] = dict(
                self.choices["vif"],
                **{"-d": self.choices["vif"], "--data": self.choices["vif"]},
            )

            pairs_timeseries = list()
            for dataset_col in list(dataset_columns.keys()):
                pairs_timeseries += [
                    f"{dataset_col},{dataset_col2}"
                    for dataset_col2 in list(dataset_columns.keys())
                    if dataset_col != dataset_col2
                ]

            self.choices["granger"] = {c: {} for c in pairs_timeseries}

            self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help"""
        current_user = get_current_user()
        mt = MenuText("econometrics/")
        mt.add_param(
            "_data_loc",
            f"\n\t{str(current_user.preferences.USER_EXPORTS_DIRECTORY)}\n"
            f"\t{str(current_user.preferences.USER_CUSTOM_IMPORTS_DIRECTORY/'econometrics')}",
        )
        mt.add_raw("\n")
        mt.add_cmd("load")
        mt.add_cmd("remove", self.files)
        mt.add_raw("\n")
        mt.add_param("_loaded", self.loaded_dataset_cols)

        mt.add_info("_exploration_")
        mt.add_cmd("show", self.files)
        mt.add_cmd("plot", self.files)
        mt.add_cmd("type", self.files)
        mt.add_cmd("desc", self.files)
        mt.add_cmd("corr", self.files)
        mt.add_cmd("index", self.files)
        mt.add_cmd("clean", self.files)
        mt.add_cmd("add", self.files)
        mt.add_cmd("eval", self.files)
        mt.add_cmd("delete", self.files)
        mt.add_cmd("combine", self.files)
        mt.add_cmd("rename", self.files)
        mt.add_cmd("lag", self.files)
        mt.add_cmd("ret", self.files)
        mt.add_cmd("export", self.files)
        mt.add_info("_assumption_testing_")
        mt.add_cmd("norm", self.files)
        mt.add_cmd("granger", self.files)
        mt.add_cmd("root", self.files)
        mt.add_cmd("coint", self.files)
        mt.add_cmd("vif", self.files)
        mt.add_cmd("dwat", self.files and self.regression["OLS"]["model"])
        mt.add_cmd("bgod", self.files and self.regression["OLS"]["model"])
        mt.add_cmd("bpag", self.files and self.regression["OLS"]["model"])
        mt.add_info("_time_series_")
        mt.add_cmd("ols", self.files)
        mt.add_cmd("garch", self.files)
        mt.add_info("_panel_")
        mt.add_cmd("panel", self.files)
        mt.add_cmd("compare", self.files)

        console.print(text=mt.menu_text, menu="Econometrics")
        console.print()

    def custom_reset(self):
        """Class specific component of reset command"""
        return ["econometrics"]

    def update_loaded(self):
        self.list_dataset_cols = []
        self.loaded_dataset_cols = "\n"

        if not self.files:
            self.list_dataset_cols.append("")
            return

        maxfile = max(len(file) for file in self.files)

        for dataset, data in self.datasets.items():
            dataset_columns = ", ".join(data.columns)
            dataset_name = f"{dataset} {(maxfile - len(dataset)) * ' '}:"
            self.loaded_dataset_cols += f"\t{dataset_name} {dataset_columns}\n"
            self.list_dataset_cols.extend([f"{dataset}.{col}" for col in data.columns])

    @log_start_end(log=logger)
    def call_load(self, other_args: List[str]):
        """Process load"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load dataset (from previous export, custom imports or StatsModels).",
        )
        parser.add_argument(
            "-f",
            "--file",
            help="File to load data in (can be custom import, "
            "may have been exported before or can be from Statsmodels)",
            type=str,
        )
        parser.add_argument(
            "-a",
            "--alias",
            help="Alias name to give to the dataset",
            type=str,
        )

        parser.add_argument(
            "-e",
            "--examples",
            help="Use this argument to show examples of Statsmodels to load in. "
            "See: https://www.statsmodels.org/devel/datasets/index.html",
            action="store_true",
            default=False,
            dest="examples",
        )
        parser.add_argument(
            "--sheet-name",
            dest="sheet_name",
            default=None,
            nargs="+",
            help="Name of excel sheet to save data to. Only valid for .xlsx files.",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")

        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            # show examples from statsmodels
            if ns_parser.examples:
                df = pd.DataFrame.from_dict(common_model.DATA_EXAMPLES, orient="index")
                print_rich_table(
                    df,
                    headers=list(["description"]),
                    show_index=True,
                    index_name="file name",
                    title="Examples from Statsmodels",
                )
                return

            if not ns_parser.file:
                return
            possible_data = list(common_model.DATA_EXAMPLES.keys()) + list(
                self.DATA_FILES.keys()
            )
            if ns_parser.file not in possible_data:
                file = ""
                # Try to see if the user is just missing the extension
                for file_ext in list(self.DATA_FILES.keys()):
                    if file_ext.startswith(ns_parser.file):
                        # found the correct file
                        file = file_ext
                        break

                if not file:
                    console.print(
                        "[red]The file/dataset selected does not exist.[/red]"
                    )
                    return
            else:
                file = ns_parser.file

            if ns_parser.alias:
                alias = ns_parser.alias
            else:
                alias = (
                    ".".join(ns_parser.file.split(".")[:-1])
                    if "." in ns_parser.file
                    else ns_parser.file
                )

            # check if this dataset has been added already
            if alias in self.files:
                console.print(
                    "[red]The file/dataset selected has already been loaded.[/red]"
                )
                return

            data = common_model.load(
                file,
                data_files=self.DATA_FILES,
                data_examples=common_model.DATA_EXAMPLES,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

            if not data.empty:
                data.columns = data.columns.map(lambda x: x.lower().replace(" ", "_"))
                self.files.append(alias)
                self.datasets[alias] = data
                self.update_runtime_choices()
                self.update_loaded()

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
            choices=common_model.file_types,
            type=str,
            default="xlsx",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = self.parse_known_args_and_warn(
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
        ns_parser = self.parse_known_args_and_warn(parser, other_args, NO_EXPORT)

        if not ns_parser:
            return

        if not ns_parser.name:
            console.print("Please enter a valid dataset.\n")
            return

        if ns_parser.name not in self.datasets:
            console.print(f"[red]'{ns_parser.name}' is not a loaded dataset.[/red]\n")
            return

        del self.datasets[ns_parser.name]
        self.files.remove(ns_parser.name)

        self.update_runtime_choices()

        self.update_loaded()

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

        if ns_parser and ns_parser.values:
            data: Dict = {}
            for datasetcol in ns_parser.values:
                dataset, col = datasetcol.split(".")
                data[datasetcol] = self.datasets[dataset][col]

            econometrics_view.display_plot(
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

        parser.add_argument(
            "-s",
            "--sortby",
            help="Sort based on a column in the DataFrame",
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

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED, limit=10
        )

        if ns_parser:
            dataset_names = (
                list(self.datasets.keys()) if not ns_parser.name else [ns_parser.name]
            )

            for name in dataset_names:
                df = self.datasets[name]

                if name in self.datasets and self.datasets[name].empty:
                    return console.print(
                        f"[red]No data available for {ns_parser.name}.[/red]\n"
                    )
                if ns_parser.sortby:
                    sort_column = ns_parser.sortby
                    if sort_column not in self.datasets[name].columns:
                        console.print(
                            f"[red]{sort_column} not a valid column. Showing without sorting.\n[/red]"
                        )
                    else:
                        df = df.sort_values(by=sort_column, ascending=ns_parser.reverse)

                print_rich_table(
                    df,
                    headers=list(df.columns),
                    show_index=True,
                    title=f"Dataset {name}",
                    export=bool(ns_parser.export),
                    limit=ns_parser.limit,
                )

                export_data(
                    ns_parser.export,
                    os.path.dirname(os.path.abspath(__file__)),
                    f"{ns_parser.name}_show",
                    df.head(ns_parser.limit),
                    ns_parser.sheet_name,
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
            choices=self.choices.get("desc", []),
            dest="name",
            help="The name of the dataset.column you want to show the descriptive statistics",
            required="-h" not in other_args,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = self.parse_known_args_and_warn(
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
                    export=bool(ns_parser.export),
                )

                export_data(
                    ns_parser.export,
                    os.path.dirname(os.path.abspath(__file__)),
                    f"{dataset}_{col}_desc",
                    df,
                    ns_parser.sheet_name,
                )
            else:
                df = self.datasets[ns_parser.name]
                if not df.empty:
                    df = df.describe()
                    print_rich_table(
                        df,
                        headers=self.datasets[ns_parser.name].columns,
                        show_index=True,
                        title=f"Statistics for dataset: '{ns_parser.name}'",
                        export=bool(ns_parser.export),
                    )

                    export_data(
                        ns_parser.export,
                        os.path.dirname(os.path.abspath(__file__)),
                        f"{ns_parser.name}_desc",
                        df,
                        ns_parser.sheet_name,
                    )
                else:
                    console.print("Empty dataset")

    @log_start_end(log=logger)
    def call_corr(self, other_args: List[str]):
        """Process correlation command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="corr",
            description="Plot correlation coefficients.",
        )
        parser.add_argument(
            "-d",
            "--dataset",
            help="The name of the dataset you want to select",
            dest="target_dataset",
            type=str,
            choices=list(self.datasets.keys()),
        )

        # if user does not put in --dataset
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--dataset")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_FIGURES_ALLOWED,
        )

        if ns_parser:
            # check proper file name is provided
            if not ns_parser.target_dataset:
                console.print("[red]Please enter valid dataset.\n[/red]")
                return

            data = self.datasets[ns_parser.target_dataset]

            econometrics_view.display_corr(
                data,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_type(self, other_args: List[str]):
        """Process type command"""
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
            choices=self.choices.get("type", []),
        )
        parser.add_argument(
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
        ns_parser = self.parse_known_args_and_warn(parser, other_args, NO_EXPORT)

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
        """Process index command"""
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
        ns_parser = self.parse_known_args_and_warn(parser, other_args, NO_EXPORT)

        if ns_parser:
            name = ns_parser.name
            index = ns_parser.index

            if index:
                values_found = (
                    [val.strip() for val in index.split(",")]
                    if "," in index
                    else [index]
                )

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
                            f"The column '{columns[0]}' contains {len(null_values)} NaN "
                            "values. As multiple columns are provided, it is assumed this "
                            "column represents entities (i), the NaN values are forward "
                            "filled. Remove the -a argument to disable this."
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
        """Process clean command"""
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, NO_EXPORT, limit=5
        )
        if ns_parser:
            self.datasets[ns_parser.name] = econometrics_model.clean(
                self.datasets[ns_parser.name],
                ns_parser.fill,
                ns_parser.drop,
                ns_parser.limit,
            )
            console.print(f"Successfully cleaned '{ns_parser.name}' dataset")
        console.print()

    @log_start_end(log=logger)
    def call_add(self, other_args: List[str]):
        """Process add command"""
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
        ns_parser = self.parse_known_args_and_warn(parser, other_args, NO_EXPORT)

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
                    f"{ns_parser.sign} {str(ns_parser.criteriaordatasetcol)}",
                    target=self.datasets[dataset],
                    inplace=True,
                )

            self.update_runtime_choices()
            self.update_loaded()
        console.print()

    @log_start_end(log=logger)
    def call_lag(self, other_args: List[str]):
        """Process lag command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lag",
            description="Add lag to a variable by shifting a column.",
        )
        parser.add_argument(
            "-v",
            "--values",
            help="Dataset.column values to add lag to.",
            dest="values",
            choices={
                f"{dataset}.{column}": {column: None, dataset: None}
                for dataset, dataframe in self.datasets.items()
                for column in dataframe.columns
            },
            type=str,
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-l",
            "--lags",
            action="store",
            dest="lags",
            type=check_positive,
            default=5,
            help="How many periods to lag the selected column.",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-f",
            "--fill-value",
            action="store",
            dest="fill_value",
            help="The value used for filling the newly introduced missing values.",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=NO_EXPORT
        )

        if not ns_parser:
            return

        try:
            dataset, col = ns_parser.values.split(".")
            data = self.datasets[dataset]
        except ValueError:
            console.print("[red]Please enter 'dataset'.'column'.[/red]\n")
            return

        data[col + "_with_" + str(ns_parser.lags) + "_lags"] = data[col].shift(
            ns_parser.lags, fill_value=ns_parser.fill_value
        )
        self.datasets[dataset] = data

        self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_ret(self, other_args: List[str]):
        """Process ret command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ret",
            description="Calculate returns for the given column.",
        )
        parser.add_argument(
            "-v",
            "--values",
            help="Dataset.column values to calculate returns.",
            dest="values",
            choices={
                f"{dataset}.{column}": {column: None, dataset: None}
                for dataset, dataframe in self.datasets.items()
                for column in dataframe.columns
            },
            type=str,
            required="-h" not in other_args,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=NO_EXPORT
        )

        if not ns_parser:
            return

        try:
            dataset, col = ns_parser.values.split(".")
            data = self.datasets[dataset]
        except ValueError:
            console.print("[red]Please enter 'dataset'.'column'.[/red]\n")
            return

        data[col + "_returns"] = econometrics_model.get_returns(data[col])
        self.datasets[dataset] = data

        self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_eval(self, other_args):
        """Process eval command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="eval",
            description="""Create custom data column from loaded datasets.  Can be mathematical expressions supported
                by pandas.eval() function.

                Example.  If I have loaded `fred DGS2,DGS5` and I want to create a new column that is the difference
                between these two, I can create a new column by doing `eval spread = DGS2 - DGS5`.
                Notice that the command is case sensitive, i.e., `DGS2` is not the same as `dgs2`.
                """,
        )
        parser.add_argument(
            "-q",
            "--query",
            type=str,
            nargs="+",
            dest="query",
            required="-h" not in other_args,
            help="Query to evaluate on loaded datasets",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-q")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            self.datasets = econometrics_helpers.create_new_entry(
                self.datasets, " ".join(ns_parser.query)
            )
            self.update_runtime_choices()
            self.update_loaded()

    @log_start_end(log=logger)
    def call_delete(self, other_args: List[str]):
        """Process delete command"""
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
            " multiple with <dataset.column>,<dataset.column2>",
            dest="delete",
            type=check_list_values(self.choices.get("delete", [])),
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-d")
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
    def call_combine(self, other_args: List[str]):
        """Process combine command"""
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
            choices=self.choices.get("combine", []),
        )
        parser.add_argument(
            "-c",
            "--columns",
            help="The columns we want to add <dataset.column>,<dataset.column2>",
            dest="columns",
            type=check_list_values(self.choices.get("delete", [])),
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-d")
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
    def call_rename(self, other_args: List[str]):
        """Process rename command"""
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
            choices=self.choices.get("rename", []),
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

    @log_start_end(log=logger)
    def call_ols(self, other_args: List[str]):
        """Process ols command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ols",
            description="Performs an OLS regression on timeseries data.",
        )
        parser.add_argument(
            "-d",
            "--dependent",
            type=str,
            dest="dependent",
            help="The dependent variable on the regression you would like to perform",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-i",
            "--independent",
            type=check_list_values(self.choices.get("regressions", [])),
            dest="independent",
            help=(
                "The independent variables on the regression you would like to perform. "
                "E.g. historical.high,historical.low"
            ),
            required="-h" not in other_args,
        )
        parser.add_argument(
            "--no-output",
            action="store_true",
            default=False,
            help="Hide the output of the regression",
            dest="no_output",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-d")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if "," in ns_parser.dependent:
                console.print(
                    "It appears you have selected multiple variables for the dependent variable. "
                    "Please select one.\nDid you intend to include these variables as independent "
                    f"variables? Use -i {ns_parser.dependent} in this case.\n"
                )
            elif ns_parser.dependent in self.choices.get("regressions", []):
                (
                    regression_df,
                    dependent_variable,
                    independent_variables,
                ) = regression_model.get_regression_data(
                    [ns_parser.dependent] + ns_parser.independent,
                    self.datasets,
                    "OLS",
                )
                self.regression["OLS"]["data"] = regression_df
                self.regression["OLS"]["dependent"] = dependent_variable
                self.regression["OLS"]["independent"] = independent_variables
                model = regression_model.get_ols(
                    regression_df[dependent_variable],
                    regression_df[independent_variables],
                )
                self.regression["OLS"]["model"] = model
                if not ns_parser.no_output:
                    console.print(model.summary())

            else:
                console.print(
                    f"{ns_parser.dependent} not in {','.join(self.choices.get('regressions', []))}\n"
                    f"Please choose a valid dataset and column combination.\n"
                )

    @log_start_end(log=logger)
    def call_norm(self, other_args: List[str]):
        """Process normality command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="norm",
            description="Test whether the used data is normally distributed.",
        )
        parser.add_argument(
            "-v",
            "--value",
            type=str,
            choices=self.choices.get("norm", []),
            dest="column",
            help="The dataset.column you want to test normality for",
            required="-h" not in other_args,
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
            other_args.insert(0, "-v")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser and ns_parser.column:
            dataset, column = ns_parser.column.split(".")

            if isinstance(self.datasets[dataset][column].index, pd.MultiIndex):
                return console.print(
                    f"The column '{column}' in '{dataset}' is a MultiIndex. To test for normality"
                    ", make sure to set a singular time index.\n"
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

            econometrics_view.display_norm(
                data, dataset, column, ns_parser.plot, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_root(self, other_args: List[str]):
        """Process unit root command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="root",
            description="Show unit root tests of a column of a dataset",
        )
        parser.add_argument(
            "-v",
            "--value",
            type=str,
            choices=self.choices.get("root", []),
            dest="column",
            help="The column and name of the database you want test unit root for",
            required="-h" not in other_args,
        )

        parser.add_argument(
            "-r",
            "--fuller_reg",
            help="Type of regression. Can be 'c','ct','ctt','nc'. c - Constant and t - trend order",
            choices=["c", "ct", "ctt", "n"],
            default="c",
            type=str,
            dest="fuller_reg",
        )
        parser.add_argument(
            "-k",
            "--kps_reg",
            help="Type of regression. Can be 'c', 'ct'. c - Constant and t - trend order",
            choices=["c", "ct"],
            type=str,
            dest="kpss_reg",
            default="c",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser and ns_parser.column:
            if "." in ns_parser.column:
                dataset, column = ns_parser.column.split(".")
            else:
                console.print(
                    "[red]Column must be formatted as 'dataset.column'[/red]\n"
                )

            if isinstance(self.datasets[dataset][column].index, pd.MultiIndex):
                console.print(
                    f"The column '{column}' from the dataset '{dataset}' is a MultiIndex. To test for unitroot in a "
                    "timeseries, make sure to set a singular time index.\n"
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

    @log_start_end(log=logger)
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
            "-d",
            "--dependent",
            type=str,
            dest="dependent",
            help="The dependent variable on the regression you would like to perform",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-i",
            "--independent",
            type=check_list_values(self.choices.get("regressions", [])),
            dest="independent",
            help=(
                "The independent variables on the regression you would like to perform. "
                "E.g. wage_panel.married,wage_panel.union"
            ),
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-r",
            "--regression",
            type=str,
            choices=self.PANEL_CHOICES,
            dest="type",
            help="The type of regression you wish to perform. This can be either pols (Pooled OLS), "
            "re (Random Effects), bols (Between OLS), fe (Fixed Effects) or fdols (First Difference OLS)",
            default="pols",
        )
        parser.add_argument(
            "-e",
            "--entity_effects",
            dest="entity_effects",
            help="Using this command creates entity effects, which is equivalent to including dummies for each entity. "
            "This is only used within Fixed Effects estimations (when type is set to 'fe')",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-t",
            "--time_effects",
            dest="time_effects",
            help="Using this command creates time effects, which is equivalent to including dummies for each time. "
            "This is only used within Fixed Effects estimations (when type is set to 'fe')",
            action="store_true",
            default=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-d")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if "," in ns_parser.dependent:
                console.print(
                    "It appears you have selected multiple variables for the dependent variable. "
                    "The model only accepts one.\nDid you intend to include these variables as independent "
                    f"variables? Use -i {ns_parser.dependent} in this case.\n"
                )
            elif ns_parser.dependent in self.choices.get("regressions", []):
                regression_vars = [ns_parser.dependent] + ns_parser.independent

                if regression_vars and len(regression_vars) > 1:
                    for variable in regression_vars:
                        if "." not in variable:
                            console.print(
                                "[red]Please follow the format 'dataset.column'[/red]\n"
                            )
                            continue
                        dataset, column = variable.split(".")
                        if not isinstance(
                            self.datasets[dataset][column].index, pd.MultiIndex
                        ):
                            other_column = (
                                self.datasets[dataset].drop(column, axis=1).columns[0]
                            )
                            return console.print(
                                f"The column '{column}' from the dataset '{dataset}' is not a MultiIndex. Make sure "
                                f"you set the index correctly with the index (e.g. index {dataset} -i {column},"
                                f"{other_column}) command where the first level is the entity (e.g. Tesla Inc.) and "
                                f"the second level the date (e.g. 2021-03-31)\n"
                            )

                    # Ensure that OLS is always ran to be able to perform tests
                    regression_types = [ns_parser.type.upper(), "OLS"]

                    for regression in regression_types:
                        regression_name = regression
                        if regression == "FE":
                            if ns_parser.entity_effects:
                                regression_name = regression_name + "_EE"
                            if ns_parser.time_effects:
                                regression_name = regression_name + "_IE"

                        (
                            regression_df,
                            dependent_variable,
                            independent_variables,
                        ) = regression_model.get_regression_data(
                            [ns_parser.dependent] + ns_parser.independent,
                            self.datasets,
                            regression,
                        )
                        self.regression[regression]["data"] = regression_df
                        self.regression[regression]["dependent"] = dependent_variable
                        self.regression[regression][
                            "independent"
                        ] = independent_variables
                        self.regression[regression_name][
                            "model"
                        ] = regression_view.display_panel(
                            regression_df[dependent_variable],
                            regression_df[independent_variables],
                            regression,
                            ns_parser.entity_effects,
                            ns_parser.time_effects,
                            ns_parser.export,
                        )
            else:
                console.print(
                    f"{ns_parser.dependent} not in {','.join(self.choices['regressions'])}\n"
                    f"Please choose a valid dataset and column combination.\n"
                )

    @log_start_end(log=logger)
    def call_compare(self, other_args: List[str]):
        """Process compare command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="compare",
            description="Compare results between all activated Panel regression models",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            regression_model.get_comparison(
                self.regression,
                ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
            console.print()

    @log_start_end(log=logger)
    def call_dwat(self, other_args: List[str]):
        """Process unitroot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dwat",
            description=(
                "Show autocorrelation tests from Durbin-Watson. "
                "Needs OLS to be run in advance with independent and dependent variables"
            ),
        )
        parser.add_argument(
            "-p",
            "--plot",
            help="Plot the residuals",
            dest="plot",
            action="store_true",
            default=False,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if not self.regression["OLS"]["model"]:
                console.print(
                    "Please perform an OLS regression before estimating the Durbin-Watson statistic.\n"
                )
            else:
                dependent_variable = self.regression["OLS"]["data"][
                    self.regression["OLS"]["dependent"]
                ]
                regression_view.display_dwat(
                    self.regression["OLS"]["model"],
                    dependent_variable,
                    ns_parser.plot,
                    ns_parser.export,
                )

    @log_start_end(log=logger)
    def call_bgod(self, other_args):
        """Process bgod command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="bgod",
            description=(
                "Show Breusch-Godfrey autocorrelation test results. "
                "Needs OLS to be run in advance with independent and dependent variables"
            ),
        )
        parser.add_argument(
            "-l",
            "--lags",
            type=check_positive,
            dest="lags",
            help="The lags for the Breusch-Godfrey test",
            default=3,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if not self.regression["OLS"]["model"]:
                console.print(
                    "Perform an OLS regression before estimating the Breusch-Godfrey statistic.\n"
                )
            else:
                regression_view.display_bgod(
                    self.regression["OLS"]["model"], ns_parser.lags, ns_parser.export
                )

    @log_start_end(log=logger)
    def call_bpag(self, other_args):
        """Process bpag command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="bpag",
            description=(
                "Show Breusch-Pagan heteroscedasticity test results. "
                "Needs OLS to be run in advance with independent and dependent variables"
            ),
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if not self.regression["OLS"]["model"]:
                console.print(
                    "Perform an OLS regression before estimating the Breusch-Pagan statistic.\n"
                )
            else:
                regression_view.display_bpag(
                    self.regression["OLS"]["model"], ns_parser.export
                )

    @log_start_end(log=logger)
    def call_garch(self, other_args: List[str]):
        """Process garch command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="garch",
            description=r"""Calculates annualized volatility forecasts based on GARCH.
            GARCH (Generalized autoregressive conditional heteroskedasticity) is stochastic model for time series,
            which is for instance used to model volatility clusters, stock return and inflation. It is a
            generalisation of the ARCH models.

            $\text{GARCH}(p, q)  = (1 - \alpha - \beta) \sigma_l + \sum_{i=1}^q \alpha u_{t-i}^2 + \sum_{i=1}^p \beta
            \sigma_{t-i}^2$ [1]

            The GARCH-model assumes that the variance estimate consists of 3 components:
            - $\sigma_l$ ; the long term component, which is unrelated to the current market conditions
            - $u_t$ ; the innovation/discovery through current market price changes
            - $\sigma_t$ ; the last estimate

            GARCH can be understood as a model, which allows to optimize these 3 variance components to the time
            series. This is done assigning weights to variance components: $(1 - \alpha - \beta)$ for $\sigma_l$ ,
            $\alpha$ for $u_t$ and $\beta$ for $\sigma_t$ . [2]

            The weights can be estimated by iterating over different values of $(1 - \alpha - \beta) \sigma_l$
            which we will call $\omega$ , $\alpha$ and $\beta$ , while maximizing:
            $\sum_{i} -ln(v_i) - (u_i ^ 2) / v_i$ . With the constraints:
            - $\alpha > 0$
            - $\beta > 0$
            - $\alpha + \beta < 1$
            Note that there is no restriction on $\omega$ .

            Another method used for estimation is "variance targeting", where one first sets $\omega$
            equal to the variance of the time series. This method nearly as effective as the previously mentioned and
            is less computationally effective.

            One can measure the fit of the time series to the GARCH method by using the Ljung-Box statistic. [3]

            See the sources below for reference and for greater detail.

            Sources:
            [1] Generalized Autoregressive Conditional Heteroskedasticity, by Tim Bollerslev
            [2] Finance Compact Plus Band 1, by Yvonne Seler Zimmerman and Heinz Zimmerman; ISBN: 978-3-907291-31-1
            [3] Options, Futures & other Derivates, by John C. Hull; ISBN: 0-13-022444-8""",
        )
        parser.add_argument(
            "-v",
            "--value",
            type=str,
            choices=self.choices.get("garch", []),
            dest="column",
            help="The column and name of the database you want to estimate volatility for",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-p",
            help="The lag order of the symmetric innovation",
            dest="p",
            type=int,
            default=1,
        )
        parser.add_argument(
            "-o",
            help="The lag order of the asymmetric innovation",
            dest="o",
            type=int,
            default=0,
        )
        parser.add_argument(
            "-q",
            help="The lag order of lagged volatility or equivalent",
            dest="q",
            type=int,
            default=1,
        )
        parser.add_argument(
            "-m",
            "--mean",
            help="Choose mean model",
            choices=["LS", "AR", "ARX", "HAR", "HARX", "constant", "zero"],
            default="constant",
            type=str,
            dest="mean",
        )
        parser.add_argument(
            "-l",
            "--length",
            help="The length of the estimate",
            dest="horizon",
            type=int,
            default=100,
        )
        parser.add_argument(
            "-d",
            "--detailed",
            help="Display the details about the parameter fit, for instance the confidence interval",
            dest="detailed",
            action="store_true",
            default=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            dataset, column = ns_parser.column.split(".")
            econometrics_view.display_garch(
                self.datasets[dataset],
                column,
                ns_parser.p,
                ns_parser.o,
                ns_parser.q,
                ns_parser.mean,
                ns_parser.horizon,
                ns_parser.detailed,
            )

    @log_start_end(log=logger)
    def call_granger(self, other_args: List[str]):
        """Process granger command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="granger",
            description="Show Granger causality between two timeseries",
        )
        parser.add_argument(
            "-t",
            "--timeseries",
            choices=self.choices["granger"],
            help="Requires two time series, the first time series is assumed to be Granger-caused "
            "by the second time series.",
            type=str,
            dest="ts",
            metavar="Available time series",
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
            "-c",
            "--confidence",
            help="Set the confidence level",
            type=check_positive_float,
            dest="confidence",
            default=0.05,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser and ns_parser.ts:
            datasetcol_y, datasetcol_x = ns_parser.ts.split(",")

            dataset_y, column_y = datasetcol_y.split(".")
            dataset_x, column_x = datasetcol_x.split(".")

            econometrics_view.display_granger(
                self.datasets[dataset_y][column_y].rename(datasetcol_y),
                self.datasets[dataset_x][column_x].rename(datasetcol_x),
                ns_parser.lags,
                ns_parser.confidence,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_coint(self, other_args: List[str]):
        """Process coint command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="coint",
            description="Show co-integration between two timeseries",
        )
        parser.add_argument(
            "-t",
            "--time_series",
            help="The time series you wish to test co-integration on. E.g. historical.open,historical2.close.",
            dest="ts",
            type=check_list_values(self.choices["coint"]),
            required="-h" not in other_args,
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
            other_args.insert(0, "-t")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser and ns_parser.ts:
            # We are going to pass through a variable number of series, so datasets will be a list of series
            if len(ns_parser.ts) > 1:
                datasets = []
                for series in ns_parser.ts:
                    if "." not in series:
                        console.print(
                            "[red]Invalid time series format. Should be dataset.column, "
                            "e.g. historical.open[/red]\n"
                        )
                    else:
                        dataset, column = series.split(".")
                        datasets.append(self.datasets[dataset][column])

                econometrics_view.display_cointegration_test(
                    *datasets,
                    significant=ns_parser.significant,
                    plot=ns_parser.plot,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

            else:
                console.print(
                    "[red]More than one dataset.column must be provided.\n[/red]"
                )

    @log_start_end(log=logger)
    def call_vif(self, other_args: List[str]):
        """Process vif command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="vif",
            description=r"""Calculates VIF (variance inflation factor), which tests collinearity.

            It quantifies the severity of multicollinearity in an ordinary least squares regression analysis. The square
            root of the variance inflation factor indicates how much larger the standard error increases compared to if
            that variable had 0 correlation to other predictor variables in the model.

            It is defined as:

            $ VIF_i = 1 / (1 - R_i^2) $
            where $ R_i $ is the coefficient of determination of the regression equation with the column i being the
            result from the i:th series being the exogenous variable.

            A VIF over 5 indicates a high collinearity and correlation. Values over 10 indicates causes problems,
            while a value of 1 indicates no correlation. Thus VIF values between 1 and 5 are most commonly considered
            acceptable. In order to improve the results one can often remove a column with high VIF.

            For further information see: https://en.wikipedia.org/wiki/Variance_inflation_factor""",
        )
        parser.add_argument(
            "-d",
            "--data",
            help="The datasets and columns we want to add <dataset>,<dataset2.column>,<dataset2.column2>",
            dest="data",
            type=check_list_values(self.choices["vif"]),
            default=None,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-d")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        data = pd.DataFrame()
        if ns_parser:
            if ns_parser.data is None:
                console.print("[red]Please enter a dataset to calculate vif for.[/red]")
                return
            if len(ns_parser.data) == 1 and "." in ns_parser.data[0]:
                console.print(
                    "[red]Please enter at least a dataset or two columns to calculate vif for."
                    "vif can only be calculated for at least two columns.[/red]"
                )
            for option in ns_parser.data:
                if "." in option:
                    dataset, column = option.split(".")
                else:
                    dataset = option
                    column = None

                if dataset not in self.datasets:
                    console.print(
                        f"[red]Not able to find the dataset {dataset}. Please choose one of "
                        f"the following: {', '.join(self.datasets)}[/red]"
                    )
                elif column is not None:
                    if column not in self.datasets[dataset]:
                        console.print(
                            f"[red]Not able to find the column {column}. Please choose one of "
                            f"the following: {', '.join(self.datasets[dataset].data)}[/red]"
                        )
                    else:
                        data[f"{dataset}_{column}"] = self.datasets[dataset][column]
                else:
                    for column in list(self.datasets[dataset].columns):
                        data[f"{dataset}_{column}"] = self.datasets[dataset][column]

            econometrics_view.display_vif(data)
