"""Reports Controller Module."""
__docformat__ = "numpy"

import argparse
import logging
import os

# pylint: disable=R1732, R0912
from typing import Any, Dict, List

import openbb_terminal.config_terminal as cfg
from openbb_terminal import feature_flags as obbff
from openbb_terminal.core.config.paths import (
    USER_CUSTOM_REPORTS_DIRECTORY,
)
from openbb_terminal.reports import reports_model
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText

# from openbb_terminal.terminal_helper import is_packaged_application

logger = logging.getLogger(__name__)


class ReportController(BaseController):
    """Report Controller class."""

    CHOICES_COMMANDS: List[str] = [
        "crypto",
        "economy",
        "equity",
        "etf",
        "forecast",
        "forex",
        "portfolio",
        "run",
        "load",
    ]
    PATH = "/reports/"

    REPORTS: List[str] = reports_model.get_reports_available()
    REPORTS = sorted(list(set(CHOICES_COMMANDS).intersection(REPORTS)))
    PARAMETERS_DICT: Dict[str, Any] = {}

    def __init__(self, queue: List[str] = None):
        """Constructor"""

        super().__init__(queue)
        self.update_choices()

    def update_choices(self):
        """Update controller choices with reports available under templates folder."""

        for report_name in self.REPORTS:
            # Extract report parameters do display on menu
            self.PARAMETERS_DICT[report_name] = reports_model.extract_parameters(
                str(reports_model.REPORTS_FOLDER / report_name)
            )

        if session and obbff.USE_PROMPT_TOOLKIT:

            self.choices: dict = {c: {} for c in self.controller_choices}
            self.choices["run"] = {
                "--file": {c: None for c in reports_model.USER_REPORTS},
                "-f": "--file",
                "--parameters": {},
                "-p": "--parameters",
            }
            for report_name in self.REPORTS:

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
        self.REPORTS = sorted(
            list(set(self.CHOICES_COMMANDS).intersection(self.REPORTS))
        )
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
        console.print(text=mt.menu_text, menu="Reports - WORK IN PROGRESS")

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
        # if is_packaged_application():
        #     console.print("This report is disabled for the installed version")
        #     return

        try:
            import darts  # pyright: reportMissingImports=false # noqa: F401, E501 # pylint: disable=C0415, W0611
            from darts import (  # pyright: reportMissingImports=false, pylint: disable=C0415, W0611
                utils,  # noqa: F401, E501
            )

            FORECASTING_TOOLKIT_ENABLED = True
        except ImportError:
            FORECASTING_TOOLKIT_ENABLED = False
            console.print(
                "[yellow]"
                "Forecasting Toolkit is disabled. "
                "To use the Forecasting features please install the toolkit following the "
                "instructions here: https://docs.openbb.co/sdk/quickstart/installation/"
                "\n"
                "[/yellow]"
            )
        if FORECASTING_TOOLKIT_ENABLED:
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

                choices = reports_model.get_arg_choices(report_name, arg_name)

                getattr(parser, "add_argument")(
                    "--" + arg_name,
                    type=str,
                    default=arg_default,
                    choices=choices,
                    dest=arg_name,
                    help=arg_name,
                )

            if (
                other_args
                and "-" not in other_args[0][0]
                and len(self.PARAMETERS_DICT[report_name]) == 1
            ):
                other_args.insert(
                    0, "--" + list(self.PARAMETERS_DICT[report_name].keys())[0]
                )
            ns_parser = self.parse_simple_args(parser, other_args)

            if ns_parser:
                cfg.LOGGING_SUPPRESS = True
                parameters = vars(ns_parser)
                parameters.pop("help")
                reports_model.render_report(
                    input_path=str(reports_model.REPORTS_FOLDER / report_name),
                    args_dict=parameters,
                )
                cfg.LOGGING_SUPPRESS = False

        else:
            console.print("[red]Notebook not found![/red]\n")

    @log_start_end(log=logger)
    def call_run(self, other_args: List[str]):
        """Process run command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="run",
            description=f"Run a notebook from this folder: '{str(USER_CUSTOM_REPORTS_DIRECTORY)}'.",
        )
        parser.add_argument(
            "-f",
            "--file",
            dest="file",
            choices=reports_model.USER_REPORTS,
            required="-h" not in other_args,
            help="The file to be loaded",
        )
        parser.add_argument(
            "-p",
            "--parameters",
            nargs="+",
            dest="parameters",
            help="Report parameters with format 'name:value'.",
        )

        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            # Validate parameter inputs
            parameters_dict = {}
            if ns_parser.parameters:
                for p in ns_parser.parameters:
                    if ":" in p:
                        item = p.split(":")
                        if item[1]:
                            parameters_dict[item[0]] = item[1]
                        else:
                            console.print(
                                f"[red]Bad format '{p}': empty value.[/red]\nExecuting with defaults.\n"
                            )
                    else:
                        console.print(
                            f"[red]Bad format '{p}': use format 'name:value'.[/red]\nExecuting with defaults.\n"
                        )

            if ns_parser.file:
                complete_file_path = str(USER_CUSTOM_REPORTS_DIRECTORY / ns_parser.file)
                if os.path.exists(complete_file_path):
                    reports_model.render_report(
                        input_path=complete_file_path, args_dict=parameters_dict
                    )
                else:
                    console.print(
                        f"[red]Notebook '{ns_parser.file}' not found![/red]\n"
                    )
