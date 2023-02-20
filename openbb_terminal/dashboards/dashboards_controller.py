"""Dashboards Module"""
__docformat__ = "numpy"

import argparse
import logging
import os
import subprocess  # nosec
from typing import List, Optional

import openbb_terminal.config_terminal as cfg
from openbb_terminal import feature_flags as obbff
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

# pylint: disable=consider-using-with


logger = logging.getLogger(__name__)


class DashboardsController(BaseController):
    """Dashboards Controller class"""

    CHOICES_COMMANDS = [
        "stocks",
        "correlation",
        "vsurf",
        "chains",
        "shortdata",
        "crypto",
        "futures",
        "forecast",
        "forecasting",
    ]
    PATH = "/dashboards/"

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}

            choices["support"] = self.SUPPORT_CHOICES
            choices["about"] = self.ABOUT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("dashboards/")
        mt.add_raw("\nVoila Apps:\n")
        mt.add_cmd("stocks")
        mt.add_cmd("correlation")
        mt.add_cmd("vsurf")
        mt.add_cmd("chains")
        mt.add_cmd("shortdata")
        mt.add_cmd("crypto")
        mt.add_cmd("futures")
        mt.add_cmd("forecast")
        mt.add_raw("\nStreamlit Apps:\n")
        mt.add_cmd("forecasting")
        console.print(text=mt.menu_text, menu="Dashboards")

    @log_start_end(log=logger)
    def call_stocks(self, other_args: List[str]):
        """Process stocks command"""
        self.create_call_voila(other_args, "stocks", "stocks")

    @log_start_end(log=logger)
    def call_correlation(self, other_args: List[str]):
        """Process correlation command"""
        self.create_call_voila(other_args, "correlation", "correlation")

    @log_start_end(log=logger)
    def call_vsurf(self, other_args: List[str]):
        """Process vsurf command"""
        self.create_call_voila(other_args, "vsurf", "")

    @log_start_end(log=logger)
    def call_chains(self, other_args: List[str]):
        """Process chains command"""
        self.create_call_voila(other_args, "chains", "")

    @log_start_end(log=logger)
    def call_shortdata(self, other_args: List[str]):
        """Process shortdata command"""
        self.create_call_voila(other_args, "shortdata", "")

    @log_start_end(log=logger)
    def call_crypto(self, other_args: List[str]):
        """Process crypto command"""
        self.create_call_voila(other_args, "crypto", "")

    @log_start_end(log=logger)
    def call_futures(self, other_args: List[str]):
        """Process futures command"""
        self.create_call_voila(other_args, "futures", "")

    @log_start_end(log=logger)
    def call_forecast(self, other_args: List[str]):
        """Process forecast command"""
        self.create_call_voila(other_args, "forecast", "")

    @log_start_end(log=logger)
    def call_forecasting(self, other_args: List[str]):
        """Process forecasting command"""
        self.create_call_streamlit(other_args, "forecast")

    @classmethod
    def create_call_voila(
        cls, other_args: List[str], name: str, filename: Optional[str] = None
    ) -> None:
        filename = filename if filename else name

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog=name,
            description=f"""Shows {name} dashboard""",
        )
        parser.add_argument(
            "-j",
            "--jupyter",
            action="store_true",
            default=False,
            dest="jupyter",
            help="Shows dashboard in jupyter-lab.",
        )
        parser.add_argument(
            "-n",
            "--no-input",
            action="store_true",
            default=False,
            dest="input",
            help="Skips confirmation to run server.",
        )
        parser.add_argument(
            "-d",
            "--dark",
            action="store_true",
            default=False,
            dest="dark",
            help="Whether to show voila in dark mode",
        )
        ns_parser = cls.parse_simple_args(parser, other_args)

        if ns_parser:
            cmd = "jupyter-lab" if ns_parser.jupyter else "voila"
            base_path = os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "voila"
            )
            file = os.path.join(base_path, f"{filename}.ipynb")
            if not ns_parser.input:
                console.print(
                    f"Warning: opens a port on your computer to run a {cmd} server."
                )
                response = input("Would you like us to run the server for you [yn]? ")
            args = ""
            if ns_parser.dark and not ns_parser.jupyter:
                args += "--theme=dark"
            if ns_parser.input or response.lower() == "y":
                cfg.LOGGING_SUPPRESS = True
                subprocess.Popen(
                    f"{cmd} {file} {args}",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,  # nosec
                )
                cfg.LOGGING_SUPPRESS = False
            else:
                console.print(f"Type: {cmd} voila/{file}\ninto a terminal to run.")

    @classmethod
    def create_call_streamlit(
        cls, other_args: List[str], name: str, filename: Optional[str] = None
    ) -> None:
        filename = filename if filename else name

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog=name,
            description=f"""Shows streamlit {name} dashboard""",
        )
        parser.add_argument(
            "-n",
            "--no-input",
            action="store_true",
            default=False,
            dest="input",
            help="Skips confirmation to run server.",
        )
        ns_parser = cls.parse_simple_args(parser, other_args)

        if ns_parser:
            cmd = "streamlit run"
            base_path = os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "stream"
            )
            file = os.path.join(base_path, f"{filename}.py")
            if not ns_parser.input:
                console.print(
                    f"Warning: opens a port on your computer to run a {cmd} server."
                )
                response = input("Would you like us to run the server for you [yn]? ")
            args = ""
            if ns_parser.input or response.lower() == "y":
                subprocess.Popen(
                    f"{cmd} {file} {args}",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                )
            else:
                console.print(f"Type: {cmd} stream/{file}\ninto a terminal to run.")
