"""Reports Controller Module."""
__docformat__ = "numpy"

from argparse import Namespace
import argparse
import logging

# pylint: disable=R1732, R0912
import os
from typing import Any, Dict, List

from openbb_terminal import feature_flags as obbff
from openbb_terminal.helper_funcs import parse_simple_args
from openbb_terminal.reports import reports_model
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText

logger = logging.getLogger(__name__)


class ReportController(BaseController):
    """Report Controller class."""

    CURRENT_LOCATION = reports_model.CURRENT_LOCATION
    OUTPUT_FOLDER = reports_model.OUTPUT_FOLDER
    CHOICES_COMMANDS = ["run"]
    PATH = "/reports/"

    REPORTS: List[str] = []

    def __init__(self, queue: List[str] = None):
        """Constructor"""

        super().__init__(queue)
        self.update_choices()

    def update_choices(self):
        """Update controller choices with reports available under templates folder."""

        if session and obbff.USE_PROMPT_TOOLKIT:

            self.REPORTS = [
                notebooks[:-6]
                for notebooks in os.listdir(reports_model.REPORTS_FOLDER)
                if notebooks.endswith(".ipynb")
            ]

            self.choices: dict = {c: {} for c in self.controller_choices}
            self.choices["run"] = {
                "--report": {c: None for c in self.REPORTS},
                "-r": "--report",
            }
            self.choices["support"] = self.SUPPORT_CHOICES
            self.choices["about"] = self.ABOUT_CHOICES

        self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help."""

        self.update_choices()

        mt = MenuText("reports/")
        mt.add_info("_reports_")
        mt.add_raw("\n")
        mt.add_cmd("run")
        mt.add_raw("\n")
        mt.add_info("_Available_reports_")
        MAX_LEN_NAME = max(len(name) for name in self.REPORTS) + 2
        templates_string = ""
        for report_name in self.REPORTS:

            parameters_names, _ = reports_model.extract_parameters(report_name)

            if len(parameters_names) > 1 or not parameters_names:
                args = f"<{'> <'.join(parameters_names)}>"
            else:
                args = f"<{parameters_names[0]}>"

            templates_string += (
                f"    [cmds]>[/cmds] {report_name}"
                + f"{(MAX_LEN_NAME-len(report_name))*' '} "
                + f"{args if args != '<>' else ''}\n"
            )
        mt.add_raw(f"{templates_string}")
        mt.add_raw("\n")

        console.print(text=mt.menu_text, menu="Reports")

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
            if "--report" in other_args:
                other_args.remove("--report")

            other_args.remove(ns_parser.report)

            reports_model.produce_report(ns_parser.report, other_args)
