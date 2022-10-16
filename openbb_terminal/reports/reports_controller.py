"""Reports Controller Module."""
__docformat__ = "numpy"

import argparse
import logging
import os

# pylint: disable=R1732, R0912
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

    REPORTS: List[str] = reports_model.get_reports_available()
    PARAMETERS_DICT: Dict[str, Any] = {}

    CHOICES_COMMANDS: List[str] = REPORTS + ["run", "load"]
    PATH = "/reports/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""

        super().__init__(queue)
        self.file_types = ["ipynb"]
        self.update_choices()

    def update_choices(self):
        """Update controller choices with reports available under templates folder."""

        if session and obbff.USE_PROMPT_TOOLKIT:

            self.choices: dict = {c: {} for c in self.controller_choices}
            self.choices["run"] = {
                "--file": {},
                "-f": "--file",
            }
            for report_name in self.REPORTS:

                self.PARAMETERS_DICT[report_name] = reports_model.extract_parameters(
                    str(reports_model.REPORTS_FOLDER / report_name)
                )

                # Completer with limited user choices to avoid unforeseen problems
                self.choices[report_name] = {}
                for arg in self.PARAMETERS_DICT[report_name]:
                    if report_name in reports_model.REPORT_CHOICES:
                        self.choices[report_name][
                            "--" + arg
                        ] = reports_model.REPORT_CHOICES[report_name]["--" + arg]

            self.choices["support"] = self.SUPPORT_CHOICES
            self.choices["about"] = self.ABOUT_CHOICES

        self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help."""

        self.REPORTS = reports_model.get_reports_available()
        self.update_choices()

        mt = MenuText("reports/")
        mt.add_info("_reports_")
        mt.add_raw("\n")
        mt.add_info("_OpenBB_reports_")
        MAX_LEN_NAME = max(len(name) for name in self.REPORTS) + 2
        templates_string = ""
        for report_name in self.REPORTS:

            parameters_names = list(self.PARAMETERS_DICT[report_name].keys())

            if len(parameters_names) > 1 or not parameters_names:
                args = f"<{'> <'.join(parameters_names)}>"
            else:
                args = f"<{parameters_names[0]}>"

            templates_string += (
                f"    [cmds]{report_name}[/cmds]"
                + f"{(MAX_LEN_NAME-len(report_name))*' '} "
                + f"[param]{args if args != '<>' else ''}[/param]\n"
            )
        mt.add_raw(f"{templates_string}")
        mt.add_raw("\n")
        mt.add_info("_Custom_reports_")
        mt.add_cmd("run")
        console.print(text=mt.menu_text, menu="Reports")

    @log_start_end(log=logger)
    def call_etf(self, other_args: List[str]):
        self.run_report("etf", other_args)

    @log_start_end(log=logger)
    def call_forex(self, other_args: List[str]):
        self.run_report("forex", other_args)

    @log_start_end(log=logger)
    def call_portfolio(self, other_args: List[str]):
        self.run_report("portfolio", other_args)

    @log_start_end(log=logger)
    def call_economy(self, other_args: List[str]):
        self.run_report("economy", other_args)

    @log_start_end(log=logger)
    def call_equity(self, other_args: List[str]):
        self.run_report("equity", other_args)

    @log_start_end(log=logger)
    def call_crypto(self, other_args: List[str]):
        self.run_report("crypto", other_args)

    @log_start_end(log=logger)
    def call_forecast(self, other_args: List[str]):
        self.run_report("forecast", other_args)

    @log_start_end(log=logger)
    def run_report(self, report_name: str, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog=report_name,
            description=f"Run {report_name} report.",
        )

        if report_name in self.PARAMETERS_DICT:
            # Assign respective parameters as arguments
            for arg_name, arg_default in self.PARAMETERS_DICT[report_name].items():
                getattr(parser, "add_argument")(
                    "--" + arg_name,
                    type=str,
                    default=arg_default,
                    dest=arg_name,
                    help=arg_name,
                )

            ns_parser = parse_simple_args(parser, other_args)

            # The report is rendered here.
            if ns_parser:
                params = vars(ns_parser)
                params.pop("help")
                reports_model.render_report(
                    str(reports_model.REPORTS_FOLDER / report_name), params
                )

        else:
            console.print("[red]Notebook not found![/red]\n")

    @log_start_end(log=logger)
    def call_run(self, other_args: List[str]):
        """Process returns command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="run",
            description="Run a notebook",
        )
        parser.add_argument(
            "-f",
            "--file",
            type=str,
            dest="file",
            required="-h" not in other_args,
            help="The file to be loaded",
        )

        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        # The report is rendered here.
        if ns_parser and ns_parser.file:
            params = vars(ns_parser)
            notebook_file = params.pop("file")
            params.pop("help")
            if os.path.exists(notebook_file):
                reports_model.render_report(notebook_file, params)
