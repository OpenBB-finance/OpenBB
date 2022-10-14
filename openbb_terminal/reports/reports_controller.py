"""Reports Controller Module."""
__docformat__ = "numpy"

from argparse import Namespace
import argparse
import logging

# pylint: disable=R1732, R0912
import os
from pathlib import Path
from tkinter import N
import webbrowser
from ast import literal_eval
from datetime import datetime
from typing import Any, Dict, List
import papermill as pm

from openbb_terminal import feature_flags as obbff
from openbb_terminal.helper_funcs import parse_simple_args
from openbb_terminal.reports import reports_model
from openbb_terminal.core.config.paths import USER_EXPORTS_DIRECTORY
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText

logger = logging.getLogger(__name__)


class ReportController(BaseController):
    """Report Controller class."""

    CURRENT_LOCATION = reports_model.CURRENT_LOCATION
    REPORTS_FOLDER = reports_model.REPORTS_FOLDER
    OUTPUT_FOLDER = reports_model.OUTPUT_FOLDER

    report_names = [
        notebooks[:-6]
        for notebooks in os.listdir(REPORTS_FOLDER)
        if notebooks.endswith(".ipynb")
    ]
    reports_dict = {str(v + 1): k for v, k in enumerate(report_names)}
    parameters_dict: Dict[str, Any] = {}

    CHOICES_COMMANDS = ["run"]
    CHOICES_MENUS = list(reports_dict.keys()) + report_names
    PATH = "/reports/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""

        super().__init__(queue)
        if session and obbff.USE_PROMPT_TOOLKIT:
            self.choices: dict = {c: {} for c in self.controller_choices}
            self.choices["support"] = self.SUPPORT_CHOICES
            self.choices["about"] = self.ABOUT_CHOICES
            self.completer = NestedCompleter.from_nested_dict(self.choices)

            # Extract required parameters per report
            for _, report_name in self.reports_dict.items():

                (
                    parameters_names,
                    parameters_values,
                ) = reports_model.extract_parameters(report_name)

                self.parameters_dict[report_name] = [
                    parameters_names,
                    parameters_values,
                ]

    def print_help(self):
        """Print help."""

        mt = MenuText("reports/")
        mt.add_info("_reports_")
        mt.add_cmd("run")

        self.report_names = [
            notebooks[:-6]
            for notebooks in os.listdir(self.REPORTS_FOLDER)
            if notebooks.endswith(".ipynb")
        ]
        self.reports_dict = {str(v + 1): k for v, k in enumerate(self.report_names)}

        MAX_LEN_NAME = max(len(name) for name in self.report_names) + 2
        menu_string = ""
        for k, report_name in self.reports_dict.items():

            (
                parameters_names,
                parameters_values,
            ) = reports_model.extract_parameters(report_name)

            self.parameters_dict[report_name] = [
                parameters_names,
                parameters_values,
            ]

            parameters_names = self.parameters_dict[report_name][0]
            if len(parameters_names) > 1 or not parameters_names:
                args = f"<{'> <'.join(parameters_names)}>"
            else:
                args = f"<{parameters_names[0]}>"

            menu_string += (
                f"    {k}. {report_name}"
                + f"{(MAX_LEN_NAME-len(report_name))*' '} "
                + f"{args if args != '<>' else ''}\n"
            )

        mt.add_raw(f"[cmds]{menu_string}[/cmds]")
        console.print(text=mt.menu_text, menu="Reports - WORK IN PROGRESS")

    @log_start_end(log=logger)
    def call_run(self, other_args: List[str]):
        """Display current keys"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="run",
            description="Run specified report.",
        )
        parser.add_argument(
            "-r", "--report", type=str, dest="report", help="report", default=False
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-r")

        # # atribuir programticamente o argumento
        # getattr(parser, "add_argument")()

        ns_parser = parse_simple_args(parser, other_args)

        if ns_parser:
            if "-r" in other_args:
                other_args.remove("-r")
            if "--reports" in other_args:
                other_args.remove("--report")

            other_args.remove(ns_parser.report)

            reports_model.produce_report(ns_parser.report, other_args)
