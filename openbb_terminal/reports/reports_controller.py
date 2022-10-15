"""Reports Controller Module."""
__docformat__ = "numpy"

from argparse import Namespace
import argparse
from email.policy import default
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

    CHOICES_COMMANDS = ["run"]
    PATH = "/reports/"
    REPORTS: List[str] = []
    PARAMETERS_DICT: Dict[str, Any] = {}

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
            for report_name in self.REPORTS:

                self.PARAMETERS_DICT[report_name] = reports_model.extract_parameters(
                    report_name
                )

            for report_name, arg_names in self.PARAMETERS_DICT.items():
                self.choices["run"]["-" + report_name] = {}
                for arg in arg_names:
                    self.choices["run"]["-" + report_name]["--" + arg] = None

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
        mt.add_info("_Available_notebooks_")
        MAX_LEN_NAME = max(len(name) for name in self.REPORTS) + 2
        templates_string = ""
        for report_name in self.REPORTS:

            parameters_names = list(self.PARAMETERS_DICT[report_name].keys())

            if len(parameters_names) > 1 or not parameters_names:
                args = f"<{'> <'.join(parameters_names)}>"
            else:
                args = f"<{parameters_names[0]}>"

            templates_string += (
                f"    [cmds]>[/cmds] {report_name}"
                + f"{(MAX_LEN_NAME-len(report_name))*' '} "
                + f"[param]{args if args != '<>' else ''}[/param]\n"
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

        # Assign report name as argument
        report_name = other_args[0]
        if report_name.startswith("-"):
            report_name = report_name[1:]

        if report_name in self.PARAMETERS_DICT:
            getattr(parser, "add_argument")(
                other_args[0],
                action="store_true",
                help=report_name,
            )

            # Assign respective parameters as arguments
            for arg_name, arg_default in self.PARAMETERS_DICT[report_name].items():
                getattr(parser, "add_argument")(
                    "--" + arg_name,
                    type=str,
                    default=arg_default,
                    dest=arg_name,
                    help=arg_name,
                )

            ns_parser = self.parse_known_args_and_warn(parser, other_args)

            if ns_parser:
                # change this params to send a dicvtionary instead of a list so
                # that user can change order of params
                params = [
                    item for item in other_args if not item.startswith(("-", "--"))
                ]
                reports_model.produce_report(report_name, params)

        else:
            console.print("[red]Notebook not found![/red]\n")


# seria bom poder abrir notebook ja existentes no exports atraves do terminal
# o notebook de crypto esta a falhar no report
# posso criar prompt de parametros permitidos para os nossos notebooks
# etf simbolos de etf
# portfolio os portfolios disponiveis etc
# o prompt de sugestoes nao esta a funcionar com mais que um parametro
