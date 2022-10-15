"""Reports Controller Module."""
__docformat__ = "numpy"

from argparse import Namespace
import argparse
from ast import parse
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

    REPORTS: List[str] = [
        notebooks[:-6]
        for notebooks in os.listdir(reports_model.REPORTS_FOLDER)
        if notebooks.endswith(".ipynb")
    ]
    PARAMETERS_DICT: Dict[str, Any] = {}

    CHOICES_COMMANDS: List[str] = REPORTS
    PATH = "/reports/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""

        super().__init__(queue)
        self.update_choices()

        # Create a call_ method for each report
        for report in self.REPORTS:
            setattr(
                self,
                "call_" + report,
                ReportController.make_func(obj=self, report_name=report),
            )

    @classmethod
    def make_func(cls, obj, report_name):
        def func(other_args):
            obj.run_report(report_name, other_args)

        return func

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
        mt.add_info("_Notebooks_")
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
# fazer um try catch a volta do execute report
# amanha arranjar os reports que nao funcionam e tentar fazer um installer
