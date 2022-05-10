"""Custom Data Controller Module"""
__docformat__ = "numpy"

import argparse
import logging
from pathlib import Path
from typing import List

import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.custom import custom_model, custom_view
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_FIGURES_ALLOWED,
    parse_known_args_and_warn,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)
# pylint:disable=import-outside-toplevel


class CustomDataController(BaseController):
    """Alternative Controller class"""

    CHOICES_COMMANDS: List[str] = ["load", "plot", "show", "info"]
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
    PATH = "/custom/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)
        self.data = pd.DataFrame()
        self.file = ""
        self.DATA_FILES = [file.name for file in Path("custom_imports").iterdir()]

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["load"] = {c: None for c in self.DATA_FILES}
            choices["plot"]["-k"] = {c: None for c in self.pandas_plot_choices}
            self.choices = choices

            choices = {**choices, **self.SUPPORT_CHOICES}

            self.completer = NestedCompleter.from_nested_dict(choices)

    def update_runtime_choices(self):
        if session and obbff.USE_PROMPT_TOOLKIT:
            self.choices["plot"] = {c: None for c in self.data.columns}
            self.choices["plot"]["-y"] = {c: None for c in self.data.columns}
            self.choices["plot"]["-x"] = {c: None for c in self.data.columns}
            self.choices["plot"]["--vs"] = {c: None for c in self.data.columns}
            self.choices["show"]["-s"] = {c: None for c in self.data.columns}

        self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help"""
        has_data_start = "" if not self.data.empty else "[unvl]"
        has_data_end = "" if not self.data.empty else "[/unvl]"
        help_text = f"""[cmds]
    load            load in custom data set[/cmds]

[param]Current file:[/param]    {self.file or None}[cmds]{has_data_start}

    show            show portion of loaded data
    info            show data info (columns and datatypes)
    plot            plot data from loaded file{has_data_end}[/cmds]
[menu]
>   qa              quantitative analysis,   \t e.g.: decompose, cusum, residuals analysis
>   pred            prediction techniques    \t e.g.: regression, arima, rnn, lstm[/menu]
"""
        console.print(text=help_text, menu="Custom")

    @log_start_end(log=logger)
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
            choices=self.DATA_FILES,
            help="File to load in.",
            default="test.csv",
            type=str,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            file = Path("custom_imports") / ns_parser.file
            self.data = custom_model.load(file)
            self.data.columns = self.data.columns.map(lambda x: x.lower())
            for col in self.data.columns:
                if col in ["date", "time", "timestamp"]:  # Could be others?
                    self.data[col] = pd.to_datetime(self.data[col])
                    self.data = self.data.set_index(col)
            self.file = ns_parser.file
            self.update_runtime_choices()
        console.print("")

    @log_start_end(log=logger)
    def call_plot(self, other_args: List[str]):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="Plot 2 columns of loaded data",
        )
        parser.add_argument(
            "-y",
            help="Variable to plot along y",
            dest="yvar",
            type=str,
            choices=list(self.data.columns),
        )
        parser.add_argument(
            "-x",
            "--vs",
            help="Variable along x axis",
            dest="xvar",
            type=str,
            choices=list(self.data.columns),
            default="",
        )
        parser.add_argument(
            "-k",
            "--kind",
            default="line",
            help="Type of plot for data",
            choices=self.pandas_plot_choices,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-y")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            if self.data.empty:
                logger.error("No data loaded")
                console.print("[red]No data loaded.[/red]\n")
                return
            custom_view.custom_plot(
                self.data,
                ns_parser.yvar,
                ns_parser.xvar,
                kind=ns_parser.kind,
                export=ns_parser.export,
            )
        console.print("")

    @log_start_end(log=logger)
    def call_show(self, other_args: List[str]):
        """Process head command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="show",
            description="Show loaded dataframe",
        )
        parser.add_argument(
            "-s", "--sortcol", nargs="+", type=str, dest="sortcol", default=""
        )
        parser.add_argument(
            "-a", "--ascend", action="store_true", default=False, dest="ascend"
        )
        ns_parser = parse_known_args_and_warn(parser, other_args, limit=5)
        if ns_parser:
            if self.data.empty:
                logger.error("No data loaded")
                console.print("[red]No data loaded.[/red]\n")
                return
            if ns_parser.sortcol:
                sort_column = " ".join(ns_parser.sortcol)
                if sort_column not in self.data.columns:
                    logger.warning(
                        "%s is not a valid column. Showing without sorting", sort_column
                    )
                    console.print(
                        f"[red]{sort_column} not a valid column.  Showing without sorting.\n[/red]"
                    )
                else:
                    console.print(
                        self.data.sort_values(
                            by=sort_column, ascending=ns_parser.ascend
                        ).head(ns_parser.limit)
                    )
                    console.print()
                    return

            console.print(self.data.head(ns_parser.limit))
        console.print()

    @log_start_end(log=logger)
    def call_info(self, other_args: List[str]):
        """Process info command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="info",
            description="Show information of custom data.",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.data.empty:
                logger.error("No data loaded.")
                console.print("[red]No data loaded.[/red]\n")
                return
            console.print(self.data.info())
        console.print()

    @log_start_end(log=logger)
    def call_qa(self, _):
        """Process qa command"""
        from openbb_terminal.custom.quantitative_analysis import qa_controller

        self.queue = self.load_class(
            qa_controller.QaController,
            custom_df=self.data,
            file=self.file,
            queue=self.queue,
        )

    @log_start_end(log=logger)
    def call_pred(self, _):
        """Process pred command"""
        if obbff.ENABLE_PREDICT:
            from openbb_terminal.custom.prediction_techniques import pred_controller

            self.queue = self.load_class(
                pred_controller.PredictionTechniquesController,
                self.data,
                self.file,
                self.queue,
            )
