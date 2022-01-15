"""Custom Data Controller Module"""
__docformat__ = "numpy"

import argparse
import logging
from typing import List
from pathlib import Path

import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.rich_config import console
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    EXPORT_ONLY_FIGURES_ALLOWED,
)
from gamestonk_terminal.custom import custom_model, custom_view

logger = logging.getLogger(__name__)
# pylint:disable=import-outside-toplevel


class CustomDataController(BaseController):
    """Alternative Controller class"""

    CHOICES_COMMANDS: List[str] = ["load", "plot", "head"]

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__("/custom/", queue)
        self.data = pd.DataFrame()
        self.file = ""
        self.DATA_FILES = [file.name for file in Path("custom_imports").iterdir()]

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["load"] = {c: None for c in self.DATA_FILES}

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        has_data_start = "" if not self.data.empty else "[unvl]"
        has_data_end = "" if not self.data.empty else "[/unvl]"
        help_text = f"""[cmds]
    load            load in custom data set[/cmds]

Current file:    {self.file or None}[cmds]{has_data_start}
    head            show first rows of loaded file
    plot            plot data from loaded file{has_data_end}[/cmds]
            """
        console.print(text=help_text, menu="Custom")

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
            self.file = ns_parser.file

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
            "-v",
            "--vs",
            help="Variable along x axis",
            dest="xvar",
            type=str,
            choices=list(self.data.columns),
            default="",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-y")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            custom_view.custom_plot(
                self.data, ns_parser.yvar, ns_parser.xvar, export=ns_parser.export
            )
        console.print("")

    def call_head(self, other_args: List[str]):
        """Process head command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="head",
            description="Plot first 5 rows of loaded dataframe",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            console.print(self.data.head())
