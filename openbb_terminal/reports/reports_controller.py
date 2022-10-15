"""Reports Controller Module."""
__docformat__ = "numpy"

import argparse
from dataclasses import replace
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

        # Create a call_ method for each report and assign a run report function to it.
        # This allows to run notebooks as commands with proper input validation,
        # avoiding unforeseen crashes.
        #
        # The benefits on the user side are that it is now possible to use 'help' flag
        # and run with default arguments or any other useful property of our controller.
        #
        # Example:
        # class ReportController:
        #     ...
        #   def call_etf(self, other_args: List[str]):
        #       self.run_report(
        #           report_name = "forex",
        #           other_args = ["--symbol", "EURUSD"]
        #       )

        for report in self.REPORTS:
            setattr(
                self,
                "call_" + report,
                ReportController.make_func(obj=self, report_name=report),
            )

    @classmethod
    def make_func(cls, obj, report_name: str):
        """Dynamic function builder."""

        def func(other_args):
            obj.run_report(report_name, other_args)

        return func

    def update_choices(self):
        """Update controller choices with reports available under templates folder."""

        if session and obbff.USE_PROMPT_TOOLKIT:

            self.REPORTS = reports_model.get_reports_available()

            self.choices: dict = {c: {} for c in self.controller_choices}
            self.choices["run"] = {
                "--file": {},
                "-f": "--file",
            }
            for report_name in self.REPORTS:

                self.PARAMETERS_DICT[report_name] = reports_model.extract_parameters(
                    reports_model.REPORTS_FOLDER / report_name
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
                    reports_model.REPORTS_FOLDER / report_name, params
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
            if os.path.exists(ns_parser.file):
                params = vars(ns_parser)
                params.pop("help")
                reports_model.render_report(ns_parser.file, params)


# amanha arranjar os reports que nao funcionam e tentar fazer um installer
# testar custom reports do user, pelo menos o nome do ficheiro tenho de subsitiuir os espaços por "_"?
